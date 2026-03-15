from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .mixins import PublicApiMixin, ApiErrorsMixin
from .utils import google_get_access_token, google_get_user_info, generate_tokens_for_user
from .models import User
from .serilizers import UserSerializer
from .constants import ACCESS_TOKEN_COOKIE, ACCESS_TOKEN_MAX_AGE


class GoogleLoginApi(PublicApiMixin, ApiErrorsMixin, APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=True)

    def post(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        code = input_serializer.validated_data['code']
        redirect_uri = f'{settings.BASE_FRONTEND_URL}/auth/callback'

        google_access_token, google_refresh_token = google_get_access_token(
            code=code,
            redirect_uri=redirect_uri,
        )
        user_data = google_get_user_info(access_token=google_access_token)

        try:
            user = User.objects.get(email=user_data['email'])
        except User.DoesNotExist:
            username = user_data['email'].split('@')[0]
            user = User.objects.create(
                username=username,
                email=user_data['email'],
                first_name=user_data.get('given_name', ''),
                last_name=user_data.get('family_name', ''),
                registration_method='google',
            )

        if google_refresh_token:
            user.google_refresh_token = google_refresh_token
            user.save(update_fields=['google_refresh_token'])

        access_token, _ = generate_tokens_for_user(user)

        response = Response({'user': UserSerializer(user).data})
        response.set_cookie(
            ACCESS_TOKEN_COOKIE,
            str(access_token),
            max_age=ACCESS_TOKEN_MAX_AGE,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
        )
        return response


class MeApi(ApiErrorsMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({'user': UserSerializer(request.user).data})
