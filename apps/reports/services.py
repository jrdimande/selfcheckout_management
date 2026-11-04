from decimal import Decimal

from django.db.models import Avg, Count, Max, Q, Sum
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek

from apps.core.utils import apply_date_range, sum0
from apps.customers.models import Customer
from apps.payments.models import Payment
from apps.sales.models import Sale, SaleItem

REPORTS = {
    "sales_daily": "Vendas diárias",
    "sales_weekly": "Vendas semanais",
    "sales_monthly": "Vendas mensais",
    "revenue": "Receitas por mês e método de pagamento",
    "top_products": "Produtos mais vendidos",
    "customers": "Clientes",
    "payment_methods": "Métodos de pagamento",
}


def _label(v, fmt):
    return v.strftime(fmt) if hasattr(v, "strftime") else str(v)


def _sales_by(trunc, fmt, d_from, d_to):
    qs = apply_date_range(Sale.objects.all(), "sale_date", d_from, d_to)
    rows = (qs.annotate(p=trunc("sale_date")).values("p")
            .annotate(n=Count("id"), t=sum0("total"), a=Avg("total"), m=Max("total")).order_by("p"))
    return (["Período", "Nº vendas", "Receita", "Ticket médio", "Maior venda"],
            [[_label(r["p"], fmt), r["n"], r["t"], r["a"], r["m"]] for r in rows])


def build(kind, d_from=None, d_to=None):
    if kind == "sales_daily":
        headers, rows = _sales_by(TruncDate, "%Y-%m-%d", d_from, d_to)
    elif kind == "sales_weekly":
        headers, rows = _sales_by(TruncWeek, "Semana de %Y-%m-%d", d_from, d_to)
    elif kind == "sales_monthly":
        headers, rows = _sales_by(TruncMonth, "%Y-%m", d_from, d_to)
    elif kind == "revenue":
        qs = apply_date_range(Payment.objects.all(), "sale__sale_date", d_from, d_to)
        data = (qs.annotate(m=TruncMonth("sale__sale_date")).values("m", "payment_method")
                .annotate(n=Count("id"), t=sum0("amount")).order_by("m", "payment_method"))
        headers = ["Mês", "Método", "Nº pagamentos", "Valor"]
        rows = [[_label(r["m"], "%Y-%m"), r["payment_method"], r["n"], r["t"]] for r in data]
    elif kind == "top_products":
        qs = apply_date_range(SaleItem.objects.all(), "sale__sale_date", d_from, d_to)
        data = (qs.order_by().values("product_id", "product__name")
                .annotate(q=Sum("quantity"), t=sum0("subtotal")).order_by("-q")[:100])
        headers = ["UUID", "Produto", "Unidades vendidas", "Receita"]
        rows = [[r["product_id"], r["product__name"], r["q"], r["t"]] for r in data]
    elif kind == "customers":
        f = Q()
        if d_from:
            f &= Q(sales__sale_date__gte=d_from)
        if d_to:
            from datetime import timedelta
            f &= Q(sales__sale_date__lt=d_to + timedelta(days=1))
        data = (Customer.objects.annotate(n=Count("sales", filter=f), t=sum0("sales__total", filter=f))
                .order_by("-t", "name"))
        headers = ["UUID", "Nome", "Saldo", "Nº compras", "Total gasto"]
        rows = [[c.uuid, c.name, c.balance, c.n, c.t] for c in data]
    elif kind == "payment_methods":
        qs = apply_date_range(Payment.objects.all(), "sale__sale_date", d_from, d_to)
        data = qs.order_by().values("payment_method").annotate(n=Count("id"), t=sum0("amount"), a=Avg("amount")).order_by("-t")
        headers = ["Método", "Nº pagamentos", "Valor total", "Valor médio"]
        rows = [[r["payment_method"], r["n"], r["t"], r["a"]] for r in data]
    else:
        raise ValueError(kind)
    return {"title": REPORTS[kind], "headers": headers, "rows": [[_fmt(c) for c in r] for r in rows]}


def _fmt(v):
    if isinstance(v, Decimal):
        return f"{v:.2f}"
    if isinstance(v, float):
        return f"{v:.2f}"
    return "" if v is None else v
