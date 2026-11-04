import uuid as _uuid

from django import forms

from apps.core.forms import BootstrapMixin

from .models import Product

LABELS = {"name": "Nome", "price": "Preço", "stock": "Stock", "minimum_stock": "Stock mínimo"}


class ProductCreateForm(BootstrapMixin, forms.ModelForm):
    uuid = forms.CharField(max_length=100, required=False, label="UUID / código de barras",
                           help_text="Deixe vazio para gerar automaticamente.")

    class Meta:
        model = Product
        fields = ["uuid", "name", "price", "stock", "minimum_stock"]
        labels = LABELS

    def clean_uuid(self):
        value = (self.cleaned_data.get("uuid") or "").strip() or str(_uuid.uuid4())
        if Product.objects.filter(pk=value).exists():
            raise forms.ValidationError("Já existe um produto com este UUID.")
        return value


class ProductUpdateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "price", "stock", "minimum_stock"]
        labels = LABELS


class ProductPriceForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ["price"]
        labels = LABELS


class ProductFilterForm(BootstrapMixin, forms.Form):
    q = forms.CharField(required=False, label="Pesquisar", widget=forms.TextInput(attrs={"placeholder": "Nome ou UUID"}))
    stock = forms.ChoiceField(required=False, label="Stock", choices=[("", "Todos"), ("low", "Stock baixo"), ("out", "Sem stock")])
