from django.db import models


class ReadOnlyModel(models.Model):
    """Registos históricos (vendas/pagamentos): o Django nunca os altera nem elimina."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        raise PermissionError("Registos financeiros históricos são só de leitura.")

    def delete(self, *args, **kwargs):
        raise PermissionError("Registos financeiros históricos são só de leitura.")
