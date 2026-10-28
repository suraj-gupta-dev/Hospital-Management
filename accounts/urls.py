from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views



urlpatterns = [
    path("register/", views.UserCreateAPIView.as_view(), name="register"),
    path("login/", views.LoginGenericAPIView.as_view(), name="login"),
    path("logout/", views.LogoutAPIView.as_view(), name="logout"),
    path("change-password/", views.ChangePasswordAPIView.as_view(), name="change-password"),
    path("staff/", views.StaffCreateGenericAPIView.as_view(), name="staff-create"),
    path("patients/", views.PatientListCreateAPIView.as_view(), name="patients"),
    path("patients/<str:patient_id>/", views.PatientRetrieveUpdateAPIView.as_view(), name="patient-details"),
    path("patients/<str:patient_id>/picture/", views.PatientPictureUpdateAPIView.as_view(), name="patient-picture"),
]

router = DefaultRouter()
router.register("users", views.UserModelViewSet)
router.register("doctors", views.DoctorModelViewSet)
router.register("nurses", views.NurseModelViewSet)
router.register("receptionists", views.ReceptionistModelViewSet)

urlpatterns += router.urls