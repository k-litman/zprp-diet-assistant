import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from diet_assistant.utils.views import OpenAPISchemaView, ReDocView
from diet_assistant.utils.exceptions import handlers

urlpatterns = [
    path("healthz/", include("health_check.urls")),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("diet_assistant.users.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path(
        settings.OPENAPI_SCHEMA_URL,
        OpenAPISchemaView.as_view(),
        name=settings.OPENAPI_SCHEMA_VIEW_NAME,
    ),
    path("docs/", ReDocView.as_view(), name="redoc"),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = handlers.bad_request
handler403 = handlers.permission_denied
handler404 = handlers.not_found
handler500 = handlers.server_error

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            handler400,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            handler403,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            handler404,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", handler500),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

if os.environ.get("DJANGO_SETTINGS_MODULE") == "config.settings.production":
    urlpatterns += [path("prometheus/", include("django_prometheus.urls"))]
