"""Prepared structural and contextual validation with one document traversal."""

from copy import deepcopy
from time import perf_counter

from sttv.common.errors import BuildError
from sttv.common.schema import current_session, schema_validator
from .checks.compiler import Compiler
from .checks.context import DocumentContext

FORMAT = 'sttv.parse_database'
FORMAT_VERSION = 6


class DatabaseRules:
    def __init__(self):
        start = perf_counter()
        schema = schema_validator('database.schema.json').schema
        self.compiler = Compiler(schema)
        container = deepcopy(schema)
        container['properties']['documents'].pop('items', None)
        self.container = self.compiler.prepare(container)
        self.document = self.compiler.prepare(schema['$defs']['document'])
        self.seconds = perf_counter() - start


def database_rules():
    session = current_session()
    if session is None:
        return DatabaseRules()
    if session.database_rules is None:
        session.database_rules = DatabaseRules()
    return session.database_rules


class DatabaseValidator:
    def __init__(self):
        self.rules, self.sources, self.count = database_rules(), set(), 0

    def document(self, document, index):
        context = DocumentContext(document, f'/documents/{index}')
        try:
            self.rules.document(document, context.prefix, context)
            identity = (document['source']['root'], document['source']['file'].casefold())
            if identity in self.sources:
                raise BuildError('duplicate_source', f'Repeated source document: {identity[1]}', field_path=context.prefix)
            context.finish(document)
        except BuildError as exc:
            source = document.get('source') if isinstance(document, dict) else None
            if isinstance(source, dict) and isinstance(source.get('file'), str):
                exc.args = (f"{source['file']}: {exc}",)
            raise
        self.sources.add(identity)
        self.count += 1
        return context.count

    def container(self, database):
        if (not isinstance(database, dict) or database.get('format') != FORMAT
                or database.get('format_version') != FORMAT_VERSION):
            raise BuildError('incompatible_database', 'Unsupported database format; rebuild from source files')
        self.rules.container(database, '', None)


def validate_database(database):
    validator = DatabaseValidator()
    validator.container(database)
    for index, document in enumerate(database['documents']):
        validator.document(document, index)
