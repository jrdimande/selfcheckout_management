from decimal import Decimal

from django.db import models
from django.urls import reverse


class Customer(models.Model):
    uuid = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        managed = False
        db_table = "customer"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.uuid})"

    def get_absolute_url(self):
        return reverse("customers:detail", args=[self.pk])

    def deletion_blocker(self):
        n = self.sales.count()
        return f"O cliente tem {n} venda(s) associada(s) e não pode ser eliminado." if n else None
