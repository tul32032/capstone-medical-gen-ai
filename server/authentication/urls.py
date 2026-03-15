from django.urls import path
from .views import GoogleLoginApi, MeApi

urlpatterns = [
    path("auth/login/google/", GoogleLoginApi.as_view(), name="login-with-google"),
    path("auth/me/", MeApi.as_view(), name="me"),
]
