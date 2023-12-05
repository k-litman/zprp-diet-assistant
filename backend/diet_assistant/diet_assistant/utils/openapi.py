"""
OpenAPI utilities.
"""
import pathlib

from django.conf import settings

from prance import ResolvingParser


def load_openapi_schema(
    schema_dir_path: str = None, schema_filename: str = None
) -> dict:
    """
    Load a YAML-formatted OpenAPI schema.
    """
    schema_dir_path = schema_dir_path or str(settings.OPENAPI_SCHEMA_DIR)
    schema_filename = schema_filename or settings.OPENAPI_SCHEMA_FILENAME
    schema_filepath = pathlib.Path(schema_dir_path) / schema_filename

    parser = ResolvingParser(str(schema_filepath), backend="openapi-spec-validator")
    return parser.specification
