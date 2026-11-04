from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.views.generic import DetailView

from apps.core.utils import apply_date_range
from apps.core.views import FilteredListView

from .forms import SaleFilterForm
from .models import Sale


class SaleList(FilteredListView):
    title = "Vendas"
    model = Sale
    filter_form_class = SaleFilterForm
    detail_url = "sales:detail"
    columns = [("Venda", "id"), ("Data", "sale_date", "date"), ("Cliente", "customer.name"),
               ("Artigos", "item_count"), ("Pagamento", "payment_methods"), ("Total", "total", "money")]

    def base_queryset(self):
        return (Sale.objects.select_related("customer").prefetch_related("payments")
                .annotate(item_count=Count("items", distinct=True)).order_by("-sale_date", "-id"))

    def apply_filters(self, qs, d):
        if d.get("sale_id"):
            qs = qs.filter(pk=d["sale_id"])
        if d.get("customer"):
            qs = qs.filter(Q(customer__name__icontains=d["customer"]) | Q(customer__uuid__icontains=d["customer"]))
        if d.get("min_total") is not None:
            qs = qs.filter(total__gte=d["min_total"])
        if d.get("max_total") is not None:
            qs = qs.filter(total__lte=d["max_total"])
        return apply_date_range(qs, "sale_date", d.get("date_from"), d.get("date_to"))

    def get_stats(self, qs):
        agg = qs.order_by().aggregate(n=Count("id", distinct=True), total=Sum("total"))
        return [("Vendas (filtro)", agg["n"]), ("Valor total (filtro)", f"{agg['total'] or 0:,.2f}")]


class SaleDetail(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = "sales/detail.html"
    queryset = Sale.objects.select_related("customer")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        payments = list(self.object.payments.all())
        paid = sum((p.amount for p in payments), 0)
        ctx.update(items=self.object.items.select_related("product"), payments=payments, paid=paid,
                   mismatch=paid != self.object.total)
        return ctx
