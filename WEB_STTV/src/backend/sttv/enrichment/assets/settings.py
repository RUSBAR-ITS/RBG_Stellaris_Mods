"""Resolve resource preparation configuration through existing path helpers."""

from dataclasses import dataclass
from pathlib import Path

from sttv.common.paths import PRODUCT_ROOT, path_from, selected_path, output_path
from sttv.common.variables import expand_variables
from sttv.common.schema import validate_schema
from sttv.storage.settings import load, confined
from sttv.common.errors import BuildError
from sttv.enrichment.localization.settings import load_settings


@dataclass
class Settings:
    options: dict
    storage: object
    source: Path
    localization: object
    report: Path


def configure(variables_path, config_path, snapshot, storage_path=None):
    values = expand_variables(snapshot.json(variables_path, 'configuration'))
    options = snapshot.json(config_path, 'configuration')
    validate_schema(options, 'assets.schema.json')
    work = path_from(values['WORK_DIR'], PRODUCT_ROOT)
    storage = load(variables_path, storage_path or selected_path(options['storage'], work))
    for path in storage.config_files:
        snapshot.json(path, 'configuration')
    source = path_from(values[options['source_root']], PRODUCT_ROOT)
    confined(source, options['technology_directory'])
    assets = confined(storage.root, options['directory'])
    documents = confined(storage.root, storage.documents)
    if assets == storage.manifest or assets.is_relative_to(documents) or documents.is_relative_to(assets):
        raise BuildError('storage_path_collision', 'Resource directory overlaps documents or manifest')
    loc = load_settings(variables_path, selected_path(options['localization'], work), snapshot,
                        database=storage.manifest.relative_to(work).as_posix())
    report = output_path(work, options['report'])
    if report.is_relative_to(storage.root):
        raise BuildError('storage_path_collision', 'Resource report must be outside the set')
    return Settings(options, storage, source, loc, report)
