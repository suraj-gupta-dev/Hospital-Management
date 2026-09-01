from django.urls import path
from . import views



urlpatterns = [
    path("register/", views.UserCreateAPIView.as_view(), name="register"),
    path("login/", views.LoginGenericAPIView.as_view(), name="login"),
    path("logout/", views.LogoutAPIView.as_view(), name="logout"),
    path("change-password/", views.ChangePasswordAPIView.as_view(), name="change-password")
]
