from django.urls import path

from . import views

app_name = "sales"
urlpatterns = [
    path("", views.SaleList.as_view(), name="list"),
    path("<int:pk>/", views.SaleDetail.as_view(), name="detail"),
]
