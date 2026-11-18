"""Resolve localization paths without loading parser settings or libraries."""

import codecs
import re
from dataclasses import dataclass
from pathlib import Path

from sttv.common.errors import BuildError
from sttv.common.paths import (PRODUCT_ROOT, PRODUCT_DIRECTORIES, REPOSITORY_ROOT,
                               distinct_paths, output_path, path_from, protected, selected_path)
from sttv.common.datasets import REGISTRY_PATH
from sttv.common.schema import validate_schema
from sttv.common.variables import expand_variables


@dataclass
class Settings:
    options: dict
    work: Path
    database: Path
    report: Path
    selection_directory: str
    sources: dict


def load_settings(variables_path, config_path, snapshot, kind='technologies', database=None, report_path=None):
    variables = expand_variables(snapshot.json(variables_path, "configuration"))
    options = snapshot.json(config_path, "configuration")
    validate_schema(options, "localization.schema.json")
    work = path_from(variables['WORK_DIR'], PRODUCT_ROOT)
    target_path = selected_path(options['targets'][kind], work)
    target = snapshot.json(target_path, 'configuration')
    snapshot.json(REGISTRY_PATH, 'configuration')
    validate_schema(target, 'localization_target.schema.json')
    options = {**options, **target, 'kind': kind,
               'database': database or options.get('database', 'database.json'),
               'report': report_path or options.get('report', 'reports/localization_report.json')}
    options.pop('targets')
    required = {"WORK_DIR", "STELLARIS_ROOT", options["selection"]["variable"]}
    required.update(tier for spec in options["languages"].values() for tier in spec["sources"])
    if required - variables.keys():
        raise BuildError("missing_variable", f"Missing variables: {sorted(required - variables.keys())}")
    game = path_from(variables["STELLARIS_ROOT"], PRODUCT_ROOT)
    selection = path_from(variables[options["selection"]["variable"]], game)
    if selection == game or not selection.is_relative_to(game):
        raise BuildError("unsafe_source", "Technology selection must stay inside STELLARIS_ROOT")
    sources = {language: [(tier, path_from(variables[tier], game)) for tier in spec["sources"]]
               for language, spec in options["languages"].items()}
    config_files = [Path(variables_path).resolve(), Path(config_path).resolve(), target_path, REGISTRY_PATH]
    roots = [game, REPOSITORY_ROOT / ".git", *config_files,
             *(directory for tiers in sources.values() for _, directory in tiers),
             *(PRODUCT_ROOT / name for name in PRODUCT_DIRECTORIES)]
    if "WORKSHOP_DIR" in variables:
        roots.append(path_from(variables["WORKSHOP_DIR"], game))
    work = path_from(variables["WORK_DIR"], PRODUCT_ROOT)
    if (work in (PRODUCT_ROOT, REPOSITORY_ROOT) or not work.is_relative_to(REPOSITORY_ROOT)
            or protected(work, roots) or any(root.is_relative_to(work) for root in roots if root.is_dir())):
        raise BuildError("unsafe_output", "WORK_DIR must stay inside the repository and outside inputs")
    database, report = (output_path(work, options[key], roots) for key in ("database", "report"))
    paths = [database, report, *config_files]
    distinct_paths(paths)
    existing = [path for path in paths if path.exists()]
    if any(left.samefile(right) for i, left in enumerate(existing) for right in existing[i + 1:]):
        raise BuildError("output_collision", "Input and output files alias each other")
    for spec in (options["selection"], options["reading"]):
        if any(character in spec["pattern"] for character in ("/", "\\")):
            raise BuildError("invalid_pattern", "File patterns must match basenames only")
    reference = options["references"]
    if reference["delimiter"] in "[]£\\" or reference["delimiter"].isspace():
        raise BuildError("invalid_reference", "Reference delimiter conflicts with opaque tokens")
    try:
        pattern = re.compile(reference["key_pattern"])
        codecs.lookup(options["reading"]["encoding"])
    except (re.error, LookupError) as exc:
        raise BuildError("invalid_localization_config", str(exc)) from exc
    if pattern.fullmatch(""):
        raise BuildError("invalid_reference", "Reference keys must be nonempty")
    return Settings(options, work, database, report, selection.relative_to(game).as_posix(), sources)
