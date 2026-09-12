from django.urls import path

from . import views



urlpatterns = [
    path("hospital/", views.HospitalAPIView.as_view(), name="hospital-details"),
]
