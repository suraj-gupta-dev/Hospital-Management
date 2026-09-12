from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from .serializers import (
    HospitalDetailSerializer,
)
from .models import  Hospital





class HospitalAPIView(APIView):
    def get(self, request):
        hospitals = Hospital.objects.first()
        serializer = HospitalDetailSerializer(hospitals)
        return Response(serializer.data)

                                          
