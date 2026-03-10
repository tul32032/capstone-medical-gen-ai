from django.urls import path
from .views import LoginView, CustomTokenRefreshView, LogoutView, SignupView, TestAuthView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("token/logout/", LogoutView.as_view(), name="logout"),
    path("test/", TestAuthView.as_view(), name="test_auth"),
]
