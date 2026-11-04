import uuid as _uuid

from rest_framework import serializers

from apps.customers.models import Customer
from apps.payments.models import Payment
from apps.products.models import Product
from apps.sales.models import Sale, SaleItem


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["uuid", "name", "balance"]
        extra_kwargs = {"uuid": {"required": False}}

    def validate_name(self, v):
        v = v.strip()
        if not v:
            raise serializers.ValidationError("O nome não pode ser vazio.")
        return v

    def create(self, data):
        data.setdefault("uuid", str(_uuid.uuid4()))
        return Customer.objects.create(**data)

    def update(self, instance, data):
        # uuid e saldo são geridos pela app Self-Checkout: não se alteram por aqui.
        data.pop("uuid", None)
        data.pop("balance", None)
        return super().update(instance, data)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["uuid", "name", "price", "stock", "minimum_stock"]
        extra_kwargs = {"uuid": {"required": False}}

    def validate(self, a):
        for f in ("price", "stock", "minimum_stock"):
            if f in a and a[f] < 0:
                raise serializers.ValidationError({f: "Não pode ser negativo."})
        return a

    def create(self, data):
        data.setdefault("uuid", str(_uuid.uuid4()))
        return Product.objects.create(**data)

    def update(self, instance, data):
        data.pop("uuid", None)
        return super().update(instance, data)


class SaleItemSerializer(serializers.ModelSerializer):
    product_uuid = serializers.CharField(source="product_id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = SaleItem
        fields = ["id", "product_uuid", "product_name", "quantity", "unit_price", "subtotal"]


class PaymentSerializer(serializers.ModelSerializer):
    sale_date = serializers.DateTimeField(source="sale.sale_date", read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "sale", "sale_date", "amount", "payment_method"]


class SaleSerializer(serializers.ModelSerializer):
    customer_uuid = serializers.CharField(source="customer_id", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    items = SaleItemSerializer(many=True, read_only=True)
    payments = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = ["id", "customer_uuid", "customer_name", "sale_date", "total", "items", "payments"]

    def get_payments(self, obj):
        return [{"id": p.id, "amount": str(p.amount), "payment_method": p.payment_method} for p in obj.payments.all()]
