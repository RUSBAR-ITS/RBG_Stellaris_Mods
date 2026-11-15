"""Resolve configured paths independently of the caller's working directory."""

import re
from dataclasses import dataclass
from pathlib import Path

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.paths import (PRODUCT_ROOT, PRODUCT_DIRECTORIES, distinct_paths,
                               output_path, path_from, protected, selected_path)
from sttv.common.schema import validate_schema
from sttv.script.syntax import Syntax, load_syntax


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
    profile: Path
    registry: Path
    generation_report: Path
    protected: list
    config_files: list
    syntax: Syntax
    inline_directory: Path
    inline_options: dict


def substitute(value, lookup):
    result = re.sub(r"\$\{([A-Za-z0-9_]+)\}", lambda match: lookup(match[1]), value)
    if "$" + "{" in result:
        raise BuildError("invalid_variable", "Invalid variable substitution")
    return result


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
            expanded[key] = substitute(raw[key], lambda name: expand(name, trail + (key,)))
        return expanded[key]

    for key in raw:
        expand(key)
    return expanded


def load_settings(variables_path, config_path):
    values = expand_variables(read_json(variables_path))
    options = read_json(config_path)
    validate_schema(options, "backend.schema.json")
    required = {"WORK_DIR", "STELLARIS_ROOT", "WORKSHOP_DIR", "TECH_PATH", "INLINE_SCRIPTS_DIR"}
    names = {name for spec in options["localization"]["languages"].values()
             for name in spec["sources"]}
    missing = (required | names) - values.keys()
    if missing:
        raise BuildError("missing_variable", f"Missing variables: {sorted(missing)}")
    game = path_from(values["STELLARIS_ROOT"], PRODUCT_ROOT)
    workshop = path_from(values["WORKSHOP_DIR"], PRODUCT_ROOT)
    technology = path_from(values["TECH_PATH"], game)
    inline_directory = path_from(values["INLINE_SCRIPTS_DIR"], game)
    if not inline_directory.is_relative_to(game):
        raise BuildError("unsafe_source", "INLINE_SCRIPTS_DIR must remain inside STELLARIS_ROOT")
    if not technology.is_relative_to(game):
        raise BuildError("unsafe_source", "TECH_PATH must remain inside STELLARIS_ROOT")
    sources = {name: path_from(values[name], game) for name in names}
    work = path_from(values["WORK_DIR"], PRODUCT_ROOT)
    roots = [game, workshop, technology, inline_directory, *sources.values(),
             *(PRODUCT_ROOT / name for name in PRODUCT_DIRECTORIES)]
    if protected(work, roots):
        raise BuildError("unsafe_output", "WORK_DIR overlaps a protected directory")
    profile = selected_path(options["rules"]["profile"], work)
    paths = [output_path(work, value, roots) for value in (
        options["outputs"]["database"], options["outputs"]["report"],
        options["rules"]["registry"], options["rules"]["report"])]
    config_files = [Path(variables_path).resolve(), Path(config_path).resolve()]
    parser_paths = [selected_path(options["parser"][key], work) for key in ("lexical", "constructs", "logical_operators")]
    config_files.extend(parser_paths)
    inline_config = selected_path(options["parser"]["inline_scripts"], work)
    config_files.append(inline_config)
    inline_options = read_json(inline_config)
    validate_schema(inline_options, "parser_inline_scripts.schema.json")
    distinct_paths([*paths, profile, *config_files])
    syntax = load_syntax(*parser_paths)
    for lang, spec in options["localization"]["languages"].items():
        if spec["header"] != {"ru": "l_russian", "en": "l_english"}[lang]:
            raise BuildError("language_mismatch", f"Invalid header for {lang}")
    database, report, registry, generation_report = paths
    return Settings(values, options, work, game, workshop, technology, sources,
                    database, report, profile, registry, generation_report, roots, config_files, syntax,
                    inline_directory, inline_options)


def check_sources(settings):
    directories = {settings.game, settings.technology, settings.inline_directory, *settings.sources.values()}
    for profile in settings.options["definitions"].values():
        directory = path_from(profile["subdirectory"], settings.technology)
        if not directory.is_relative_to(settings.technology):
            raise BuildError("unsafe_source", "Definition directory escapes TECH_PATH")
        directories.add(directory)
    for directory in sorted(directories):
        if not directory.is_dir():
            raise BuildError("source_unavailable", f"Source directory unavailable: {directory}")
