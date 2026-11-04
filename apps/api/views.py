from django.db import transaction
from rest_framework import filters, viewsets
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import AdminWriteOrReadOnly
from apps.audit.services import log, snapshot
from apps.core.utils import apply_date_range
from apps.customers.models import Customer
from apps.dashboard.services import get_statistics
from apps.payments.models import Payment
from apps.products.models import Product
from apps.sales.models import Sale

from .serializers import CustomerSerializer, PaymentSerializer, ProductSerializer, SaleSerializer

DB = "selfcheckout"


class Conflict(APIException):
    status_code = 409
    default_detail = "Operação não permitida pelas regras de integridade."


class AuditedModelViewSet(viewsets.ModelViewSet):
    permission_classes = [AdminWriteOrReadOnly]
    lookup_field = "uuid"
    lookup_value_regex = "[^/]+"
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "uuid"]

    def perform_create(self, serializer):
        with transaction.atomic(using=DB):
            obj = serializer.save()
        log(self.request, "create", obj, None, snapshot(obj))

    def perform_update(self, serializer):
        before = snapshot(serializer.instance)
        with transaction.atomic(using=DB):
            obj = serializer.save()
        log(self.request, "update", obj, before, snapshot(obj))

    def perform_destroy(self, instance):
        blocker = instance.deletion_blocker()
        if blocker:
            raise Conflict(blocker)
        before, pk, label = snapshot(instance), instance.pk, str(instance)
        with transaction.atomic(using=DB):
            instance.delete()
        log(self.request, "delete", instance, before, None, object_id=pk, object_repr=label)


class CustomerViewSet(AuditedModelViewSet):
    queryset = Customer.objects.order_by("name")
    serializer_class = CustomerSerializer


class ProductViewSet(AuditedModelViewSet):
    queryset = Product.objects.order_by("name")
    serializer_class = ProductSerializer


class SaleViewSet(viewsets.ReadOnlyModelViewSet):
    """Vendas: só leitura (registos históricos)."""
    serializer_class = SaleSerializer

    def get_queryset(self):
        qs = (Sale.objects.select_related("customer").prefetch_related("items__product", "payments"))
        p = self.request.query_params
        if p.get("customer"):
            qs = qs.filter(customer_id=p["customer"])
        try:
            from datetime import date
            d_from = date.fromisoformat(p["date_from"]) if p.get("date_from") else None
            d_to = date.fromisoformat(p["date_to"]) if p.get("date_to") else None
        except ValueError:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Datas inválidas (use AAAA-MM-DD).")
        return apply_date_range(qs, "sale_date", d_from, d_to)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """Pagamentos: só leitura."""
    serializer_class = PaymentSerializer

    def get_queryset(self):
        qs = Payment.objects.select_related("sale")
        if self.request.query_params.get("method"):
            qs = qs.filter(payment_method=self.request.query_params["method"])
        return qs


class DashboardStatistics(APIView):
    def get(self, request):
        return Response(get_statistics())
