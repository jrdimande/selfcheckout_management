from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    ACTIONS = [("create", "Criação"), ("update", "Actualização"), ("delete", "Eliminação")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    username = models.CharField(max_length=150)
    action = models.CharField(max_length=20, choices=ACTIONS)
    model = models.CharField("Registo", max_length=100)
    object_id = models.CharField(max_length=100)
    object_repr = models.CharField(max_length=255)
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("audit:detail", args=[self.pk])

    def diff(self):
        keys = list((self.before or {}).keys() | (self.after or {}).keys())
        return [(k, (self.before or {}).get(k, "—"), (self.after or {}).get(k, "—"),
                 (self.before or {}).get(k) != (self.after or {}).get(k)) for k in sorted(keys)]
