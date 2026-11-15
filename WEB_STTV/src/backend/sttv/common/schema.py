"""JSON Schema validation without automatic remote schema retrieval."""

from .paths import PRODUCT_ROOT

from jsonschema import Draft202012Validator
from referencing import Registry

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json



def schema_validator(name):
    schema = read_json(PRODUCT_ROOT / "schemas" / name)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, registry=Registry())


def validate_schema(value, name):
    error = next(schema_validator(name).iter_errors(value), None)
    if error:
        path = ".".join(str(item) for item in error.absolute_path) or "$"
        raise BuildError("schema_error", f"{path}: {error.message}", field_path=path)
