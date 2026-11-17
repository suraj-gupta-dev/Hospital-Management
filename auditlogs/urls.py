from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("auditlogs", views.ReadOnlyAuditLogViewSet)

urlpatterns = [
    # path("auditlogs/", views.ReadOnlyAuditLogView.as_view()),
]

urlpatterns += router.urls