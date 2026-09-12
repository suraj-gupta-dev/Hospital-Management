from django.contrib.auth import authenticate, login, logout

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .permissions import IsAnonymousUser
from .serializers import (
    UserRegistrationSerializer, LoginSerializer,
    ChangePasswordSerializer, UserSerializer,
    DoctorProfileSerializer, PatientProfileSerializer,
    NurseProfileSerializer
)
from .models import (
    User,
    DoctorProfile, PatientProfile,
    NurseProfile,
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


class BaseProfileModelViewSet(ModelViewSet):
    queryset = None
    serializer_class = None
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            return qs.filter(user=self.request.user)
        return qs


def _make_viewsets(model, serializer):
    """
        Build a ViewSet class for `model` using `serializer`.

        The returned class inherits all behavior from BaseProfileViewSet and only
        sets `queryset` and `serializer_class`. `select_related("user")` is applied
        here to prevent N+1 queries on list endpoints.
    """
    return type(
        f"{model.__name__}ModelViewSet",
        (BaseProfileModelViewSet,),
        {"queryset": model.objects.select_related("user"), "serializer_class": serializer}
    )

DoctorProfileModelViewSet = _make_viewsets(DoctorProfile, DoctorProfileSerializer)
PatientProfileModelViewSet = _make_viewsets(PatientProfile, PatientProfileSerializer)