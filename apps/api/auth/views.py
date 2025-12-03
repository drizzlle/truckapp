from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import secrets
import random

from .serializers import (
    CustomerRegistrationSerializer,
    DriverRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer,
    EmailVerificationRequestSerializer,
    EmailVerificationConfirmSerializer,
)
from apps.api.users.serializers import UserSerializer
from apps.core.email_utils import (
    send_password_reset_email,
    send_email_verification_email,
    send_welcome_email,
)

User = get_user_model()

class CustomerRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomerRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        send_welcome_email(user, user_type='customer')

        return Response({
            "message": "Customer registered successfully",
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
        }, status=status.HTTP_201_CREATED)

class DriverRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = DriverRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        send_welcome_email(user, user_type='driver')

        return Response({
            "message": "Driver registered successfully",
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
        }, status=status.HTTP_201_CREATED)

class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # We can't easily validate request data again here without consuming the stream or duplicating logic
        # But standard usage assumes email/password were valid if we got 200
        
        if response.status_code == 200:
            try:
                # TokenObtainPairView uses 'username' field by default (which we mapped to email?)
                # If your USERNAME_FIELD is 'username', request.data['username'] is expected.
                # If the client sends 'email', we might need to handle that. 
                # Assuming the client sends what Django expects (usually 'username' or configured USERNAME_FIELD).
                # If User model has USERNAME_FIELD='email', simplejwt expects 'email'.
                
                # Let's try to fetch the user to return their data
                email = request.data.get('email') or request.data.get('username')
                if email:
                    # If email is not the username field, we might need to filter by email
                    # But our User model uses AbstractUser, so username is the field, but we might have custom logic.
                    # Let's assume basic usage for now.
                    user = User.objects.filter(email=email).first() or User.objects.filter(username=email).first()
                    if user:
                        response.data['user'] = UserSerializer(user).data
            except Exception:
                pass
                
        return response

class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

class RequestPhoneVerificationView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.phone_verified:
            return Response({"message": "Phone number is already verified"}, status=status.HTTP_400_BAD_REQUEST)

        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        user.phone_verification_code = code
        user.phone_verification_expires = timezone.now() + timedelta(minutes=15)
        user.save()

        return Response({
            "message": f"Verification code sent to {user.phone_number}",
            "code": code
        })

class ConfirmPhoneVerificationView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        user = request.user

        if not user.phone_verification_code:
            return Response({"error": "No verification code requested"}, status=status.HTTP_400_BAD_REQUEST)

        if user.phone_verification_expires and user.phone_verification_expires < timezone.now():
            return Response({"error": "Verification code has expired"}, status=status.HTTP_400_BAD_REQUEST)

        if user.phone_verification_code == code:
            user.phone_verified = True
            user.phone_verification_code = None
            user.phone_verification_expires = None
            user.save()
            return Response({"message": "Phone number verified successfully"})

        return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        token = secrets.token_urlsafe(32)
        user.password_reset_token = token
        user.password_reset_expires = timezone.now() + timedelta(hours=1)
        user.save()

        send_password_reset_email(user, token)

        return Response({
            "message": f"Password reset instructions sent to {email}",
            "token": token
        })

class PasswordResetConfirmView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        new_password = serializer.validated_data['new_password']

        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.save()

        return Response({"message": "Password has been reset successfully"})

class ChangePasswordView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        new_password = serializer.validated_data['new_password']

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully"})

class RequestEmailVerificationView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.email_verified:
            return Response({"message": "Email is already verified"}, status=status.HTTP_400_BAD_REQUEST)

        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        user.email_verification_code = code
        user.email_verification_expires = timezone.now() + timedelta(minutes=15)
        user.save()

        send_email_verification_email(user, code)

        return Response({
            "message": f"Verification code sent to {user.email}",
            "code": code
        })

class ConfirmEmailVerificationView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EmailVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']
        user = request.user

        if not user.email_verification_code:
            return Response({"error": "No verification code requested"}, status=status.HTTP_400_BAD_REQUEST)

        if user.email_verification_expires and user.email_verification_expires < timezone.now():
            return Response({"error": "Verification code has expired"}, status=status.HTTP_400_BAD_REQUEST)

        if user.email_verification_code == code:
            user.email_verified = True
            user.email_verification_code = None
            user.email_verification_expires = None
            user.save()
            return Response({"message": "Email verified successfully"})

        return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
