from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .services import get_statistics


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        s = get_statistics()
        ctx["s"] = s
        ctx["chart"] = {
            "daily": {"labels": [d["date"][5:] for d in s["daily_sales"]],
                      "sales": [d["sales"] for d in s["daily_sales"]],
                      "revenue": [float(d["revenue"]) for d in s["daily_sales"]]},
            "monthly": {"labels": [m["month"] for m in s["monthly_revenue"]],
                        "revenue": [float(m["revenue"]) for m in s["monthly_revenue"]]},
            "payments": {"labels": [p["payment_method"] for p in s["payment_methods"]],
                         "totals": [float(p["total"]) for p in s["payment_methods"]]},
        }
        return ctx
