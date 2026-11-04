from django import forms
from django.contrib.auth import get_user_model
from django.views.generic import DetailView

from apps.accounts.permissions import AdminRequiredMixin
from apps.core.forms import BootstrapMixin, date_field
from apps.core.utils import apply_date_range
from apps.core.views import FilteredListView

from .models import AuditLog


class AuditFilterForm(BootstrapMixin, forms.Form):
    user = forms.CharField(required=False, label="Utilizador")
    action = forms.ChoiceField(required=False, label="Operação", choices=[("", "Todas")] + AuditLog.ACTIONS)
    model = forms.CharField(required=False, label="Registo (ex.: customers.Customer)")
    date_from = date_field("De")
    date_to = date_field("Até")


class AuditList(AdminRequiredMixin, FilteredListView):
    title = "Auditoria"
    model = AuditLog
    filter_form_class = AuditFilterForm
    detail_url = "audit:detail"
    columns = [("Data", "created_at", "date"), ("Utilizador", "username"), ("Operação", "get_action_display"),
               ("Registo", "model"), ("Objecto", "object_repr")]

    def apply_filters(self, qs, d):
        if d.get("user"):
            qs = qs.filter(username__icontains=d["user"])
        if d.get("action"):
            qs = qs.filter(action=d["action"])
        if d.get("model"):
            qs = qs.filter(model__icontains=d["model"])
        return apply_date_range(qs, "created_at", d.get("date_from"), d.get("date_to"))


class AuditDetail(AdminRequiredMixin, DetailView):
    model = AuditLog
    template_name = "audit/detail.html"
