from datetime import date, datetime, time, timedelta

from django.db.models import Count, F, Sum
from django.db.models.functions import TruncDate, TruncMonth

from apps.core.utils import sum0
from apps.customers.models import Customer
from apps.payments.models import Payment
from apps.products.models import Product
from apps.sales.models import Sale, SaleItem


def _months_back(today, n):
    y, m = today.year, today.month - n
    while m <= 0:
        y, m = y - 1, m + 12
    return date(y, m, 1)


def get_statistics():
    """Todos os indicadores vêm de consultas reais à base de dados."""
    today = date.today()
    start_today = datetime.combine(today, time.min)
    totals = Sale.objects.aggregate(n=Count("id"), revenue=sum0("total"))
    day = Sale.objects.filter(sale_date__gte=start_today).aggregate(n=Count("id"), revenue=sum0("total"))

    d0 = today - timedelta(days=29)
    by_day = {r["d"]: r for r in Sale.objects.filter(sale_date__gte=datetime.combine(d0, time.min))
              .annotate(d=TruncDate("sale_date")).values("d").annotate(n=Count("id"), t=sum0("total")).order_by("d")}
    daily = [{"date": (d0 + timedelta(days=i)).isoformat(),
              "sales": by_day.get(d0 + timedelta(days=i), {}).get("n", 0),
              "revenue": by_day.get(d0 + timedelta(days=i), {}).get("t", 0)} for i in range(30)]

    m0 = _months_back(today, 11)
    by_month = {(r["m"].year, r["m"].month): r["t"] for r in Sale.objects.filter(sale_date__gte=datetime.combine(m0, time.min))
                .annotate(m=TruncMonth("sale_date")).values("m").annotate(t=sum0("total")).order_by("m")}
    monthly = []
    for i in range(12):
        m = _months_back(today, 11 - i)
        monthly.append({"month": m.strftime("%Y-%m"), "revenue": by_month.get((m.year, m.month), 0)})

    return {
        "total_customers": Customer.objects.count(),
        "total_products": Product.objects.count(),
        "total_sales": totals["n"],
        "total_revenue": totals["revenue"],
        "sales_today": day["n"],
        "revenue_today": day["revenue"],
        "low_stock_count": Product.objects.filter(stock__lte=F("minimum_stock")).count(),
        "daily_sales": daily,
        "monthly_revenue": monthly,
        "payment_methods": list(Payment.objects.order_by().values("payment_method")
                                .annotate(count=Count("id"), total=sum0("amount")).order_by("-total")),
        "recent_sales": list(Sale.objects.values("id", "sale_date", "total", customer_name=F("customer__name"))[:8]),
        "top_products": list(SaleItem.objects.order_by().values(uuid=F("product_id"), name=F("product__name"))
                             .annotate(quantity=Sum("quantity"), revenue=sum0("subtotal")).order_by("-quantity")[:5]),
        "top_customers": list(Customer.objects.annotate(purchases=Count("sales"), spent=sum0("sales__total"))
                              .filter(purchases__gt=0).order_by("-purchases", "-spent").values("uuid", "name", "purchases", "spent")[:5]),
        "low_stock": list(Product.objects.filter(stock__lte=F("minimum_stock")).order_by("stock").values("uuid", "name", "stock", "minimum_stock")[:8]),
    }
