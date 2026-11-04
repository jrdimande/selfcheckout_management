from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password

from apps.core.forms import BootstrapMixin

from .permissions import ADMIN_GROUP, OPERATOR_GROUP

User = get_user_model()


class UserForm(BootstrapMixin, forms.ModelForm):
    role = forms.ChoiceField(label="Perfil", choices=[(OPERATOR_GROUP, "Operador (só consulta)"),
                                                      (ADMIN_GROUP, "Administrador (acesso total)")])
    password = forms.CharField(label="Palavra-passe", required=False, widget=forms.PasswordInput(render_value=False),
                               help_text="Ao editar, deixe vazio para manter a actual.")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            from .permissions import is_admin
            self.fields["role"].initial = ADMIN_GROUP if is_admin(self.instance) else OPERATOR_GROUP
        else:
            self.fields["password"].required = True

    def clean_password(self):
        pw = self.cleaned_data.get("password")
        if pw:
            validate_password(pw, self.instance)
        return pw

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data["password"])
        user.save()
        group, _ = Group.objects.get_or_create(name=self.cleaned_data["role"])
        user.groups.set([group])
        user._is_admin = self.cleaned_data["role"] == ADMIN_GROUP
        return user


class UserFilterForm(BootstrapMixin, forms.Form):
    q = forms.CharField(required=False, label="Pesquisar", widget=forms.TextInput(attrs={"placeholder": "Utilizador, nome..."}))
