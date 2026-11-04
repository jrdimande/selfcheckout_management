from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework.permissions import SAFE_METHODS, BasePermission

ADMIN_GROUP = "Administrador"
OPERATOR_GROUP = "Operador"


def is_admin(user):
    if not (user.is_authenticated and user.is_active):
        return False
    if not hasattr(user, "_is_admin"):
        user._is_admin = user.is_superuser or user.groups.filter(name=ADMIN_GROUP).exists()
    return user._is_admin


def roles(request):
    return {"is_admin": is_admin(request.user), "CURRENCY": settings.CURRENCY}


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_admin(self.request.user)


class AdminWriteOrReadOnly(BasePermission):
    """API: autenticados leem; só administradores escrevem."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.method in SAFE_METHODS or is_admin(request.user)
