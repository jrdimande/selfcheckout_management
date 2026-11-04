from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Product(models.Model):
    uuid = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    minimum_stock = models.IntegerField(default=5, validators=[MinValueValidator(0)])

    class Meta:
        managed = False
        db_table = "product"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.uuid})"

    def get_absolute_url(self):
        return reverse("products:detail", args=[self.pk])

    @property
    def stock_status(self):
        if self.stock <= 0:
            return "Sem stock"
        return "Stock baixo" if self.stock <= self.minimum_stock else "OK"

    def deletion_blocker(self):
        n = self.sale_items.count()
        return f"O produto consta em {n} linha(s) de venda e não pode ser eliminado." if n else None
