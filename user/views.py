from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import api_view, permission_classes
from google.oauth2 import id_token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from utils.send_email import send_email
from .serializers import UserSerializer
import requests
import os

# Token generator for password reset
token_generator = PasswordResetTokenGenerator()

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = self.get_user(request.data["username"])
        user_serializer = UserSerializer(user)
        serialized_user = user_serializer.data

        return Response(
            {
                "refresh": response.data["refresh"],
                "access": response.data["access"],
                "user": serialized_user,
            }
        )

    def get_user(self, username):
        return User.objects.get(username=username)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # Decode the refresh token to get the user ID
        refresh_token = request.data.get("refresh")
        refresh = RefreshToken(refresh_token)
        user_id = refresh["user_id"]

        # Get the user
        user = User.objects.get(id=user_id)
        user_serializer = UserSerializer(user)
        serialized_user = user_serializer.data

        return Response({"access": response.data["access"], "user": serialized_user})


class SignupViewSet(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    http_method_names = ["post"]

    def create(self, request):
        recaptcha_response = request.data.get('g-recaptcha-response')
        if not recaptcha_response:
            return Response({"error": "reCAPTCHA token is missing."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify reCAPTCHA
        recaptcha_secret = os.getenv("RECAPTCHA_SECRET_KEY")
        recaptcha_verification_url = f"https://www.google.com/recaptcha/api/siteverify"
        verification_response = requests.post(recaptcha_verification_url, data={
            'secret': recaptcha_secret,
            'response': recaptcha_response
        })

        verification_result = verification_response.json()
        if not verification_result.get('success'):
            return Response({"error": "Invalid reCAPTCHA. Please try again."}, status=status.HTTP_400_BAD_REQUEST)

        # Proceed with user creation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(**serializer.validated_data)
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": serializer.data,
            },
            status=status.HTTP_201_CREATED
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def google_complete(request):
    client_id = os.getenv("GOOGLE_CLIENT_ID")

    token = request.data.get("token")

    if not token:
        return Response({"error": "Token is missing"}, status=400)

    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)

        email = idinfo["email"]
        first_name = idinfo.get("given_name", "")
        last_name = idinfo.get("family_name", "")

        user, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email, "first_name": first_name, "last_name": last_name},
        )

        if created:
            user.set_unusable_password()
            user.save()

        login(request, user)

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)

        user_serializer = UserSerializer(user)
        serialized_user = user_serializer.data

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": serialized_user,
            }
        )

    except ValueError:
        return Response({"error": "Invalid token"}, status=400)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_link(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

    # Generate password reset token and user encoded ID
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Construct the password reset link
    reset_link = f"{os.getenv('FRONTEND_URL')}/reset-password/{uid}/{token}/"

    # Send email with the reset link
    subject = "Password Reset Requested"
    message = f"Click the link below to reset your password:\n{reset_link}"

    send_email(subject, message, [email])

    return Response({"message": "Password reset link sent."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request, uidb64, token):
    new_password = request.data.get('new_password')

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        return Response({"error": "Invalid token or user ID."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if token is valid
    if not token_generator.check_token(user, token):
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

    # Set the new password for the user
    user.set_password(new_password)
    user.save()

    return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)