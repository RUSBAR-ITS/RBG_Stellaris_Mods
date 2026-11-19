"""Resolve storage settings without opening the game or invoking a builder."""

from dataclasses import dataclass
from pathlib import Path

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.paths import PRODUCT_ROOT, REPOSITORY_ROOT, PRODUCT_DIRECTORIES, path_from, output_path, selected_path
from sttv.common.variables import expand_variables
from sttv.common.schema import validate_schema
from .identity import relative


def confined(root, path):
    target = root.joinpath(*relative(path).split('/')).resolve()
    if target == root or not target.is_relative_to(root):
        raise BuildError('unsafe_storage_path', f'Path escapes set root: {path}')
    return target


@dataclass
class StorageSettings:
    root: Path
    manifest: Path
    documents: str
    staging: Path
    report: Path
    workers: int
    config_files: list


def load(variables_path=None, config_path=None):
    variables_path = Path(variables_path or PRODUCT_ROOT / 'global_variables.json').resolve()
    config_path = Path(config_path or PRODUCT_ROOT / 'config/storage.json').resolve()
    values = expand_variables(read_json(variables_path))
    work = path_from(values['WORK_DIR'], PRODUCT_ROOT)
    if (not work.is_relative_to(REPOSITORY_ROOT) or work in (REPOSITORY_ROOT, PRODUCT_ROOT)
            or work.is_relative_to(REPOSITORY_ROOT / '.git')
            or any(work.is_relative_to(PRODUCT_ROOT / name) for name in PRODUCT_DIRECTORIES)):
        raise BuildError('unsafe_output', 'Storage WORK_DIR must remain in the repository working area')
    options = read_json(config_path)
    validate_schema(options, 'storage.schema.json')
    root = output_path(work, options['directory'])
    manifest = confined(root, options['manifest'])
    if '/' in options['manifest']:
        raise BuildError('unsafe_storage_path', 'Manifest must be at the set root')
    documents = relative(options['documents'])
    staging = output_path(work, options['staging_directory'])
    report = output_path(work, options['report'])
    parallel_path = selected_path(options['parallel'], work)
    parallel = read_json(parallel_path)
    validate_schema(parallel, 'parallel.schema.json')
    configs = [variables_path, config_path, parallel_path]
    for path in [staging, report, *configs]:
        if path == root or path.is_relative_to(root) or root.is_relative_to(path):
            raise BuildError('storage_path_collision', f'Storage path overlaps set: {path}')
    if confined(root, documents) == manifest:
        raise BuildError('storage_path_collision', 'Documents overlap manifest')
    return StorageSettings(root, manifest, documents, staging, report, parallel['workers'], configs)
