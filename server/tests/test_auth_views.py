from unittest.mock import patch

from django.urls import reverse

from authentication.models import User
from tests.helpers import attach_access_cookie


def test_email_signup_creates_user_and_sets_cookie(client):
    url = reverse("signup-with-email")

    with patch("authentication.views.generate_tokens_for_user", return_value=("jwt-1", None)):
        response = client.post(
            url,
            data={
                "email": "newuser@example.com",
                "password": "password123",
                "first_name": "New",
                "last_name": "User",
            },
            content_type="application/json",
        )

    created_user = User.objects.get(email="newuser@example.com")

    assert response.status_code == 201
    assert created_user.username == "newuser"
    assert response.json()["user"]["email"] == "newuser@example.com"
    assert response.cookies["access_token"].value == "jwt-1"


def test_email_signup_deduplicates_username(client):
    User.objects.create_user(
        username="taken",
        email="taken@example.com",
        password="password123",
    )

    with patch("authentication.views.generate_tokens_for_user", return_value=("jwt-2", None)):
        response = client.post(
            reverse("signup-with-email"),
            data={
                "email": "taken@another.com",
                "password": "password123",
            },
            content_type="application/json",
        )

    assert response.status_code == 201
    assert User.objects.get(email="taken@another.com").username == "taken1"


def test_email_signup_rejects_duplicate_email(client):
    User.objects.create_user(
        username="dup",
        email="dup@example.com",
        password="password123",
    )

    response = client.post(
        reverse("signup-with-email"),
        data={
            "email": "dup@example.com",
            "password": "password123",
        },
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json()["error"] == "A user with this email already exists."


def test_email_login_returns_cookie_for_valid_credentials(client):
    User.objects.create_user(
        username="loginuser",
        email="login@example.com",
        password="password123",
    )

    with patch("authentication.views.generate_tokens_for_user", return_value=("jwt-3", None)):
        response = client.post(
            reverse("login-with-email"),
            data={
                "email": "login@example.com",
                "password": "password123",
            },
            content_type="application/json",
        )

    assert response.status_code == 200
    assert response.cookies["access_token"].value == "jwt-3"


def test_email_login_rejects_unknown_user(client):
    response = client.post(
        reverse("login-with-email"),
        data={
            "email": "missing@example.com",
            "password": "password123",
        },
        content_type="application/json",
    )

    assert response.status_code == 401
    assert response.json()["error"] == "Invalid email or password."


def test_google_login_creates_user_and_persists_refresh_token(client):
    url = reverse("login-with-google")

    with (
        patch(
            "authentication.views.google_get_access_token",
            return_value=("google-access", "google-refresh"),
        ),
        patch(
            "authentication.views.google_get_user_info",
            return_value={
                "email": "googleuser@example.com",
                "given_name": "Google",
                "family_name": "User",
            },
        ),
        patch("authentication.views.generate_tokens_for_user", return_value=("jwt-4", None)),
    ):
        response = client.post(
            url,
            data={"code": "google-auth-code"},
            content_type="application/json",
        )

    user = User.objects.get(email="googleuser@example.com")

    assert response.status_code == 200
    assert user.registration_method == "google"
    assert user.google_refresh_token == "google-refresh"
    assert response.cookies["access_token"].value == "jwt-4"


def test_google_login_reuses_existing_user(client):
    existing_user = User.objects.create_user(
        username="existing",
        email="existing@example.com",
        password="password123",
        first_name="Old",
    )

    with (
        patch(
            "authentication.views.google_get_access_token",
            return_value=("google-access", None),
        ),
        patch(
            "authentication.views.google_get_user_info",
            return_value={
                "email": "existing@example.com",
                "given_name": "Updated",
                "family_name": "Name",
            },
        ),
        patch("authentication.views.generate_tokens_for_user", return_value=("jwt-5", None)),
    ):
        response = client.post(
            reverse("login-with-google"),
            data={"code": "google-auth-code"},
            content_type="application/json",
        )

    existing_user.refresh_from_db()

    assert response.status_code == 200
    assert User.objects.count() == 1
    assert existing_user.google_refresh_token is None


def test_me_returns_current_user(client):
    user = User.objects.create_user(
        username="meuser",
        email="me@example.com",
        password="password123",
        first_name="Current",
    )
    attach_access_cookie(client, user)

    response = client.get(reverse("me"))

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "me@example.com"


def test_logout_clears_access_cookie(client):
    response = client.post(reverse("logout"))

    assert response.status_code == 200
    assert response.json() == {"success": True}
    assert response.cookies["access_token"].value == ""
