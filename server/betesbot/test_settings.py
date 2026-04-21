from .settings import *  # noqa: F403


SECRET_KEY = SECRET_KEY or "test-secret-key"
DEBUG = True
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",  # noqa: F405
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

GOOGLE_OAUTH2_CLIENT_ID = "test-client-id"
GOOGLE_OAUTH2_CLIENT_SECRET = "test-client-secret"
BASE_FRONTEND_URL = "http://testserver"
