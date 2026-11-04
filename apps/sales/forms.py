from django import forms

from apps.core.forms import BootstrapMixin, date_field


class SaleFilterForm(BootstrapMixin, forms.Form):
    sale_id = forms.IntegerField(required=False, min_value=1, label="ID da venda")
    customer = forms.CharField(required=False, label="Cliente (nome/UUID)")
    date_from = date_field("De")
    date_to = date_field("Até")
    min_total = forms.DecimalField(required=False, min_value=0, label="Valor mín.")
    max_total = forms.DecimalField(required=False, min_value=0, label="Valor máx.")
