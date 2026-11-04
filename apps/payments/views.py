from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count
from django.views.generic import DetailView

from apps.core.forms import BootstrapMixin, date_field
from apps.core.utils import apply_date_range, sum0
from apps.core.views import FilteredListView

from .models import Payment


class PaymentFilterForm(BootstrapMixin, forms.Form):
    sale_id = forms.IntegerField(required=False, min_value=1, label="ID da venda")
    method = forms.ChoiceField(required=False, label="Método")
    date_from = date_field("De")
    date_to = date_field("Até")
    min_amount = forms.DecimalField(required=False, min_value=0, label="Valor mín.")
    max_amount = forms.DecimalField(required=False, min_value=0, label="Valor máx.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Os métodos vêm da base de dados, ou seja, são os valores usados pela app Java.
        methods = Payment.objects.order_by().values_list("payment_method", flat=True).distinct()
        self.fields["method"].choices = [("", "Todos")] + [(m, m) for m in sorted(methods)]


class PaymentList(FilteredListView):
    title = "Pagamentos"
    model = Payment
    filter_form_class = PaymentFilterForm
    detail_url = "payments:detail"
    columns = [("ID", "id"), ("Data (venda)", "sale.sale_date", "date"), ("Venda", "sale_id"),
               ("Cliente", "sale.customer.name"), ("Método", "payment_method"), ("Valor", "amount", "money")]

    def base_queryset(self):
        return Payment.objects.select_related("sale", "sale__customer")

    def apply_filters(self, qs, d):
        if d.get("sale_id"):
            qs = qs.filter(sale_id=d["sale_id"])
        if d.get("method"):
            qs = qs.filter(payment_method=d["method"])
        if d.get("min_amount") is not None:
            qs = qs.filter(amount__gte=d["min_amount"])
        if d.get("max_amount") is not None:
            qs = qs.filter(amount__lte=d["max_amount"])
        return apply_date_range(qs, "sale__sale_date", d.get("date_from"), d.get("date_to"))

    def get_stats(self, qs):
        agg = qs.order_by().aggregate(n=Count("id"), total=sum0("amount"), avg=Avg("amount"))
        stats = [("Pagamentos", agg["n"]), ("Total", f"{agg['total']:,.2f}"), ("Média", f"{agg['avg'] or 0:,.2f}")]
        for row in qs.order_by().values("payment_method").annotate(n=Count("id"), t=sum0("amount")).order_by("-t")[:4]:
            stats.append((row["payment_method"], f"{row['t']:,.2f} ({row['n']})"))
        return stats


class PaymentDetail(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = "payments/detail.html"
    queryset = Payment.objects.select_related("sale", "sale__customer")
