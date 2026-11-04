from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import DetailView

from apps.core.utils import sum0
from apps.core.views import CreateRecord, DeleteRecord, FilteredListView, UpdateRecord

from .forms import CustomerCreateForm, CustomerFilterForm, CustomerUpdateForm
from .models import Customer

LIST = reverse_lazy("customers:list")


class CustomerList(FilteredListView):
    title = "Clientes"
    model = Customer
    filter_form_class = CustomerFilterForm
    columns = [("UUID", "uuid"), ("Nome", "name"), ("Saldo", "balance", "money"),
               ("Compras", "purchases"), ("Total gasto", "spent", "money")]
    detail_url, edit_url, delete_url = "customers:detail", "customers:edit", "customers:delete"
    create_url, create_label = "customers:create", "Novo cliente"

    def base_queryset(self):
        return Customer.objects.annotate(purchases=Count("sales"), spent=sum0("sales__total")).order_by("name")

    def apply_filters(self, qs, d):
        q = d.get("q")
        return qs.filter(Q(name__icontains=q) | Q(uuid__icontains=q)) if q else qs


class CustomerDetail(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = "customers/detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        sales = self.object.sales.prefetch_related("payments")
        agg = sales.aggregate(n=Count("id"), spent=sum0("total"))
        ctx.update(sales=sales[:50], purchases=agg["n"], spent=agg["spent"])
        return ctx


class CustomerCreate(CreateRecord):
    model, form_class = Customer, CustomerCreateForm
    title, cancel_url, success_message = "Novo cliente", LIST, "Cliente registado."


class CustomerEdit(UpdateRecord):
    model, form_class = Customer, CustomerUpdateForm
    title, cancel_url, success_message = "Editar cliente", LIST, "Cliente actualizado."


class CustomerDelete(DeleteRecord):
    model = Customer
    success_url_name = "customers:list"
