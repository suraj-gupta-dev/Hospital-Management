from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action

from .permissions import (
    IsAnonymousUser, PatientAccessPermission,
    IsDoctorReceptOrAdmin, IsOwnerOnly,
)

from .serializers import (
    UserRegistrationSerializer, LoginSerializer,
    ChangePasswordSerializer, UserSerializer,
    DoctorProfileSerializer, PatientProfileSerializer,
    NurseProfileSerializer, ReceptionistProfileSerializer,
    ReceptCreatePatientSerializer, StaffCreateSerializer
)
from .serializers import STAFF_PROFILE_MAP
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
        user = serializer.save(role=User.RoleChoices.PATIENT)
        return Response({
            'status': 'success',
            'message': 'User registered successfully',
            'data': {
                'id': user.user_id,
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

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path="me"
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class DoctorModelViewSet(ModelViewSet):
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated, IsDoctorReceptOrAdmin]

    def get_queryset(self):
        if getattr(self.request.user, 'role', None) == User.RoleChoices.DOCTOR:
            return super().get_queryset().filter(user=self.request.user)
        return super().get_queryset()


class PatientModelViewSet(ModelViewSet):
    queryset = PatientProfile.objects.all()
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated, PatientAccessPermission]

    def get_queryset(self):
        if getattr(self.request.user, 'role', None) == "PAT":
            return super().get_queryset().filter(user=self.request.user)
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(role="PAT")

    def get_serializer_class(self):
        if self.action == "create":
            return ReceptCreatePatientSerializer
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


class NurseModelViewSet(ModelViewSet):
    queryset = NurseProfile.objects.all()
    serializer_class = NurseProfileSerializer
    permission_classes = [IsAuthenticated, IsDoctorReceptOrAdmin]

    def get_queryset(self):
        if getattr(self.request.user, 'role', None) == User.RoleChoices.NURSE:
            return super().get_queryset().filter(user=self.request.user)
        return super().get_queryset()


class ReceptionistModelViewSet(ModelViewSet):
    queryset = ReceptionistProfile.objects.all()
    serializer_class = ReceptionistProfileSerializer
    permission_classes = [IsAuthenticated, IsDoctorReceptOrAdmin]

    def get_queryset(self):
        if getattr(self.request.user, 'role', None) == User.RoleChoices.RECEPTIONIST:
            return super().get_queryset().filter(user=self.request.user)
        return super().get_queryset()


class StaffCreateGenericAPIView(GenericAPIView):
    serializer_class = StaffCreateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            result = serializer.save()
            user, profile = result["user"], result["profile"]
            _, profile_serializer_cls = STAFF_PROFILE_MAP[user.role]

        return Response({
            "status": "success",
            "message": f"{user.get_role_display() if hasattr(user, 'get_role_display') else user.role}",
            "user": UserSerializer(user).data,
            "profile": profile_serializer_cls(profile, context={"request": request}).data
        }, status=status.HTTP_201_CREATED)
