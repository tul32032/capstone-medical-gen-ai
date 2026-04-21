from types import SimpleNamespace
from unittest.mock import patch

import jwt
import pytest
from django.http import HttpResponse
from rest_framework.exceptions import AuthenticationFailed

from authentication.backends import JWTCookieAuthentication
from authentication.constants import ACCESS_TOKEN_COOKIE
from authentication.middleware import JWTRefreshCookieMiddleware
from authentication.models import User
from authentication.utils import generate_tokens_for_user


def test_authenticate_returns_none_without_cookie():
    backend = JWTCookieAuthentication()
    request = SimpleNamespace(COOKIES={})

    assert backend.authenticate(request) is None


def test_authenticate_returns_user_for_valid_cookie():
    user = User.objects.create_user(
        username="cookieuser",
        email="cookie@example.com",
        password="password123",
    )
    access_token, _ = generate_tokens_for_user(user)
    request = SimpleNamespace(COOKIES={ACCESS_TOKEN_COOKIE: str(access_token)})

    authenticated_user, token = JWTCookieAuthentication().authenticate(request)

    assert authenticated_user == user
    assert int(token["user_id"]) == user.id


def test_try_refresh_rejects_invalid_payload():
    request = SimpleNamespace()

    with pytest.raises(AuthenticationFailed, match="Invalid token"):
        JWTCookieAuthentication()._try_refresh(request, "not-a-token")


def test_try_refresh_requires_google_refresh_token():
    user = User.objects.create_user(
        username="expired",
        email="expired@example.com",
        password="password123",
    )
    expired_token = jwt.encode({"user_id": user.id}, "unused-secret", algorithm="HS256")
    request = SimpleNamespace()

    with pytest.raises(AuthenticationFailed, match="Session expired"):
        JWTCookieAuthentication()._try_refresh(request, expired_token)


def test_try_refresh_clears_stale_google_refresh_token():
    user = User.objects.create_user(
        username="refreshfail",
        email="refreshfail@example.com",
        password="password123",
        google_refresh_token="old-refresh-token",
    )
    expired_token = jwt.encode({"user_id": user.id}, "unused-secret", algorithm="HS256")
    request = SimpleNamespace()

    with patch(
        "authentication.backends.google_refresh_access_token",
        side_effect=Exception("refresh failed"),
    ):
        with pytest.raises(AuthenticationFailed, match="Session expired"):
            JWTCookieAuthentication()._try_refresh(request, expired_token)

    user.refresh_from_db()
    assert user.google_refresh_token is None


def test_try_refresh_issues_new_access_token_and_updates_profile():
    user = User.objects.create_user(
        username="refreshok",
        email="refreshok@example.com",
        password="password123",
        first_name="Old",
        last_name="Name",
        google_refresh_token="refresh-token",
    )
    expired_token = jwt.encode({"user_id": user.id}, "unused-secret", algorithm="HS256")
    request = SimpleNamespace()
    fresh_access_token, _ = generate_tokens_for_user(user)

    with (
        patch(
            "authentication.backends.google_refresh_access_token",
            return_value="google-access-token",
        ),
        patch(
            "authentication.backends.google_get_user_info",
            return_value={"given_name": "New", "family_name": "Surname"},
        ),
        patch(
            "authentication.backends.generate_tokens_for_user",
            return_value=(fresh_access_token, None),
        ),
    ):
        authenticated_user, token = JWTCookieAuthentication()._try_refresh(
            request,
            expired_token,
        )

    user.refresh_from_db()

    assert authenticated_user == user
    assert int(token["user_id"]) == user.id
    assert request._new_access_token == str(fresh_access_token)
    assert user.first_name == "New"
    assert user.last_name == "Surname"


def test_middleware_sets_new_access_cookie():
    request = SimpleNamespace(_new_access_token="fresh-token")
    middleware = JWTRefreshCookieMiddleware(lambda _: HttpResponse("ok"))

    response = middleware(request)

    assert response.cookies["access_token"].value == "fresh-token"


def test_middleware_leaves_response_unchanged_without_new_token():
    request = SimpleNamespace()
    middleware = JWTRefreshCookieMiddleware(lambda _: HttpResponse("ok"))

    response = middleware(request)

    assert "access_token" not in response.cookies
