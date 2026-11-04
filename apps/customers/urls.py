from django.urls import path

from . import views

app_name = "customers"
urlpatterns = [
    path("", views.CustomerList.as_view(), name="list"),
    path("new/", views.CustomerCreate.as_view(), name="create"),
    path("<str:pk>/", views.CustomerDetail.as_view(), name="detail"),
    path("<str:pk>/edit/", views.CustomerEdit.as_view(), name="edit"),
    path("<str:pk>/delete/", views.CustomerDelete.as_view(), name="delete"),
]
