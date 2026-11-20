"""Generate application schemas from permanent declarations, without game input."""

from jsonschema import Draft202012Validator

from sttv.common.paths import PRODUCT_ROOT
from sttv.common.errors import BuildError
from sttv.common.persistence import save_json
from . import configuration, database, reports, syntax, inline, static_variables, scripted, values
from .helpers import document
from . import localization, localization_report, database_sets, source_exceptions
from . import libraries, parallel, technology_tree, technology_tree_rules, storage, assets, dlc, service
from . import acquisition


def declarations():
    return {
        'acquisition_sources.schema.json': acquisition.sources(),
        'acquisition_effects.schema.json': acquisition.effects(),
        'acquisition_entries.schema.json': acquisition.entries(),
        'acquisition_document.schema.json': acquisition.document(),
        'dlc.schema.json': dlc.configuration(),
        'dlc_group.schema.json': dlc.group(),
        'service.schema.json': service.configuration(),
        'assets.schema.json': assets.configuration(),
        'assets_report.schema.json': assets.report(),
        'storage.schema.json': storage.configuration(),
        'database_manifest.schema.json': storage.manifest(),
        'database_document.schema.json': storage.document(),
        'storage_report.schema.json': storage.report(),
        'technology_tree.schema.json': technology_tree.configuration(),
        'technology_tree_rules.schema.json': technology_tree_rules.schema(),
        'technology_tree_combination.schema.json': technology_tree.combination(),
        'technology_tree_profile.schema.json': technology_tree.profile(),
        'technology_tree_report.schema.json': technology_tree.report(),
        'parallel.schema.json': parallel.configuration(),
        'libraries.schema.json': libraries.configuration(),
        'library.schema.json': libraries.artifact(),
        'library_manifest.schema.json': libraries.manifest(),
        'library_report.schema.json': libraries.report(),
        "datasets.schema.json": database_sets.registry(),
        "parser_source_exceptions.schema.json": source_exceptions.configuration(),
        "database_set.schema.json": database_sets.configuration(),
        "database_set_report.schema.json": database_sets.report(),
        "localization.schema.json": localization.configuration(),
        "localization_target.schema.json": localization.target(),
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
