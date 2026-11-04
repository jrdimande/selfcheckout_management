from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("customers", views.CustomerViewSet, basename="customer")
router.register("products", views.ProductViewSet, basename="product")
router.register("sales", views.SaleViewSet, basename="sale")
router.register("payments", views.PaymentViewSet, basename="payment")

urlpatterns = [
    path("dashboard/statistics/", views.DashboardStatistics.as_view(), name="dashboard-statistics"),
    path("", include(router.urls)),
]
