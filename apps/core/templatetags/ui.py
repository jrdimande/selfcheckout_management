from decimal import Decimal

from django import template
from django.conf import settings
from django.utils.html import format_html

register = template.Library()
BADGES = {"OK": "success", "Stock baixo": "warning", "Sem stock": "danger",
          "Administrador": "primary", "Operador": "secondary"}


@register.filter
def money(v):
    if v is None or v == "":
        return "—"
    return f"{Decimal(v):,.2f} {settings.CURRENCY}".strip()


@register.filter
def attr(obj, path):
    for part in path.split("."):
        if obj is None:
            return None
        obj = getattr(obj, part, None)
        if callable(obj):
            obj = obj()
    return obj


@register.simple_tag
def cell(obj, col):
    value = attr(obj, col[1])
    kind = col[2] if len(col) > 2 else ""
    if value is None or value == "":
        return "—"
    if kind == "money":
        return money(value)
    if kind == "date":
        return value.strftime("%d/%m/%Y %H:%M")
    if kind == "badge":
        return format_html('<span class="badge text-bg-{}">{}</span>', BADGES.get(value, "secondary"), value)
    if kind == "bool":
        return format_html('<i class="bi bi-{}"></i>', "check-circle-fill text-success" if value else "x-circle text-muted")
    return value


@register.simple_tag(takes_context=True)
def qs(context, **kwargs):
    q = context["request"].GET.copy()
    for k, v in kwargs.items():
        q[k] = v
    return q.urlencode()
