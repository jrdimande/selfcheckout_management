from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q, Sum
from django.urls import reverse_lazy
from django.views.generic import DetailView

from apps.core.utils import sum0
from apps.core.views import CreateRecord, DeleteRecord, FilteredListView, UpdateRecord
from apps.sales.models import SaleItem

from .forms import ProductCreateForm, ProductFilterForm, ProductPriceForm, ProductUpdateForm
from .models import Product

LIST = reverse_lazy("products:list")


class ProductList(FilteredListView):
    title = "Produtos"
    model = Product
    filter_form_class = ProductFilterForm
    columns = [("UUID", "uuid"), ("Nome", "name"), ("Preço", "price", "money"), ("Stock", "stock"),
               ("Mínimo", "minimum_stock"), ("Estado", "stock_status", "badge"), ("Un. vendidas", "sold")]
    detail_url, edit_url, delete_url = "products:detail", "products:edit", "products:delete"
    create_url, create_label = "products:create", "Novo produto"

    def base_queryset(self):
        return Product.objects.annotate(sold=Sum("sale_items__quantity")).order_by("name")

    def apply_filters(self, qs, d):
        if d.get("q"):
            qs = qs.filter(Q(name__icontains=d["q"]) | Q(uuid__icontains=d["q"]))
        if d.get("stock") == "low":
            qs = qs.filter(stock__lte=F("minimum_stock"))
        elif d.get("stock") == "out":
            qs = qs.filter(stock__lte=0)
        return qs


class ProductDetail(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "products/detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        items = SaleItem.objects.filter(product=self.object)
        agg = items.aggregate(qty=Sum("quantity"), revenue=sum0("subtotal"))
        ctx.update(sold=agg["qty"] or 0, revenue=agg["revenue"],
                   recent=items.select_related("sale", "sale__customer").order_by("-sale__sale_date", "-id")[:20])
        return ctx


class ProductCreate(CreateRecord):
    model, form_class = Product, ProductCreateForm
    title, cancel_url, success_message = "Novo produto", LIST, "Produto registado."


class ProductEdit(UpdateRecord):
    model, form_class = Product, ProductUpdateForm
    title, cancel_url, success_message = "Editar produto", LIST, "Produto actualizado."


class ProductPrice(UpdateRecord):
    model, form_class = Product, ProductPriceForm
    title, cancel_url, success_message = "Actualizar preço", LIST, "Preço actualizado."


class ProductDelete(DeleteRecord):
    model = Product
    success_url_name = "products:list"
