"""
Utilities for view construction and views which don"t fit into any other app.
"""

from django.conf import settings
from django.views.generic import TemplateView

from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from config.openapi import openapi_schema
from backend.utils.openapi import load_openapi_schema


class OpenAPISchemaView(APIView):
    """
    Return the OpenAPI schema.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    renderer_classes = (JSONRenderer,)

    def get(self, request):
        return Response(
            data=openapi_schema if not settings.DEBUG else load_openapi_schema(),
            content_type="application/openapi+json; charset=utf-8",
        )


class ReDocView(TemplateView):
    """
    Render the ReDoc UI for the OpenAPI schema.
    """

    template_name = "redoc/redoc.html"
    schema_view_name = settings.OPENAPI_SCHEMA_VIEW_NAME
    page_title = "diet-assistant API"
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["schema_view_name"] = self.schema_view_name
        context["page_title"] = self.page_title
        return context
