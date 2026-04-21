from unittest.mock import patch

from django.core.exceptions import ValidationError
from rest_framework import exceptions as rest_exceptions
from rest_framework.test import APIRequestFactory
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.mixins import ApiAuthMixin, ApiErrorsMixin, PublicApiMixin
from authentication.models import User
from main import main


class ErrorView(ApiErrorsMixin, APIView):
    def get(self, request):
        return Response({"ok": True})


def build_view():
    view = ErrorView()
    factory = APIRequestFactory()
    view.request = view.initialize_request(factory.get("/"))
    view.headers = {}
    return view


def test_api_auth_and_public_mixins_expose_expected_classes():
    assert ApiAuthMixin.authentication_classes
    assert ApiAuthMixin.permission_classes
    assert PublicApiMixin.authentication_classes == ()
    assert PublicApiMixin.permission_classes == ()


def test_api_errors_mixin_translates_validation_error():
    view = build_view()

    response = view.handle_exception(ValidationError("bad input"))

    assert response.status_code == 400
    assert "bad input" in str(response.data)


def test_api_errors_mixin_passes_through_drf_exceptions():
    view = build_view()

    response = view.handle_exception(rest_exceptions.NotFound("missing"))

    assert response.status_code == 404


def test_api_errors_mixin_maps_user_does_not_exist():
    view = build_view()

    response = view.handle_exception(User.DoesNotExist("missing user"))

    assert response.status_code == 403
    assert "missing user" in str(response.data)


def test_main_prints_expected_message():
    with patch("builtins.print") as mock_print:
        main()

    mock_print.assert_called_once_with("Hello from server!")
