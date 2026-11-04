from django.urls import path

from . import views

app_name = "audit"
urlpatterns = [
    path("", views.AuditList.as_view(), name="list"),
    path("<int:pk>/", views.AuditDetail.as_view(), name="detail"),
]
