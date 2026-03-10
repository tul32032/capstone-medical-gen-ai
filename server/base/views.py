import os
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

_secure = os.environ.get("DEBUG", "False") != "True"
COOKIE_SETTINGS = {
    "httponly": True,
    "secure": _secure,
    "samesite": "None" if _secure else "Lax",
    "path": "/",
}


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"success": False, "detail": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"success": False, "detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = authenticate(request, username=user.username, password=password)
        if user is None:
            return Response(
                {"success": False, "detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        res = Response({"success": True})
        res.set_cookie(
            key="access_token", value=str(refresh.access_token), **COOKIE_SETTINGS
        )
        res.set_cookie(key="refresh_token", value=str(refresh), **COOKIE_SETTINGS)
        return res


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get("refresh_token")

            if not refresh_token:
                return Response({"success": False, "detail": "No refresh token"})

            serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
            serializer.is_valid(raise_exception=True)
            tokens = serializer.validated_data

            res = Response({"success": True})
            res.set_cookie(
                key="access_token", value=tokens["access"], **COOKIE_SETTINGS
            )

            if "refresh" in tokens:
                res.set_cookie(
                    key="refresh_token", value=tokens["refresh"], **COOKIE_SETTINGS
                )

            return res

        except (TokenError, InvalidToken):
            return Response(
                {"success": False, "detail": "Invalid or expired refresh token"}
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except (TokenError, InvalidToken):
                pass

        res = Response({"success": True})
        res.delete_cookie("access_token", path="/")
        res.delete_cookie("refresh_token", path="/")
        return res


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"success": False, "detail": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"success": False, "detail": "Email already registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(username=email, email=email, password=password)
        refresh = RefreshToken.for_user(user)

        res = Response({"success": True}, status=status.HTTP_201_CREATED)
        res.set_cookie(
            key="access_token", value=str(refresh.access_token), **COOKIE_SETTINGS
        )
        res.set_cookie(key="refresh_token", value=str(refresh), **COOKIE_SETTINGS)
        return res


class TestAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"success": True, "user": request.user.username})
