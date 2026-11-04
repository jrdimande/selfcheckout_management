from django import forms
from django.shortcuts import render
from django.views import View

from apps.accounts.permissions import AdminRequiredMixin
from apps.core.forms import BootstrapMixin, date_field

from . import exports
from .services import REPORTS, build


class ReportForm(BootstrapMixin, forms.Form):
    kind = forms.ChoiceField(label="Relatório", choices=list(REPORTS.items()))
    date_from = date_field("De")
    date_to = date_field("Até")


class ReportView(AdminRequiredMixin, View):
    def get(self, request):
        form = ReportForm(request.GET or {"kind": "sales_daily"})
        report = None
        if form.is_valid():
            d = form.cleaned_data
            report = build(d["kind"], d["date_from"], d["date_to"])
            fmt = request.GET.get("export")
            if fmt == "xlsx":
                return exports.to_xlsx(report, d["kind"])
            if fmt == "pdf":
                return exports.to_pdf(report, d["kind"])
        return render(request, "reports/index.html", {"form": form, "report": report})
