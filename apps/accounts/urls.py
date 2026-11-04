from django.contrib.auth import views as auth
from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("login/", auth.LoginView.as_view(template_name="registration/login.html", redirect_authenticated_user=True), name="login"),
    path("logout/", auth.LogoutView.as_view(), name="logout"),
    path("users/", views.UserList.as_view(), name="users"),
    path("users/new/", views.UserCreate.as_view(), name="user_create"),
    path("users/<int:pk>/edit/", views.UserEdit.as_view(), name="user_edit"),
]
