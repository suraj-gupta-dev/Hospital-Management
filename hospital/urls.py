from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views



urlpatterns = []

router = DefaultRouter()
router.register("departments", views.DepartmentModelViewSet)

urlpatterns += router.urls