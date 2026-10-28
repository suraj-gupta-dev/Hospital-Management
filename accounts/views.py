from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.middleware.csrf import get_token
from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, GenericAPIView, ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


from .permissions import (
    IsAnonymousUser, PatientAccessPermission,
    IsDoctorReceptOrAdmin
)

from .serializers import (
    UserRegistrationSerializer, LoginSerializer,
    ChangePasswordSerializer, AdminReadUserSerializer,
    DoctorProfileSerializer, NurseProfileSerializer,
    ReceptionistProfileSerializer, StaffCreateSerializer,
    ProfilePictureSerializer, PatientListCreateSerializer,
    PatientRetrieveUpdateSerializer
)
from .serializers import STAFF_PROFILE_MAP
from .models import (
    User, PatientUser,
    DoctorProfile, NurseProfile,
    ReceptionistProfile, PatientProfile
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
    serializer_class = AdminReadUserSerializer
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


class PatientListCreateAPIView(ListCreateAPIView):
    queryset = PatientUser.objects.select_related("patient_profile")
    serializer_class = PatientListCreateSerializer
    permission_classes = [IsAuthenticated, PatientAccessPermission]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        if getattr(self.request.user, 'role', None) == User.RoleChoices.PATIENT:
            return super().get_queryset().filter(pk=self.request.user.pk)
        return super().get_queryset()


class PatientRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = PatientUser.objects.select_related("patient_profile")
    serializer_class = PatientRetrieveUpdateSerializer
    permission_classes = [IsAuthenticated, PatientAccessPermission]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    lookup_field = "patient_profile__patient_id"
    lookup_url_kwarg = "patient_id"

    def get_queryset(self):
        if getattr(self.request.user, 'role', None) == User.RoleChoices.PATIENT:
            return super().get_queryset().filter(pk=self.request.user.pk)
        return super().get_queryset()
    

class PatientPictureUpdateAPIView(GenericAPIView):
    serializer_class = ProfilePictureSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient_id = self.kwargs["patient_id"]
        patient_profile = get_object_or_404(PatientProfile, pk=patient_id)
        patient_profile.profile_picture = serializer.validated_data["profile_picture"]
        patient_profile.save()
        return Response({
            "message": "profile picture uploaded successfully."
        }, status=status.HTTP_200_OK)


class BaseProfileModelViewSet(ModelViewSet):
    http_method_names = ["get", "put", "patch", "delete"]
    USER_ROLE = None

    def get_queryset(self):
            if getattr(self.request.user, 'role', None) == self.USER_ROLE:
                return super().get_queryset().filter(user=self.request.user)
            return super().get_queryset()
    
    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="picture",
        parser_classes=[MultiPartParser, FormParser],
        serializer_class=ProfilePictureSerializer
    )
    def picture(self, request, pk=None):
        profile = self.get_object()

        is_owner = profile.user == request.user
        is_admin = request.user.is_superuser or request.user.role == "HA"
        # only the owner or an admin may change a picture
        if not (is_owner or is_admin):
            raise PermissionDenied("you don't have permission.")

        if request.method == "DELETE":
            if profile.profile_picture:
                profile.profile_picture.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = ProfilePictureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if profile.profile_picture: # remove the old file so media doesn't pile up
            profile.profile_picture.delete(save=False)
        profile.profile_picture = serializer.validated_data["profile_picture"]
        profile.save(update_fields=["profile_picture", "updated_at"])

        return Response({
            "profile_picture": request.build_absolute_uri(profile.profile_picture.url)
        }, status=status.HTTP_200_OK)


class DoctorModelViewSet(BaseProfileModelViewSet):
    queryset = DoctorProfile.objects.prefetch_related("user")
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated, IsDoctorReceptOrAdmin]
    USER_ROLE = User.RoleChoices.DOCTOR


class NurseModelViewSet(BaseProfileModelViewSet):
    queryset = NurseProfile.objects.prefetch_related("user")
    serializer_class = NurseProfileSerializer
    permission_classes = [IsAuthenticated, IsDoctorReceptOrAdmin]
    USER_ROLE = User.RoleChoices.NURSE


class ReceptionistModelViewSet(BaseProfileModelViewSet):
    queryset = ReceptionistProfile.objects.prefetch_related("user")
    serializer_class = ReceptionistProfileSerializer
    permission_classes = [IsAuthenticated, IsDoctorReceptOrAdmin]
    USER_ROLE = User.RoleChoices.RECEPTIONIST


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
            "user": AdminReadUserSerializer(user).data,
            "profile": profile_serializer_cls(profile, context={"request": request}).data
        }, status=status.HTTP_201_CREATED)

