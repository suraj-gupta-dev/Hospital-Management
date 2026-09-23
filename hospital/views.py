from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .serializers import DepartmentSerializer, StaffDepartmentSerializer
from .permissions import IsStafforAdminOnly
from .models import Department, StaffDeparment



                                          
class DepartmentModelViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class StaffDepartmentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStafforAdminOnly]
    serializer_class = StaffDepartmentSerializer

    def post(self, request):
        serializer = StaffDepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)