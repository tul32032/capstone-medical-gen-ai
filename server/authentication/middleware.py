from django.conf import settings
from .constants import ACCESS_TOKEN_COOKIE, ACCESS_TOKEN_MAX_AGE


class JWTRefreshCookieMiddleware:
    """
    After each request, if authentication silently issued a new JWT
    (because the old one was expired but the Google refresh token was valid),
    set the new token as an HttpOnly cookie on the response.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        new_token = getattr(request, '_new_access_token', None)
        if new_token:
            response.set_cookie(
                ACCESS_TOKEN_COOKIE,
                new_token,
                max_age=ACCESS_TOKEN_MAX_AGE,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
            )

        return response
