"""
Test the global error handlers here. We change the templates for these for
non-DRF projects, and DRF project should probably set their own. These tests
also sanity-check whether the middleware stack and apps are configured correctly.
"""

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404
from django.test.client import Client
from django.urls import path

import pytest

from config.urls import handler400, handler403, handler404, handler500  # noqa
from config.urls import urlpatterns as existing_urlpatterns

pytestmark = pytest.mark.urls("tests.test_handlers")


def internal_error_view(request):
    raise Exception


def not_found_view(request):
    raise Http404


def forbidden_view(request):
    raise PermissionDenied


def bad_request_view(request):
    raise SuspiciousOperation


# We use a custom urlconf because we need to use custom views for these tests, and
# we also need to test the whole Django stack rather than the view in isolation
urlpatterns = existing_urlpatterns + [
    path("500_error", internal_error_view),
    path("404_error", not_found_view),
    path("403_error", forbidden_view),
    path("400_error", bad_request_view),
]


@pytest.mark.django_db
def test_500_handler():
    client = Client(raise_request_exception=False)
    response = client.get("/500_error")
    assert response.status_code == 500
    assert response.json() == {
        "code": "SERVER_ERROR",
        "detail": ["Internal Server Error"],
    }


@pytest.mark.django_db
def test_404_handler(client):
    response = client.get("/404_error")
    assert response.status_code == 404
    assert response.json() == {"code": "NOT_FOUND", "detail": ["Not Found"]}


@pytest.mark.django_db
def test_403_handler(client):
    response = client.get("/403_error")
    assert response.status_code == 403
    assert response.json() == {
        "code": "PERMISSION_DENIED",
        "detail": ["You do not have permission to perform this action"],
    }


@pytest.mark.django_db
def test_400_handler(client):
    response = client.get("/400_error")
    assert response.status_code == 400
    assert response.json() == {"code": "INVALID_REQUEST", "detail": ["Invalid Request"]}
