"""
Test settings for diet-assistant project.

- Used to run tests fast on the continuous integration server and locally
"""

from .base import *  # noqa

# DEBUG
# ------------------------------------------------------------------------------
# Turn debug off so tests run faster
DEBUG = False

# This needs to be enabled if we want to use the coverage plugin for templates
TEMPLATES[0]["OPTIONS"]["debug"] = False


# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env("DJANGO_SECRET_KEY", default="CHANGEME!!!")


# EMAIL
# ------------------------------------------------------------------------------
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025

# In-memory email backend stores messages in django.core.mail.outbox
# for unit testing purposes
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


# CACHING
# ------------------------------------------------------------------------------
# Speed advantages of in-memory caching without having to run Memcached
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}


# TESTING
# ------------------------------------------------------------------------------
# TEST_RUNNER = 'django.test.runner.DiscoverRunner'
TEST_RUNNER = "config.runner.PytestTestRunner"


# CELERY
# This is provided even if you don't choose to use Celery, as the cost is negligible
# If you're confident you won't need it, feel free to remove.
# ------------------------------------------------------------------------------
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-always-eager
CELERY_TASK_ALWAYS_EAGER = True
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True


# PASSWORD HASHING
# ------------------------------------------------------------------------------
# Use fast password hasher so tests run faster
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


# TEMPLATES
# ------------------------------------------------------------------------------
# Keep templates in memory so tests run faster.
# See:
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
TEMPLATES[0]["OPTIONS"]["loaders"] = [
    [
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    ]
]
