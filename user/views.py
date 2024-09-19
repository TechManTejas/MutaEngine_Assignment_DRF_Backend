from django.contrib.auth.models import User
from django.contrib.auth import login
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
import os


class SignupViewSet(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    http_method_names = ["post"]

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(**serializer.validated_data)
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": serializer.data,
            }
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
