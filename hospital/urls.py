from django.urls import path

from . import views



urlpatterns = [
    path("hospitals/", views.HospitalAPIView.as_view(), name="hospitals"),
    path("hospital/add/", views.HospitalListCreateAPIView.as_view(), name="add-hospital"),
    path("hospital/admin/profile/", views.HospitalAdminProfileCreateAPIView.as_view(), name="hos-adm-pro"),   
    path("branches/", views.BranchGenericAPIView.as_view(), name="branches"),   
]
