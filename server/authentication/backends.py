import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import User
from .utils import google_refresh_access_token, google_get_user_info, generate_tokens_for_user
from .constants import ACCESS_TOKEN_COOKIE, ACCESS_TOKEN_MAX_AGE


class JWTCookieAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token_str = request.COOKIES.get(ACCESS_TOKEN_COOKIE)
        if not token_str:
            return None

        try:
            token = AccessToken(token_str)
            user = User.objects.get(id=token['user_id'])
            return (user, token)
        except TokenError:
            return self._try_refresh(request, token_str)

    def _try_refresh(self, request, expired_token_str):
        try:
            payload = jwt.decode(
                expired_token_str,
                options={"verify_signature": False},
            )
            user = User.objects.get(id=payload.get('user_id'))
        except (User.DoesNotExist, jwt.DecodeError):
            raise AuthenticationFailed('Invalid token. Please log in again.')

        if not user.google_refresh_token:
            raise AuthenticationFailed('Session expired. Please log in again.')

        try:
            google_access_token = google_refresh_access_token(
                refresh_token=user.google_refresh_token,
            )
        except Exception:
            # Google refresh token is expired or revoked, force re-login
            user.google_refresh_token = None
            user.save(update_fields=['google_refresh_token'])
            raise AuthenticationFailed('Session expired. Please log in again.')

        # Use the fresh Google access token to keep user profile up to date
        try:
            user_data = google_get_user_info(access_token=google_access_token)
            update_fields = []
            if user_data.get('given_name', '') != user.first_name:
                user.first_name = user_data.get('given_name', '')
                update_fields.append('first_name')
            if user_data.get('family_name', '') != user.last_name:
                user.last_name = user_data.get('family_name', '')
                update_fields.append('last_name')
            if update_fields:
                user.save(update_fields=update_fields)
        except Exception:
            pass

        # Google session is still valid, issue a new JWT
        new_access_token, _ = generate_tokens_for_user(user)
        new_token_str = str(new_access_token)

        # Attach to request so middleware can set the new cookie on the response
        request._new_access_token = new_token_str

        token_obj = AccessToken(new_token_str)
        return (user, token_obj)
