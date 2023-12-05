"""
Base settings for diet-assistant project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
import pathlib
import ssl
import urllib.parse

from typing import Optional, Tuple

import dj_database_url
import environs


class RedisUrlRequiredError(ValueError):
    pass


class RedisDbNumberValueError(ValueError):
    pass


class RedisUrlValueError(ValueError):
    pass


def parse_redis_url(url: str) -> Tuple[str, Optional[int], bool]:
    """
    Parse and validate a redis url. Returns the base url and the db number. The latter
    can be None if the url doesn't contain it.

    Raises ValueError if the url format is invalid.
    """
    try:
        parse_result = urllib.parse.urlparse(url)
    except ValueError as e:
        raise RedisUrlValueError(
            f"Redis url can not be parsed: {str(e)}\nHint: parsing will fail if url "
            "contains unescaped HTTP basic auth values, you can use urllib.parse.quote "
            "to encode them to url safe values"
        )
    if parse_result.scheme not in ("redis", "rediss"):
        raise RedisUrlRequiredError(
            "Redis url must use the redis:// or rediss:// scheme"
        )
    if not parse_result.path:  # no db number
        base_url, db_number = url, None
    else:
        db_number_str = parse_result.path.replace("/", "")
        try:
            db_number = int(db_number_str)
        except ValueError:
            raise RedisDbNumberValueError(
                f"The redis db number must be an integer between 0 and 9, "
                f"instead got '{db_number_str}'"
            )
        base_url = urllib.parse.urlunparse(
            (parse_result.scheme, parse_result.netloc, "", "", "", "")
        )
    use_ssl = parse_result.scheme == "rediss"
    return base_url, db_number, use_ssl


# ./diet_assistant/diet_assistant
APPS_DIR = pathlib.Path(__file__).parents[2]

# Load operating system environment variables and then prepare to use them
env = environs.Env()

# APPLICATION VERSION
# ------------------------------------------------------------------------------
APP_VERSION = "unknown"
APP_VERSION_FILE = APPS_DIR / ".appversion"
if APP_VERSION_FILE.exists():
    APP_VERSION = APP_VERSION_FILE.read_text().strip()


# GIT COMMIT
# ------------------------------------------------------------------------------
GIT_COMMIT = "unknown"
GIT_COMMIT_FILE = APPS_DIR / ".gitcommit"
if GIT_COMMIT_FILE.exists():
    GIT_COMMIT = GIT_COMMIT_FILE.read_text().strip()

# APP
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    # Default Django apps:
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.admin",
]

THIRD_PARTY_APPS = [
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.contrib.psutil",
    # "health_check.contrib.celery",  # create simple task in all queues and wait 3sec
    # "health_check.storage",  # save and delete file in storage
    # "health_check.contrib.s3boto_storage",  # requires boto and S3BotoStorage backend
    # "health_check.contrib.rabbitmq",  # requires RabbitMQ broker
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
]

# Apps specific for this project go here.
LOCAL_APPS = [
    # Custom users app
    "diet_assistant.users.apps.UsersConfig",
    # Your stuff: custom apps go here
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# MIDDLEWARES
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "diet_assistant.utils.middleware.VersionMiddleware",
]


# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)


# FIXTURES
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (APPS_DIR / "shared" / "fixtures",)

# DATABASES
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
# Uses django-environ to accept uri format
# See: https://django-environ.readthedocs.io/en/latest/#supported-types
# This is how Heroku passes the database url by default
DB_CONFIG_URL = env.str("DATABASE_URL", default=None)
if DB_CONFIG_URL is None:
    # Assume we're using Postgres and read the DB URL in parts
    DB_USER = env("POSTGRES_USER")
    DB_PASSWORD = env("POSTGRES_PASSWORD")
    DB_PORT = env("POSTGRES_PORT")
    DB_NAME = env("POSTGRES_DB")
    DB_HOST = env("POSTGRES_HOST")
    DB_CONFIG_URL = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DB_CONN_MAX_AGE = env.int("CONN_MAX_AGE", default=60)
DATABASES = {
    "default": dj_database_url.parse(DB_CONFIG_URL, conn_max_age=DB_CONN_MAX_AGE)
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

# CACHING
# ------------------------------------------------------------------------------

# Heroku URL does not pass the DB number, so we parse it in
REDIS_URL = env.str("REDIS_URL")
REDIS_BASE_URL, CACHE_REDIS_DB, _ = parse_redis_url(REDIS_URL)
if CACHE_REDIS_DB is None:
    CACHE_REDIS_DB = env.int("CACHE_REDIS_DB", default=0)
CACHE_REDIS_LOCATION = f"{REDIS_BASE_URL}/{CACHE_REDIS_DB}"

# Heroku URL does not pass the DB number, so we parse it in
CACHES = {
    "default": {
        "BACKEND": "django_prometheus.cache.backends.redis.RedisCache",
        "LOCATION": CACHE_REDIS_LOCATION,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": False,
            # mimics memcache behavior.
            # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
        },
    }
}

# GENERAL
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "UTC"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
# END SITE CONFIGURATION


# TEMPLATES
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": [APPS_DIR / "shared" / "templates"],
        "OPTIONS": {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            "debug": DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                # Your stuff: custom template context processors go here
            ],
        },
    }
]


# STATIC
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = APPS_DIR / "staticfiles"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [APPS_DIR / "shared" / "static"]

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


# MEDIA
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
# This is just a folder inside the container in local mode, where we mount a volume
# In production, this isn't used by django-storages, but needs to be set, as otherwise
# the static() helper throws an error, even though it doesn't actually do anything
# with DEBUG=false
MEDIA_ROOT = "/media/"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"


# URLs
# ------------------------------------------------------------------------------
ROOT_URLCONF = "config.urls"
# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = r"admin/"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"


# PASSWORD HASHING
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]


# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# AUTHENTICATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [  # fmt: off
    "django.contrib.auth.backends.ModelBackend",  # fmt: off
]  # fmt: off

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "users:redirect"
LOGIN_URL = "account_login"


# SLUGIFIER
# ------------------------------------------------------------------------------
AUTOSLUG_SLUGIFY_FUNCTION = "slugify.slugify"


# CELERY
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["diet_assistant.taskapp.celery.CeleryConfig"]

if USE_TZ:
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-timezone
    CELERY_TIMEZONE = TIME_ZONE
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ["json"]
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERYD_TASK_TIME_LIMIT = 5 * 60
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-soft-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERYD_TASK_SOFT_TIME_LIMIT = 60

# If using Redis as the Celery broker, we need to check and set the SSL options
if CELERY_BROKER_URL.startswith("redis"):
    _, _, celery_broker_use_ssl = parse_redis_url(CELERY_BROKER_URL)
    if celery_broker_use_ssl:
        # https://docs.celeryq.dev/en/latest/userguide/configuration.html#broker-use-ssl
        BROKER_USE_SSL = {"ssl_cert_reqs": ssl.CERT_NONE}
        # https://docs.celeryq.dev/en/latest/userguide/configuration.html#redis-backend-use-ssl
        CELERY_REDIS_BACKEND_USE_SSL = {"ssl_cert_reqs": ssl.CERT_NONE}


# DJANGO REST FRAMEWORK
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "config.authentication.BearerAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
    "SEARCH_PARAM": "search",
    "ORDERING_PARAM": "ordering",
    "COERCE_DECIMAL_TO_STRING": True,
    "UNAUTHENTICATED_USER": None,
    "EXCEPTION_HANDLER": "diet_assistant.utils.exceptions.handlers.drf_error_handler",
}

# OpenAPI Schema location
OPENAPI_SCHEMA_DIR = APPS_DIR / "schema"
OPENAPI_SCHEMA_FILENAME = "schema.yml"
OPENAPI_SCHEMA_URL = "docs/swagger.json"
OPENAPI_SCHEMA_VIEW_NAME = "openapi-schema-json"

# Your common stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------
