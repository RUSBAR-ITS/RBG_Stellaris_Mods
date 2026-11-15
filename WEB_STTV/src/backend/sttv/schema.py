"""JSON Schema validation without automatic remote schema retrieval."""

from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry

from .errors import BuildError
from .json_io import read_json

PRODUCT_ROOT = Path(__file__).resolve().parents[3]


def schema_validator(name):
    schema = read_json(PRODUCT_ROOT / "schemas" / name)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, registry=Registry())


def validate_schema(value, name):
    error = next(schema_validator(name).iter_errors(value), None)
    if error:
        path = ".".join(str(item) for item in error.absolute_path) or "$"
        raise BuildError("schema_error", f"{path}: {error.message}", field_path=path)
