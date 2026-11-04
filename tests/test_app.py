from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from apps.audit.models import AuditLog
from apps.customers.models import Customer
from apps.payments.models import Payment
from apps.products.models import Product
from apps.sales.models import Sale, SaleItem

User = get_user_model()


class Base(TestCase):
    databases = {"default", "selfcheckout"}

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user("admin", password="x")
        cls.admin.groups.add(Group.objects.create(name="Administrador"))
        cls.op = User.objects.create_user("op", password="x")
        cls.cust = Customer.objects.create(uuid="c1", name="Ana", balance=Decimal("10.00"))
        Customer.objects.create(uuid="c2", name="Rui")
        cls.prod = Product.objects.create(uuid="p1", name="Leite", price=Decimal("2.50"), stock=3, minimum_stock=5)
        cls.sale = Sale.objects.bulk_create([Sale(customer=cls.cust, sale_date=datetime.now(), total=Decimal("5.00"))])[0]
        cls.sale = Sale.objects.first()
        SaleItem.objects.bulk_create([SaleItem(sale=cls.sale, product=cls.prod, quantity=2, unit_price=Decimal("2.50"), subtotal=Decimal("5.00"))])
        Payment.objects.bulk_create([Payment(sale=cls.sale, amount=Decimal("5.00"), payment_method="CASH")])


class AccessTests(Base):
    def test_login_required(self):
        for name in ("dashboard:index", "customers:list", "products:list", "sales:list", "payments:list"):
            r = self.client.get(reverse(name))
            self.assertEqual(r.status_code, 302, name)

    def test_operator_can_view_not_edit(self):
        self.client.force_login(self.op)
        for name in ("dashboard:index", "customers:list", "products:list", "sales:list", "payments:list"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        self.assertEqual(self.client.get(reverse("customers:create")).status_code, 403)
        self.assertEqual(self.client.get(reverse("reports:index")).status_code, 403)
        self.assertEqual(self.client.get(reverse("audit:list")).status_code, 403)
        self.assertEqual(self.client.post(reverse("customers:delete", args=["c2"])).status_code, 403)

    def test_detail_pages(self):
        self.client.force_login(self.admin)
        for url in (reverse("customers:detail", args=["c1"]), reverse("products:detail", args=["p1"]),
                    reverse("sales:detail", args=[self.sale.pk]), reverse("payments:detail", args=[Payment.objects.first().pk])):
            self.assertEqual(self.client.get(url).status_code, 200, url)


class CrudTests(Base):
    def setUp(self):
        self.client.force_login(self.admin)

    def test_create_update_delete_customer_with_audit(self):
        r = self.client.post(reverse("customers:create"), {"uuid": "c9", "name": "Zé", "balance": "0"})
        self.assertEqual(r.status_code, 302)
        self.client.post(reverse("customers:edit", args=["c9"]), {"name": "José"})
        self.assertEqual(Customer.objects.get(pk="c9").name, "José")
        self.client.post(reverse("customers:delete", args=["c9"]))
        self.assertFalse(Customer.objects.filter(pk="c9").exists())
        self.assertEqual(list(AuditLog.objects.order_by("id").values_list("action", flat=True)), ["create", "update", "delete"])
        upd = AuditLog.objects.get(action="update")
        self.assertEqual(upd.before["name"], "Zé")
        self.assertEqual(upd.after["name"], "José")

    def test_duplicate_uuid_rejected(self):
        r = self.client.post(reverse("customers:create"), {"uuid": "c1", "name": "X", "balance": "0"})
        self.assertEqual(r.status_code, 200)

    def test_cannot_delete_customer_or_product_with_sales(self):
        self.client.post(reverse("customers:delete", args=["c1"]))
        self.client.post(reverse("products:delete", args=["p1"]))
        self.assertTrue(Customer.objects.filter(pk="c1").exists())
        self.assertTrue(Product.objects.filter(pk="p1").exists())

    def test_price_update_and_auto_uuid(self):
        self.client.post(reverse("products:price", args=["p1"]), {"price": "3.10"})
        self.assertEqual(Product.objects.get(pk="p1").price, Decimal("3.10"))
        self.client.post(reverse("products:create"), {"name": "Pão", "price": "1", "stock": "10", "minimum_stock": "2"})
        self.assertEqual(Product.objects.filter(name="Pão").count(), 1)

    def test_sales_are_read_only(self):
        with self.assertRaises(PermissionError):
            self.sale.save()
        with self.assertRaises(PermissionError):
            Payment.objects.first().delete()

    def test_user_management_hides_password_in_audit(self):
        self.client.post(reverse("accounts:user_create"), {"username": "novo", "role": "Operador", "password": "S3nha-Forte-123", "is_active": "on"})
        self.assertTrue(User.objects.filter(username="novo").exists())
        self.assertNotIn("password", AuditLog.objects.get(action="create").after)


class DataTests(Base):
    def setUp(self):
        self.client.force_login(self.admin)

    def test_dashboard_numbers_are_real(self):
        r = self.client.get(reverse("dashboard:index"))
        s = r.context["s"]
        self.assertEqual((s["total_customers"], s["total_products"], s["total_sales"]), (2, 1, 1))
        self.assertEqual(s["total_revenue"], Decimal("5.00"))
        self.assertEqual(s["top_products"][0]["quantity"], 2)
        self.assertEqual(s["payment_methods"][0]["payment_method"], "CASH")
        self.assertEqual(s["low_stock_count"], 1)

    def test_filters(self):
        r = self.client.get(reverse("sales:list"), {"customer": "ana", "min_total": "1"})
        self.assertEqual(len(r.context["page_obj"]), 1)
        r = self.client.get(reverse("sales:list"), {"min_total": "100"})
        self.assertEqual(len(r.context["page_obj"]), 0)
        r = self.client.get(reverse("payments:list"), {"method": "CASH"})
        self.assertEqual(len(r.context["page_obj"]), 1)
        r = self.client.get(reverse("customers:list"), {"q": "rui"})
        self.assertEqual(len(r.context["page_obj"]), 1)

    def test_all_reports_and_exports(self):
        from apps.reports.services import REPORTS
        for kind in REPORTS:
            self.assertEqual(self.client.get(reverse("reports:index"), {"kind": kind}).status_code, 200, kind)
            for fmt, ctype in (("xlsx", "spreadsheetml"), ("pdf", "pdf")):
                r = self.client.get(reverse("reports:index"), {"kind": kind, "export": fmt})
                self.assertEqual(r.status_code, 200, (kind, fmt))
                self.assertIn(ctype, r["Content-Type"])


class ApiTests(Base):
    def test_requires_auth(self):
        self.assertIn(self.client.get("/api/customers/").status_code, (401, 403))

    def test_operator_read_only(self):
        self.client.force_login(self.op)
        self.assertEqual(self.client.get("/api/customers/").status_code, 200)
        self.assertEqual(self.client.post("/api/customers/", {"name": "N"}, content_type="application/json").status_code, 403)

    def test_admin_crud_and_protection(self):
        self.client.force_login(self.admin)
        r = self.client.post("/api/customers/", {"name": "Novo"}, content_type="application/json")
        self.assertEqual(r.status_code, 201, r.content)
        uid = r.json()["uuid"]
        r = self.client.put(f"/api/customers/{uid}/", {"name": "Novo2", "balance": "99"}, content_type="application/json")
        self.assertEqual(r.json()["name"], "Novo2")
        self.assertEqual(Customer.objects.get(pk=uid).balance, Decimal("0.00"))  # saldo protegido
        self.assertEqual(self.client.delete(f"/api/customers/{uid}/").status_code, 204)
        self.assertEqual(self.client.delete("/api/customers/c1/").status_code, 409)
        r = self.client.post("/api/products/", {"name": "P", "price": "-1"}, content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_sales_payments_dashboard(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.post("/api/sales/", {}, content_type="application/json").status_code, 405)
        r = self.client.get(f"/api/sales/{self.sale.pk}/").json()
        self.assertEqual(r["items"][0]["product_name"], "Leite")
        self.assertEqual(r["payments"][0]["payment_method"], "CASH")
        self.assertEqual(self.client.get("/api/payments/").json()["count"], 1)
        self.assertEqual(self.client.get("/api/dashboard/statistics/").json()["total_sales"], 1)
        self.assertEqual(self.client.get("/api/sales/?date_from=xx").status_code, 400)
