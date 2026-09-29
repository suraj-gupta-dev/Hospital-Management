from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action

from .permissions import (
    IsAnonymousUser, PatientAccessPermission,
    IsDoctorRecepOrAdmin, IsOwnerOnly,
    IsDocRecepNurseOrAdmin
)

from .serializers import (
    UserRegistrationSerializer, LoginSerializer,
    ChangePasswordSerializer, UserSerializer,
    DoctorProfileSerializer, PatientProfileSerializer,
    NurseProfileSerializer, ReceptionistProfileSerializer,
    PatientProfileCreateSerializer
)
from .models import (
    User,
    DoctorProfile, PatientProfile,
    NurseProfile, ReceptionistProfile,
)






class UserCreateAPIView(CreateAPIView):
    model = User
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAnonymousUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'status': 'success',
            'message': 'User registered successfully',
            'data': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name if hasattr(user, 'full_name') else f"{user.first_name} {user.last_name}".strip()
            }
        }, status=status.HTTP_201_CREATED)


class LoginGenericAPIView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [IsAnonymousUser]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Successfully logged in.", "email": email})
        return Response({"error": "Invalid credential"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logout(request)
        return Response({"message": "Successfully LogOut!"})


class ChangePasswordAPIView(APIView):
    """
    API endpoint to change user password.
    Optionally logs out user from all sessions.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()

            logout(request)

            return Response({
                    'status': 'success',
                    'message': 'Password changed successfully. Please login again with your new password.'
                }, status=status.HTTP_200_OK)
        
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ["get", "put", "patch", "delete"]
    permission_classes = [IsAuthenticated, IsAdminUser]


class BaseProfileModelViewSet(ModelViewSet):
    def get_object(self):
        obj = get_object_or_404(super().get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        if getattr(self.request.user, 'role', None) == "PAT":
            return super().get_queryset().filter(user=self.request.user)
        return super().get_queryset()


class DoctorModelViewSet(BaseProfileModelViewSet):
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated, IsDoctorRecepOrAdmin]


class PatientModelViewSet(BaseProfileModelViewSet):
    queryset = PatientProfile.objects.all()
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated, PatientAccessPermission]

    def perform_create(self, serializer):
        serializer.save(role="PAT")

    def get_serializer_class(self):
        if self.action == "create":
            return PatientProfileCreateSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=["GET", "PUT"],
        permission_classes=[IsOwnerOnly],
        url_path="me"
    )
    def logged_in_patient(self, request):
        patient = get_object_or_404(PatientProfile, user=request.user)

        if request.method == "GET":
            serializer = self.get_serializer(patient)
            return Response(serializer.data)
        serializer = self.get_serializer(patient, data=request.data, partial=request.method=="PUT")
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class NurseModelViewSet(BaseProfileModelViewSet):
    queryset = NurseProfile.objects.all()
    serializer_class = NurseProfileSerializer
    permission_classes = [IsAuthenticated, IsDocRecepNurseOrAdmin]


class ReceptionistModelViewSet(BaseProfileModelViewSet):
    queryset = ReceptionistProfile.objects.all()
    serializer_class = ReceptionistProfileSerializer
    permission_classes = [IsAuthenticated, IsDoctorRecepOrAdmin]