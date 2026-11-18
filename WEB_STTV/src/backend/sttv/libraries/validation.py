"""Prepare library schema checks with direct dispatch on serialized class names."""

from sttv.common.errors import BuildError
from sttv.common.schema import schema_validator, current_session
from sttv.database.checks.compiler import Compiler


class LibraryCompiler(Compiler):
    def build(self, schema):
        variants = schema.get('anyOf', [])
        names = [item.get('properties', {}).get('type', {}).get('const') for item in variants]
        if names and all(isinstance(name, str) for name in names) and len(set(names)) == len(names):
            checks = {name: self.prepare(item) for name, item in zip(names, variants)}
            common = super().build({key: value for key, value in schema.items() if key != 'anyOf'})

            def dispatch(value, path, context):
                common(value, path, context)
                name = value.get('type') if isinstance(value, dict) else None
                check = checks.get(name) if isinstance(name, str) else None
                if check is None:
                    raise BuildError('library_object_type', f'Unknown prepared record at {path}')
                check(value, path, context)
            return dispatch
        return super().build(schema)


def artifact_validator():
    session = current_session()
    check = getattr(session, 'library_check', None)
    if check is None:
        check = LibraryCompiler(schema_validator('library.schema.json').schema).check
        if session is not None:
            session.library_check = check
    return check
