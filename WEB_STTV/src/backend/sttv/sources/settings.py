"""Resolve parser inputs and protected workspace outputs independently of cwd."""

import re
from dataclasses import dataclass
from pathlib import Path

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.paths import (PRODUCT_ROOT, PRODUCT_DIRECTORIES, REPOSITORY_ROOT, distinct_paths,
                               output_path, path_from, protected, selected_path)
from sttv.common.schema import validate_schema
from sttv.script.syntax import Syntax, load_syntax


@dataclass
class Settings:
    variables: dict
    options: dict
    work: Path
    game: Path
    sources: list
    database: Path
    report: Path
    protected: list
    config_files: list
    syntax: Syntax
    inline_directory: Path
    inline_options: dict
    scripted_effects_directory: Path
    parser_exceptions: dict


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
    required = {"WORK_DIR", "STELLARIS_ROOT", "INLINE_SCRIPTS_DIR", "SCRIPTED_EFFECTS_DIR"}
    required.update(spec["variable"] for spec in options["sources"])
    missing = required - values.keys()
    if missing:
        raise BuildError("missing_variable", f"Missing variables: {sorted(missing)}")
    game = path_from(values["STELLARIS_ROOT"], PRODUCT_ROOT)
    inline_directory = path_from(values["INLINE_SCRIPTS_DIR"], game)
    scripted_effects_directory = path_from(values["SCRIPTED_EFFECTS_DIR"], game)
    sources = [{**spec, "directory": path_from(values[spec["variable"]], game)}
               for spec in options["sources"]]
    directories = [inline_directory, scripted_effects_directory, *(spec["directory"] for spec in sources)]
    if any(not path.is_relative_to(game) for path in directories):
        raise BuildError("unsafe_source", "Source directories must remain inside STELLARIS_ROOT")
    work = path_from(values["WORK_DIR"], PRODUCT_ROOT)
    roots = [game, *directories, REPOSITORY_ROOT / ".git",
             *(PRODUCT_ROOT / name for name in PRODUCT_DIRECTORIES)]
    roots.extend(path_from(value, game) for key, value in values.items()
                 if key == "WORKSHOP_DIR" or key.startswith(("RU_LOC_TIER_", "EN_LOC_TIER_")))
    if (work in (REPOSITORY_ROOT, PRODUCT_ROOT) or not work.is_relative_to(REPOSITORY_ROOT)
            or protected(work, roots) or any(root.is_relative_to(work) for root in roots)):
        raise BuildError("unsafe_output", "WORK_DIR must remain in the repository, separate from protected inputs")
    paths = [output_path(work, options["outputs"][key], roots) for key in ("database", "report")]
    config_files = [Path(variables_path).resolve(), Path(config_path).resolve()]
    parser_paths = [selected_path(options["parser"][key], work)
                    for key in ("lexical", "constructs", "logical_operators")]
    inline_config = selected_path(options["parser"]["inline_scripts"], work)
    exceptions_config = selected_path(options["parser"]["exceptions"], work)
    config_files.extend([*parser_paths, inline_config, exceptions_config])
    distinct_paths([*paths, *config_files])
    inline_options = read_json(inline_config)
    validate_schema(inline_options, "parser_inline_scripts.schema.json")
    parser_exceptions = read_json(exceptions_config)
    validate_schema(parser_exceptions, "parser_exceptions.schema.json")
    syntax = load_syntax(*parser_paths)
    return Settings(values, options, work, game, sources, *paths, roots, config_files,
                    syntax, inline_directory, inline_options, scripted_effects_directory, parser_exceptions)


def check_sources(settings):
    directories = {settings.game, settings.inline_directory,
                   *(spec["directory"] for spec in settings.sources)}
    for directory in sorted(directories):
        if not directory.is_dir():
            raise BuildError("source_unavailable", f"Source directory unavailable: {directory}")
