"""Check the persisted syntax contract without consulting game sources."""

from sttv.common.errors import BuildError
from sttv.common.schema import validate_schema
from .history import validate_history
from .enrichment import validate_enrichments

FORMAT = "sttv.parse_database"
FORMAT_VERSION = 4


def validate_database(database):
    if (not isinstance(database, dict) or database.get("format") != FORMAT
            or database.get("format_version") != FORMAT_VERSION):
        raise BuildError("incompatible_database", "Unsupported database format; rebuild from source files")
    validate_schema(database, "database.schema.json")
    sources = set()
    for document in database["documents"]:
        identity = (document["source"]["root"], document["source"]["file"].casefold())
        if identity in sources:
            raise BuildError("duplicate_source", f"Repeated source document: {identity[1]}")
        sources.add(identity)
        validate_history(document)

    validate_enrichments(database)
