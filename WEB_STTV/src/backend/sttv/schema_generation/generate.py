"""Generate application schemas from permanent declarations, without game input."""

from jsonschema import Draft202012Validator

from sttv.common.paths import PRODUCT_ROOT
from sttv.common.errors import BuildError
from sttv.common.persistence import save_json
from . import configuration, database, reports, syntax, inline, static_variables, scripted, values
from .helpers import document
from . import localization, localization_report


def declarations():
    return {
        "localization.schema.json": localization.configuration(),
        "localization_report.schema.json": localization_report.schema(),
        "parser_script_values.schema.json": values.configuration(),
        "parser_scripted_calls.schema.json": scripted.configuration(),
        "parser_static_variables.schema.json": static_variables.configuration(),
        "parser_inline_scripts.schema.json": inline.configuration(),
        "parser_exceptions.schema.json": inline.exceptions(),
        "parser_lexical.schema.json": syntax.lexical(),
        "parser_constructs.schema.json": syntax.constructs(),
        "parser_logical_operators.schema.json": syntax.logical_operators(),
        "database.schema.json": database.schema(),
        "backend.schema.json": configuration.schema(),
        "report.schema.json": reports.schema(),
    }


def generate_schemas(directory=None):
    target = PRODUCT_ROOT / "schemas" if directory is None else directory
    documents = {name: document(value) for name, value in declarations().items()}
    for value in documents.values():
        Draft202012Validator.check_schema(value)
    result = {"status": "success", "written": [], "error": None}
    for name, value in sorted(documents.items()):
        try:
            save_json(target / name, value, validator=Draft202012Validator.check_schema)
            result["written"].append(name)
        except (BuildError, OSError, ValueError) as exc:
            result.update(status="failed", error=str(exc))
            break
    return result
