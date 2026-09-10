from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from .serializers import (
    HospitalAdminProfileSerializer, HospitalCreateSerializer,
    BranchSerializer, HospitalSerializer
)
from .models import HospitalAdminProfile, Hospital, Branch



class HospitalAdminProfileCreateAPIView(CreateAPIView):
    model = HospitalAdminProfile
    serializer_class = HospitalAdminProfileSerializer
    permission_classes = [IsAdminUser]


class HospitalListCreateAPIView(ListCreateAPIView):
    queryset = Hospital.objects.all()
    serializer_class = HospitalCreateSerializer


class HospitalAPIView(APIView):
    def get(self, request):
        hospitals = Hospital.objects.all()
        serializer = HospitalSerializer(hospitals, many=True)
        return Response(serializer.data)

                                          
class BranchGenericAPIView(GenericAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    def get(self, request):
        branches = self.get_queryset()
        serializer = self.get_serializer(branches, many=True)
        return Response(serializer.data)
