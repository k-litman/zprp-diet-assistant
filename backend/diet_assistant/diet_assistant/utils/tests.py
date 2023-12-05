"""
Test for the utils app.
"""
import pytest

from django.core.exceptions import PermissionDenied
from django.http import Http404

from rest_framework import serializers
from diet_assistant.utils.exceptions.api_errors import DomainAPIError
from diet_assistant.utils.exceptions.handlers import drf_error_handler


@pytest.mark.parametrize(
    "exception,response_data",
    [
        (Http404(), {"code": "NOT_FOUND", "detail": ["Not found."]}),
        (
            PermissionDenied(),
            {
                "code": "PERMISSION_DENIED",
                "detail": ["You do not have permission to perform this action."],
            },
        ),
        (
            DomainAPIError("Error message"),
            {"code": "INVALID_REQUEST", "detail": ["Error message"]},
        ),
        (
            serializers.ValidationError(
                {
                    "field": ["Field error message"],
                    "non_field_errors": ["Non-field error message"],
                }
            ),
            {
                "code": "INVALID_REQUEST",
                "detail": {
                    "field": ["Field error message"],
                    "non_field_errors": ["Non-field error message"],
                },
            },
        ),
        (
            serializers.ValidationError(
                {
                    "field": ["Field error message"],
                    "nested": {
                        "nested_field": ["Nested field error message"],
                        "non_field_errors": ["Nested non-field error message"],
                    },
                    "non_field_errors": ["Non-field error message"],
                }
            ),
            {
                "code": "INVALID_REQUEST",
                "detail": {
                    "field": ["Field error message"],
                    "nested": {
                        "nested_field": ["Nested field error message"],
                        "non_field_errors": ["Nested non-field error message"],
                    },
                    "non_field_errors": ["Non-field error message"],
                },
            },
        ),
        (
            DomainAPIError(detail="Domain error"),
            {
                "code": "INVALID_REQUEST",
                "detail": ["Domain error"],
            },
        ),
    ],
)
def test_drf_error_handler(exception, response_data):
    response = drf_error_handler(exception, {})
    assert response.data == response_data
