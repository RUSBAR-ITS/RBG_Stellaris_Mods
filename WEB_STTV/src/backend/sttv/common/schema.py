"""JSON Schema validation without automatic remote schema retrieval."""

from .paths import PRODUCT_ROOT

from jsonschema import Draft202012Validator
from referencing import Registry
from contextvars import ContextVar
from functools import wraps

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json

_session = ContextVar('sttv_schema_session', default=None)


class SchemaSession:
    def __init__(self):
        self.validators = {}
        self.database_rules = None


def schema_operation(function):
    @wraps(function)
    def execute(*args, **kwargs):
        if _session.get() is not None:
            return function(*args, **kwargs)
        token = _session.set(SchemaSession())
        try:
            return function(*args, **kwargs)
        finally:
            _session.reset(token)
    return execute


def current_session():
    return _session.get()


def schema_validator(name):
    session = _session.get()
    if session is not None and name in session.validators:
        return session.validators[name]
    schema = read_json(PRODUCT_ROOT / "schemas" / name)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, registry=Registry())
    if session is not None:
        session.validators[name] = validator
    return validator


def validate_schema(value, name):
    error = next(schema_validator(name).iter_errors(value), None)
    if error:
        path = ".".join(str(item) for item in error.absolute_path) or "$"
        raise BuildError("schema_error", f"{path}: {error.message}", field_path=path)
