Error handling
==============

We use a custom error handler defined in [the utils package]. We also have a base
exception class - `DomainError` - defined for exceptions which we want to directly
return to the client. Any type of error that should be returned to the client
and doesn't fit into any of the built-in classes (most notably, `ValidationError`),
should have its own exception class with a unique error code. For example:
```python
class UserInactive(DomainError):
    error_code = ErrorCode.USER_INACTIVE
    default_detail = "User is inactive"
```

For more details, see [the exception module].


[the utils package]: ../diet_assistant/diet_assistant/utils/exceptions/handlers.py
[the exception module]: ../diet_assistant/diet_assistant/utils/exceptions/api_errors.py
