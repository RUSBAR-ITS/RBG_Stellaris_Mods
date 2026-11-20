"""Validate the parser's bundled schemas without network retrieval."""

from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry

from document_package.errors import BuildError
from document_package.json_io import read_json

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "config"


@lru_cache
def validator(name):
    schema = read_json(ROOT / 'schemas' / name)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, registry=Registry())


def validate_schema(value, name):
    error = next(validator(name).iter_errors(value), None)
    if error:
        path = '.'.join(map(str, error.absolute_path)) or '$'
        raise BuildError('schema_error', f'{path}: {error.message}', field_path=path)
