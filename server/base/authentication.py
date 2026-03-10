from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


class CookiesJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")

        if not access_token:
            return None

        try:
            valid = self.get_validated_token(access_token)
            user = self.get_user(valid)
        except (TokenError, InvalidToken, Exception):
            return None

        return (user, valid)
