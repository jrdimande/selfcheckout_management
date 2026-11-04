from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.core.models import ReadOnlyModel


class Sale(ReadOnlyModel):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey("customers.Customer", on_delete=models.DO_NOTHING, db_column="customer_uuid",
                                 related_name="sales")
    sale_date = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = "sale"
        ordering = ["-sale_date", "-id"]

    def __str__(self):
        return f"Venda #{self.pk}"

    def get_absolute_url(self):
        return reverse("sales:detail", args=[self.pk])

    @property
    def payment_methods(self):
        return ", ".join(sorted({p.payment_method for p in self.payments.all()}))


class SaleItem(ReadOnlyModel):
    id = models.AutoField(primary_key=True)
    sale = models.ForeignKey(Sale, on_delete=models.DO_NOTHING, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.DO_NOTHING, db_column="product_uuid",
                                related_name="sale_items")
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = "sale_item"
