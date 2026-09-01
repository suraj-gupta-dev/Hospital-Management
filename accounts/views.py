from django.contrib.auth import authenticate, login, logout

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from .serializers import UserRegistrationSerializer, LoginSerializer, ChangePasswordSerializer
from .models import User


# @api_view(["POST"])
# def user_register(request):
#     serializer = UserRegistrationSerializer(request.data)
#     if serializer.is_valid():
#         user = serializer.save()
#         return Response({
#             'status': 'success',
#             'message': 'User registered successfully',
#             'data': {
#                 'id': user.id,
#                 'email': user.email,
#                 'full_name': user.full_name if hasattr(user, 'full_name') else f"{user.first_name} {user.last_name}".strip()
#             }
#         }, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors)


class UserCreateAPIView(CreateAPIView):
    model = User
    serializer_class = UserRegistrationSerializer

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


# class LoginAPIView(APIView):
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         email = serializer.validated_data["email"]
#         password = serializer.validated_data["password"]
#         user = authenticate(email=email, password=password)
#         if user is not None:
#             login(request, user)
#             return Response({"message": "Successfully logged in.", "email": email})
#         return Response({"error": "Invalid credential"}, status=status.HTTP_401_UNAUTHORIZED)


class LoginGenericAPIView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self/self.get_serializer(data=request.data)
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