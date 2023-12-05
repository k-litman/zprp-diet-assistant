from typing import Dict, List, Optional, TypedDict, Union

from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, JsonResponse

from rest_framework import exceptions, serializers, status
from rest_framework.views import exception_handler as default_drf_error_handler

from .api_errors import DomainAPIError
from .codes import ErrorCode


class ErrorDict(TypedDict, total=False):
    messages: List[str]
    fields: Dict[str, Union["ErrorDict", List[str]]]


# Generic error handlers for Django
def server_error(request, *_args, **_kwargs):
    """
    Generic 500 error handler.
    """
    data = {"code": ErrorCode.SERVER_ERROR, "detail": ["Internal Server Error"]}
    return JsonResponse(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def bad_request(request, exception, *_args, **_kwargs):
    """
    Generic 400 error handler.
    """
    data = {"code": ErrorCode.INVALID_REQUEST, "detail": ["Invalid Request"]}
    return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


def permission_denied(request, exception, *_args, **_kwargs):
    """
    Generic 403 error handler.
    """
    data = {
        "code": ErrorCode.PERMISSION_DENIED,
        "detail": ["You do not have permission to perform this action"],
    }
    return JsonResponse(data, status=status.HTTP_403_FORBIDDEN)


def not_found(request, exception, *_args, **_kwargs):
    """
    Generic 404 error handler.
    """
    data = {"code": ErrorCode.NOT_FOUND, "detail": ["Not Found"]}
    return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)


def drf_error_handler(exc, context) -> Optional[HttpResponse]:
    """
    Returns the HTTP response that should be returned for any given exception. This is a
    modified DRF default error handler which structures the response a bit differently.

    In particular, it puts all the specific error messages into the `detail` key
    instead of dumping them into the top-level response dictionary like DRF's default.
    Every error response also has an explicit code - the codes are set up for built-in
    HTTP errors, and each DomainError subclass should have its own code.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    response = default_drf_error_handler(exc, context)
    if not response:
        return response

    # Change Django's built-in exceptions to DRF's ones
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    # Ensure that we're putting detail data for validation errors into the
    # "detail" key instead of dumping it into the top-level dict like the
    if isinstance(exc, serializers.ValidationError):
        response.data = {"detail": response.data}

    # Ensure `detail` is always either a list or a dictionary
    if isinstance(response.data["detail"], str):
        response.data["detail"] = [response.data["detail"]]

    # Add the `extra` dict for domain errors if it's defined
    if isinstance(exc, DomainAPIError) and exc.extra:
        response.data.update(extra=exc.extra)

    # Set the error code. If `get_codes()` returns a string, we use that uppercased
    # Otherwise default to INVALID_REQUEST
    codes = exc.get_codes()
    if isinstance(codes, str):
        error_code = ErrorCode(codes.upper())
    else:
        error_code = ErrorCode.INVALID_REQUEST
    response.data.update(code=error_code)
    return response
