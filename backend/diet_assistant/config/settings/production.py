"""
Production settings for diet-assistant project.

- Use Redis for cache
- Use sentry for error logging
"""
import sentry_sdk

from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Raises ImproperlyConfigured exception if DJANGO_SECRET_KEY not in os.environ
SECRET_KEY = env("DJANGO_SECRET_KEY")


# DATABASES
# ------------------------------------------------------------------------------
DATABASES["default"]["ENGINE"] = "django_prometheus.db.backends.postgresql"


API_MIDDLEWARE = []
PROMETHEUS_MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]
MIDDLEWARE = (
    [PROMETHEUS_MIDDLEWARE[0]]
    + API_MIDDLEWARE
    + MIDDLEWARE
    + [PROMETHEUS_MIDDLEWARE[1]]
)


# SENTRY SDK CLIENT
# ------------------------------------------------------------------------------
# Senty DNS is taken from SENTRY_DSN environment variable
# https://sentry.io/for/django/
# https://sentry.io/for/celery/
# https://docs.sentry.io/platforms/python/logging/
SENTRY_ENVIRONMENT = env("SENTRY_ENVIRONMENT", default="production")

# https://docs.sentry.io/workflow/releases/?platform=python
SENTRY_RELEASE = f"diet_assistant@{APP_VERSION}"

SENTRY_DSN = env("SENTRY_DSN", default="")
SENTRY_SAMPLE_RATE = 1.0

sentry_sdk.init(
    release=SENTRY_RELEASE,
    environment=SENTRY_ENVIRONMENT,
    integrations=[  # fmt: off
        DjangoIntegration(),  # fmt: off
        CeleryIntegration(),  # fmt: off
    ],  # fmt: off
    dsn=SENTRY_DSN,
    traces_sample_rate=SENTRY_SAMPLE_RATE,
)


# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
# TODO: set this to 60 seconds first and then to 518400 once you prove the former works
SECURE_HSTS_SECONDS = 60
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
)
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-preload
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True
)
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"


# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
# END SITE CONFIGURATION

INSTALLED_APPS += ["gunicorn", "django_prometheus"]

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = ("rest_framework.renderers.JSONRenderer",)


# TEMPLATES
# ------------------------------------------------------------------------------
# Keep templates in memory so tests run faster.
# See:
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
TEMPLATES[0]["OPTIONS"]["loaders"] = [
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]


# https://github.com/django/django/blob/4.1/django/utils/log.py
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {"handlers": ["console", "mail_admins"], "level": "INFO"},
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


# URLs
# ------------------------------------------------------------------------------
# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = env("DJANGO_ADMIN_URL", default="admin")


# STORAGES
# ------------------------------------------------------------------------------
# https://django-storages.readthedocs.io/en/latest/#installation
INSTALLED_APPS += ["storages"]  # noqa F405

# STATIC
# ------------------------------------------------------------------------------
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# MEDIA
# ------------------------------------------------------------------------------
# DEFAULT_FILE_STORAGE = "config.storages.MediaRootS3Boto3Storage"

# DJANGO PROMETHEUS
# ------------------------------------------------------------------------------
PROMETHEUS_EXPORT_MIGRATIONS = (
    False  # if set to True Prometheus will monitor total number of applied and
)
# unapplied migrations by connection


# CORS
# ------------------------------------------------------------------------------
CORS_ORIGIN_WHITELIST = env.list("CORS_ORIGIN_WHITELIST")
CSRF_TRUSTED_ORIGINS = CORS_ORIGIN_WHITELIST


# Your production stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------
