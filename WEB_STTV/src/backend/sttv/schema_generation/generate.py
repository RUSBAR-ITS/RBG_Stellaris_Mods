"""Generate application schemas from permanent declarations, without game input."""

from jsonschema import Draft202012Validator
from stellaris_parser.schema import ROOT as PARSER_ROOT
from document_package.json_io import read_json

from sttv.common.paths import PRODUCT_ROOT
from sttv.common.errors import BuildError
from sttv.common.persistence import save_json
from . import configuration, database, reports
from .helpers import document
from . import localization, localization_report, database_sets
from . import libraries, parallel, technology_tree, technology_tree_rules, storage, assets, dlc, service
from . import acquisition


def declarations():
    syntax = {path.name: read_json(path) for path in (PARSER_ROOT / "schemas").glob("parser_*.schema.json")}
    return {
        **syntax,
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
        "database_set.schema.json": database_sets.configuration(),
        "database_set_report.schema.json": database_sets.report(),
        "localization.schema.json": localization.configuration(),
        "localization_target.schema.json": localization.target(),
        "localization_report.schema.json": localization_report.schema(),
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
