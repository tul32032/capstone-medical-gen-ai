from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from authentication import utils


class MessageError(Exception):
    def __init__(self, message):
        self.message = message


def test_get_error_message_prefers_message_attribute():
    assert utils.get_error_message(MessageError("boom")) == "boom"


def test_get_error_message_falls_back_to_string():
    assert utils.get_error_message(ValueError("plain error")) == "plain error"


@patch("authentication.utils.requests.post")
def test_google_get_access_token_returns_access_and_refresh_tokens(mock_post):
    mock_post.return_value = SimpleNamespace(
        ok=True,
        json=lambda: {"access_token": "access-123", "refresh_token": "refresh-456"},
    )

    access_token, refresh_token = utils.google_get_access_token(
        code="auth-code",
        redirect_uri="http://testserver/auth/callback",
    )

    assert access_token == "access-123"
    assert refresh_token == "refresh-456"
    assert mock_post.call_args.kwargs["data"]["code"] == "auth-code"


@patch("authentication.utils.requests.post")
def test_google_get_access_token_raises_when_google_rejects_request(mock_post):
    mock_post.return_value = SimpleNamespace(ok=False)

    with pytest.raises(ValidationError, match="Failed to obtain access token"):
        utils.google_get_access_token(
            code="bad-code",
            redirect_uri="http://testserver/auth/callback",
        )


@patch("authentication.utils.requests.post")
def test_google_refresh_access_token_returns_new_token(mock_post):
    mock_post.return_value = SimpleNamespace(
        ok=True,
        json=lambda: {"access_token": "new-access-token"},
    )

    assert (
        utils.google_refresh_access_token(refresh_token="refresh-123")
        == "new-access-token"
    )


@patch("authentication.utils.requests.post")
def test_google_refresh_access_token_raises_for_invalid_refresh_token(mock_post):
    mock_post.return_value = SimpleNamespace(ok=False)

    with pytest.raises(ValidationError, match="invalid or expired"):
        utils.google_refresh_access_token(refresh_token="expired-token")


@patch("authentication.utils.requests.get")
def test_google_get_user_info_returns_payload(mock_get):
    mock_get.return_value = SimpleNamespace(
        ok=True,
        json=lambda: {"email": "user@example.com"},
    )

    assert utils.google_get_user_info(access_token="token") == {
        "email": "user@example.com"
    }


@patch("authentication.utils.requests.get")
def test_google_get_user_info_raises_when_request_fails(mock_get):
    mock_get.return_value = SimpleNamespace(ok=False)

    with pytest.raises(ValidationError, match="Failed to obtain user info"):
        utils.google_get_user_info(access_token="bad-token")
