"""
Tests for endpoints belonging to no particular app. These are mostly sanity
checks to ensure the configuration is correct.
"""

from django.conf import settings
from django.urls import reverse

import pytest


@pytest.mark.django_db
def test_health_check(client):
    view_name = "health_check:health_check_home"
    url = reverse(view_name)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_openapi_spec_endpoint(client):
    view_name = settings.OPENAPI_SCHEMA_VIEW_NAME
    url = reverse(view_name)
    response = client.get(url, format="json")
    assert response.status_code == 200
    assert isinstance(response.data, dict)
    assert "openapi" in response.data


@pytest.mark.django_db
def test_redoc_view(client):
    view_name = "redoc"
    url = reverse(view_name)
    response = client.get(url)
    assert response.status_code == 200
