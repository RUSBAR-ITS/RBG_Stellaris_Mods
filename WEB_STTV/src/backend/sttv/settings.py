"""Resolve configured paths independently of the caller's working directory."""

import re
from dataclasses import dataclass
from pathlib import Path

from .errors import BuildError
from .json_io import read_json
from .schema import PRODUCT_ROOT, validate_schema


@dataclass
class Settings:
    variables: dict
    options: dict
    work: Path
    game: Path
    workshop: Path
    technology: Path
    sources: dict
    database: Path
    report: Path


def expand_variables(raw):
    if not isinstance(raw, dict) or any(
        not re.fullmatch(r"[A-Z][A-Z0-9_]*", key) or not isinstance(value, str)
        or not value for key, value in raw.items()
    ):
        raise BuildError("invalid_variables", "Variables must be named nonempty strings")
    expanded = {}

    def expand(key, trail=()):
        if key not in raw:
            raise BuildError("unknown_variable", f"Unknown variable: {key}")
        if key in trail:
            raise BuildError("variable_cycle", f"Configuration variable cycle: {key}")
        if key not in expanded:
            expanded[key] = re.sub(
                r"\$\{([A-Za-z0-9_]+)\}",
                lambda match: expand(match[1], trail + (key,)), raw[key])
            if "$" + "{" in expanded[key]:
                raise BuildError("invalid_variable", f"Invalid substitution in {key}")
        return expanded[key]

    for key in raw:
        expand(key)
    return expanded


def path_from(value, parent):
    path = Path(value)
    return (path if path.is_absolute() else parent / path).resolve()


def protected(path, roots):
    return any(path == root or path.is_relative_to(root) for root in roots)


def output_path(work, value, roots):
    relative = Path(value)
    if relative.is_absolute() or relative.drive:
        raise BuildError("unsafe_output", "Output filenames must be relative to WORK_DIR")
    target = (work / relative).resolve()
    if target == work or not target.is_relative_to(work) or protected(target, roots):
        raise BuildError("unsafe_output", f"Output path is not writable: {value}")
    return target


def load_settings(variables_path, config_path):
    values = expand_variables(read_json(variables_path))
    options = read_json(config_path)
    validate_schema(options, "backend.schema.json")
    required = {"WORK_DIR", "STELLARIS_ROOT", "WORKSHOP_DIR", "TECH_PATH"}
    names = {name for spec in options["localization"]["languages"].values()
             for name in spec["sources"]}
    missing = (required | names) - values.keys()
    if missing:
        raise BuildError("missing_variable", f"Missing variables: {sorted(missing)}")
    game = path_from(values["STELLARIS_ROOT"], PRODUCT_ROOT)
    workshop = path_from(values["WORKSHOP_DIR"], PRODUCT_ROOT)
    technology = path_from(values["TECH_PATH"], game)
    if not technology.is_relative_to(game):
        raise BuildError("unsafe_source", "TECH_PATH must remain inside STELLARIS_ROOT")
    sources = {name: path_from(values[name], game) for name in names}
    work = path_from(values["WORK_DIR"], PRODUCT_ROOT)
    roots = [game, workshop, technology, *sources.values(),
             PRODUCT_ROOT / "src", PRODUCT_ROOT / "schemas", PRODUCT_ROOT / "config",
             PRODUCT_ROOT / "Docs"]
    if protected(work, roots):
        raise BuildError("unsafe_output", "WORK_DIR overlaps a protected directory")
    database = output_path(work, options["outputs"]["database"], roots)
    report = output_path(work, options["outputs"]["report"], roots)
    if database == report or database.is_relative_to(report) or report.is_relative_to(database):
        raise BuildError("output_collision", "Database and report paths overlap")
    inputs = {Path(variables_path).resolve(), Path(config_path).resolve()}
    if database in inputs or report in inputs:
        raise BuildError("output_collision", "Output would replace configuration")
    for lang, spec in options["localization"]["languages"].items():
        if spec["header"] != {"ru": "l_russian", "en": "l_english"}[lang]:
            raise BuildError("language_mismatch", f"Invalid header for {lang}")
    return Settings(values, options, work, game, workshop, technology,
                    sources, database, report)


def check_sources(settings):
    directories = {settings.game, settings.technology, *settings.sources.values()}
    for profile in settings.options["definitions"].values():
        directory = path_from(profile["subdirectory"], settings.technology)
        if not directory.is_relative_to(settings.technology):
            raise BuildError("unsafe_source", "Definition directory escapes TECH_PATH")
        directories.add(directory)
    for directory in sorted(directories):
        if not directory.is_dir():
            raise BuildError("source_unavailable", f"Source directory unavailable: {directory}")
