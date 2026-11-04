from django.db import models
from django.urls import reverse

from apps.core.models import ReadOnlyModel


class Payment(ReadOnlyModel):
    id = models.AutoField(primary_key=True)
    sale = models.ForeignKey("sales.Sale", on_delete=models.DO_NOTHING, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "payment"
        ordering = ["-sale__sale_date", "-id"]

    def __str__(self):
        return f"Pagamento #{self.pk}"

    def get_absolute_url(self):
        return reverse("payments:detail", args=[self.pk])

    @property
    def payment_date(self):
        # A tabela `payment` não tem data: usa-se a data da venda associada.
        return self.sale.sale_date
