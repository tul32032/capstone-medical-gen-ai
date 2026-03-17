from django.urls import path
from .views import GoogleLoginApi, MeApi, Logout

urlpatterns = [
    path("auth/login/google/", GoogleLoginApi.as_view(), name="login-with-google"),
    path("auth/me/", MeApi.as_view(), name="me"),
    path("auth/logout/", Logout.as_view(), name="logout"),
]
