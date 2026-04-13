from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .mixins import PublicApiMixin, ApiAuthMixin, ApiErrorsMixin
from .utils import (
    google_get_access_token,
    google_get_user_info,
    generate_tokens_for_user,
)
from .models import User
from .serilizers import UserSerializer
from .constants import ACCESS_TOKEN_COOKIE, ACCESS_TOKEN_MAX_AGE


class GoogleLoginApi(PublicApiMixin, ApiErrorsMixin, APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=True)

    def post(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        code = input_serializer.validated_data["code"]
        redirect_uri = f"{settings.BASE_FRONTEND_URL}/auth/callback"

        google_access_token, google_refresh_token = google_get_access_token(
            code=code,
            redirect_uri=redirect_uri,
        )
        user_data = google_get_user_info(access_token=google_access_token)

        try:
            user = User.objects.get(email=user_data["email"])
        except User.DoesNotExist:
            username = user_data["email"].split("@")[0]
            user = User.objects.create(
                username=username,
                email=user_data["email"],
                first_name=user_data.get("given_name", ""),
                last_name=user_data.get("family_name", ""),
                registration_method="google",
            )

        if google_refresh_token:
            user.google_refresh_token = google_refresh_token
            user.save(update_fields=["google_refresh_token"])

        access_token, _ = generate_tokens_for_user(user)

        response = Response({"user": UserSerializer(user).data})
        response.set_cookie(
            ACCESS_TOKEN_COOKIE,
            str(access_token),
            max_age=ACCESS_TOKEN_MAX_AGE,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="None",
            partitioned=True,
        )
        return response


class EmailSignupApi(PublicApiMixin, ApiErrorsMixin, APIView):
    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField(required=True)
        password = serializers.CharField(required=True, min_length=8, write_only=True)
        first_name = serializers.CharField(required=False, default="")
        last_name = serializers.CharField(required=False, default="")

    def post(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        data = input_serializer.validated_data
        email = data["email"]

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "A user with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        username = email.split("@")[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=data["password"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            registration_method="email",
        )

        access_token, _ = generate_tokens_for_user(user)

        response = Response(
            {"user": UserSerializer(user).data}, status=status.HTTP_201_CREATED
        )
        response.set_cookie(
            ACCESS_TOKEN_COOKIE,
            str(access_token),
            max_age=ACCESS_TOKEN_MAX_AGE,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="None",
            partitioned=True,
        )
        return response


class EmailLoginApi(PublicApiMixin, ApiErrorsMixin, APIView):
    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField(required=True)
        password = serializers.CharField(required=True, write_only=True)

    def post(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        data = input_serializer.validated_data

        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(data["password"]):
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token, _ = generate_tokens_for_user(user)

        response = Response({"user": UserSerializer(user).data})
        response.set_cookie(
            ACCESS_TOKEN_COOKIE,
            str(access_token),
            max_age=ACCESS_TOKEN_MAX_AGE,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="None",
            partitioned=True,
        )
        return response


class MeApi(ApiAuthMixin, APIView):
    def get(self, request, *args, **kwargs):
        return Response({"user": UserSerializer(request.user).data})


class Logout(PublicApiMixin, ApiErrorsMixin, APIView):
    def post(self, request, *args, **kwargs):
        response = Response({"success": True})
        response.delete_cookie("access_token")
        return response
