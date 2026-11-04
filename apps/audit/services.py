import json
import logging

from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)


def snapshot(obj):
    """Valores dos campos do registo (nunca inclui passwords)."""
    data = {f.name: getattr(obj, f.attname) for f in obj._meta.concrete_fields if "password" not in f.name}
    return json.loads(json.dumps(data, cls=DjangoJSONEncoder))


def log(request, action, obj, before=None, after=None, *, object_id=None, object_repr=None):
    from .models import AuditLog
    user = request.user if request.user.is_authenticated else None
    try:
        AuditLog.objects.create(
            user=user, username=user.get_username() if user else "anónimo", action=action,
            model=obj._meta.label, object_id=str(object_id if object_id is not None else obj.pk),
            object_repr=(object_repr or str(obj))[:255], before=before, after=after)
    except Exception:  # a auditoria nunca deve rebentar a operação já concluída
        logger.exception("Falha ao gravar o registo de auditoria")
