import uuid as _uuid

from django import forms

from apps.core.forms import BootstrapMixin

from .models import Customer


class CustomerCreateForm(BootstrapMixin, forms.ModelForm):
    uuid = forms.CharField(max_length=100, required=False, label="UUID (cartão RFID)",
                           help_text="Deixe vazio para gerar automaticamente.")

    class Meta:
        model = Customer
        fields = ["uuid", "name", "balance"]
        labels = {"name": "Nome", "balance": "Saldo inicial"}

    def clean_uuid(self):
        value = (self.cleaned_data.get("uuid") or "").strip() or str(_uuid.uuid4())
        if Customer.objects.filter(pk=value).exists():
            raise forms.ValidationError("Já existe um cliente com este UUID.")
        return value

    def clean_name(self):
        return self.cleaned_data["name"].strip()


class CustomerUpdateForm(BootstrapMixin, forms.ModelForm):
    """O saldo não é editável aqui: é gerido pela aplicação Self-Checkout."""

    class Meta:
        model = Customer
        fields = ["name"]
        labels = {"name": "Nome"}


class CustomerFilterForm(BootstrapMixin, forms.Form):
    q = forms.CharField(required=False, label="Pesquisar", widget=forms.TextInput(attrs={"placeholder": "Nome ou UUID"}))
