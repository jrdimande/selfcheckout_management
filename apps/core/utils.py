from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db.models import DecimalField, Sum
from django.db.models.functions import Coalesce


def apply_date_range(qs, field, d_from=None, d_to=None):
    if d_from:
        qs = qs.filter(**{f"{field}__gte": datetime.combine(d_from, time.min)})
    if d_to:
        qs = qs.filter(**{f"{field}__lt": datetime.combine(d_to + timedelta(days=1), time.min)})
    return qs


def sum0(expr, **kw):
    """SUM() que devolve 0 em vez de NULL."""
    return Coalesce(Sum(expr, **kw), Decimal("0"), output_field=DecimalField(max_digits=14, decimal_places=2))
