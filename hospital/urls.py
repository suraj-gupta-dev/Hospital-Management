from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views



urlpatterns = [path("staff-depart/create/", views.StaffDepartmentAPIView.as_view(), name="staff-depart")]

router = DefaultRouter()
router.register("departments", views.DepartmentModelViewSet)

urlpatterns += router.urls