from django.urls import path
from .views import GoogleLoginApi, EmailSignupApi, EmailLoginApi, MeApi, Logout

urlpatterns = [
    path("auth/login/google/", GoogleLoginApi.as_view(), name="login-with-google"),
    path("auth/signup/email/", EmailSignupApi.as_view(), name="signup-with-email"),
    path("auth/login/email/", EmailLoginApi.as_view(), name="login-with-email"),
    path("auth/me/", MeApi.as_view(), name="me"),
    path("auth/logout/", Logout.as_view(), name="logout"),
]
