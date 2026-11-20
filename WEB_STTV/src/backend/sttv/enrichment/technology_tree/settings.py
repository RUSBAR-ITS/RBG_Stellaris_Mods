"""Load operation settings without inspecting game files or starting a builder."""

from copy import deepcopy
from dataclasses import dataclass
import hashlib
from pathlib import Path

from jsonschema import Draft202012Validator

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.paths import (PRODUCT_ROOT, REPOSITORY_ROOT, PRODUCT_DIRECTORIES, path_from,
                               selected_path, output_path, distinct_paths, protected)
from sttv.common.schema import validate_schema
from sttv.common.variables import expand_variables
from sttv.schema_generation.technology_tree_rules import parameters
from sttv.storage.settings import StorageSettings, load as load_storage


def signature(path):
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_ino


def digest_file(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


@dataclass
class Settings:
    work: Path
    options: dict
    storage: StorageSettings
    registry: dict
    targets: dict
    selection_directory: str
    rules: dict
    combination: dict
    facts: dict
    report: Path
    staging: Path
    configs: dict
    snapshots: dict
    dlc_rules: dict = None
    dlc_profile: dict = None
    cancelled: object = None
    expected_revision: str = None
    commit_guard: object = None

    def check_snapshot(self):
        if self.cancelled is not None and self.cancelled():
            raise BuildError('cancelled', 'Calculation cancelled before publication')
        for path, expected in self.snapshots.items():
            if not path.exists() or signature(path) != expected:
                raise BuildError('changed_input', f'Input changed during operation: {path}')
        for path, expected in self.configs.items():
            if digest_file(path) != expected:
                raise BuildError('changed_input', f'Configuration changed: {path}')


def resolve_rules(raw):
    validate_schema(raw, 'technology_tree_rules.schema.json')
    rules = deepcopy(raw)
    seen, schemas = set(), parameters()
    for rule in rules['rules']:
        key = rule['id']
        if key in seen:
            raise BuildError('duplicate_rule', f'Duplicate rule: {key}')
        seen.add(key)
        value = rule['parameters']
        if 'definition_ref' in value:
            name = value['definition_ref']
            if name not in rules['definitions']:
                raise BuildError('unknown_definition', f'Unknown parameter block: {name}')
            value = deepcopy(rules['definitions'][name])
        error = next(Draft202012Validator(schemas[key]).iter_errors(value), None)
        if error:
            raise BuildError('invalid_rule', f'{key}: {error.message}')
        rule['parameters'] = value
    rules['definitions'] = {}
    return rules


def load(variables_path=None, config_path=None, combination_path=None):
    configs, snapshots = {}, {}
    def read(path, schema=None):
        path = Path(path).resolve()
        snapshots[path] = signature(path)
        value = read_json(path)
        configs[path] = digest_file(path)
        if schema:
            validate_schema(value, schema)
        return value
    variables = expand_variables(read(variables_path or PRODUCT_ROOT / 'global_variables.json'))
    work = path_from(variables['WORK_DIR'], PRODUCT_ROOT)
    if (not work.is_relative_to(REPOSITORY_ROOT) or work in (REPOSITORY_ROOT, PRODUCT_ROOT)
            or protected(work, [PRODUCT_ROOT / p for p in PRODUCT_DIRECTORIES])):
        raise BuildError('unsafe_output', 'WORK_DIR must be a working directory inside the repository')
    options = read(config_path or PRODUCT_ROOT / 'config/enrichment/technology_tree.json', 'technology_tree.schema.json')
    def referenced(key, schema=None):
        return read(selected_path(options[key], work), schema)
    storage = load_storage(variables_path, selected_path(options['storage'], work))
    for path in storage.config_files:
        read(path)
    registry = referenced('dataset_registry', 'datasets.schema.json')['datasets']
    targets = referenced('technology_targets', 'localization_target.schema.json')
    rules = resolve_rules(referenced('rules'))
    dlc_rules = referenced('dlc_rules', 'dlc.schema.json')
    from sttv.enrichment.dlc.settings import resolve as resolve_dlc
    dlc_rules = resolve_dlc(dlc_rules, read, work)
    combo = read(combination_path or selected_path(options['combination'], work), 'technology_tree_combination.schema.json')
    profile = read(selected_path(combo['profile'], work), 'technology_tree_profile.schema.json')
    report, staging = (output_path(work, options[key]) for key in ('report', 'staging_directory'))
    distinct_paths([storage.manifest, report, staging, *configs])
    for path in (report, staging, *configs):
        if path.is_relative_to(storage.root) or storage.root.is_relative_to(path):
            raise BuildError('output_collision', 'Operation paths overlap the database set')
    existing = [p for p in [storage.manifest, report, *configs] if p.exists()]
    for i, path in enumerate(existing):
        if any(path.samefile(other) for other in existing[:i]):
            raise BuildError('output_collision', 'Input/output paths alias one another')
    selection = targets['selection']
    game = path_from(variables['STELLARIS_ROOT'], PRODUCT_ROOT)
    directory = path_from(variables[selection['variable']], game)
    if not directory.is_relative_to(game):
        raise BuildError('invalid_selection', 'Technology selection must be relative to game root')
    return Settings(work, options, storage, registry, targets, directory.relative_to(game).as_posix(),
                    rules, combo, profile['facts'], report, staging, configs, snapshots, dlc_rules)
