import json

from django.utils.functional import cached_property

from rest_framework.exceptions import APIException

from .codes import ErrorCode


class DomainAPIErrorMeta(type):
    """
    Metaclass for DomainError subclasses. Ensures that the 'error_code' attribute
    is provided for new classes and that it's an instance of ErrorCode.
    """

    _classes_by_codes = {}

    def __new__(mcs, name, bases, attrs):
        new_cls = super(DomainAPIErrorMeta, mcs).__new__(mcs, name, bases, attrs)
        if attrs.get("error_code") is None:
            raise TypeError(
                "Domain error classes must have an error_code attribute defined"
            )

        if not isinstance(new_cls.error_code, ErrorCode):
            raise TypeError(
                "error_code must be an instance of diet_assistant.utils.exceptions.codes.ErrorCode"
            )

        if new_cls.error_code in mcs._classes_by_codes:
            if not (mcs._classes_by_codes[new_cls.error_code] is new_cls):
                raise TypeError(
                    "Another class with this error_code already exists: {}".format(
                        mcs._classes_by_codes[new_cls.error_code]
                    )
                )

        # Map error_code to class. Used in tests for catching specific errors classes.
        mcs._classes_by_codes[new_cls.error_code] = new_cls

        return new_cls

    def __getitem__(cls, error_code):
        """
        Return class with the provided error_code. If not found, `None` is returned.
        Useful for tests, where we want to map error_codes returned from API to concrete
        exceptions.
        >>> class BarError(DomainAPIError):
        ...     error_code = ErrorCode.THROTTLED
        >>> DomainAPIError['THROTTLED'] is BarError
        True
        >>> DomainAPIError['UNKNOWN'] is None
        True
        """
        return cls._classes_by_codes.get(error_code)


class DomainAPIError(APIException, metaclass=DomainAPIErrorMeta):
    """
    A domain-specific API error than can be raised in any view. This gets detected
    by our own exception handler and the resulting response JSON will
    receive additional attributes that allow the app to easily reason about
    what actually happened.
    Subclasses are required to set an 'error_code' class attribute that must be
    an instance of diet_assistant.utils.exceptions.codes.ErrorCode.
    This conversion is performed only once, when the class is first defined.
    """

    error_code = ErrorCode.INVALID_REQUEST
    status_code = 400
    default_detail = "Invalid request"

    def __init__(self, detail=None, code=None, **kwargs):
        super().__init__(detail, code)
        self._extra = {key: value for key, value in kwargs.items() if value}

    def get_codes(self):
        return self.error_code

    @cached_property
    def extra(self):
        """
        Dict for passing extra data to the response.
        This can be anything, as long as it's serializable.
        """

        return self._extra

    def __repr__(self):
        return "{0} {1}".format(
            self.__class__.__name__, json.dumps(self.get_full_details())
        )
