from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Case, Exists, OuterRef, Q, Value, CharField, When
from django.urls import reverse_lazy

from apps.core.views import CreateRecord, FilteredListView, UpdateRecord
from apps.accounts.permissions import ADMIN_GROUP, AdminRequiredMixin

from .forms import UserFilterForm, UserForm

User = get_user_model()
DEFAULT_DB = "default"


class UserList(AdminRequiredMixin, FilteredListView):
    title = "Utilizadores"
    model = User
    filter_form_class = UserFilterForm
    columns = [("Utilizador", "username"), ("Nome", "get_full_name"), ("Email", "email"),
               ("Perfil", "role_label", "badge"), ("Activo", "is_active", "bool"), ("Último acesso", "last_login", "date")]
    edit_url = "accounts:user_edit"
    create_url = "accounts:user_create"
    create_label = "Novo utilizador"

    def base_queryset(self):
        in_admin = Exists(User.groups.through.objects.filter(user_id=OuterRef("pk"), group__name=ADMIN_GROUP))
        return User.objects.annotate(is_adm=in_admin).annotate(
            role_label=Case(When(Q(is_superuser=True) | Q(is_adm=True), then=Value(ADMIN_GROUP)),
                            default=Value("Operador"), output_field=CharField())).order_by("username")

    def apply_filters(self, qs, d):
        q = d.get("q")
        return qs.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)) if q else qs


class UserCreate(CreateRecord):
    model = User
    form_class = UserForm
    db = DEFAULT_DB
    title = "Novo utilizador"
    success_url = reverse_lazy("accounts:users")
    cancel_url = reverse_lazy("accounts:users")


class UserEdit(UpdateRecord):
    model = User
    form_class = UserForm
    db = DEFAULT_DB
    title = "Editar utilizador"
    success_url = reverse_lazy("accounts:users")
    cancel_url = reverse_lazy("accounts:users")
