"""Resolve parser inputs and protected workspace outputs independently of cwd."""

from dataclasses import dataclass
from pathlib import Path
from os.path import relpath

from sttv.common.errors import BuildError
from sttv.common.variables import expand_variables, substitute
from sttv.common.json_io import read_json
from sttv.common.paths import (PRODUCT_ROOT, PRODUCT_DIRECTORIES, REPOSITORY_ROOT, distinct_paths,
                               output_path, path_from, protected, selected_path)
from sttv.common.schema import validate_schema
from sttv.script.syntax import Syntax, load_syntax
from sttv.script.variables.rules import Rules


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
    scripted_variables_directory: Path
    parser_exceptions: dict
    static_rules: Rules
    scripted_triggers_directory: Path
    scripted_options: dict
    script_values_directory: Path
    value_options: dict
    source_exceptions: dict
    source_exceptions_file: str
    libraries: dict
    parallel: dict


def load_settings(variables_path, config_path, options=None, dataset=None):
    values = expand_variables(read_json(variables_path))
    options = options if options is not None else read_json(config_path)
    if 'datasets' in options:
        from sttv.database_sets.configuration import build_options
        if dataset is None:
            raise BuildError('missing_dataset', 'Choose a dataset or use the database-set coordinator')
        options = build_options(options, dataset)
    validate_schema(options, "backend.schema.json")
    required = {"WORK_DIR", "STELLARIS_ROOT"}
    required.update(spec["variable"] for spec in options["sources"])
    missing = required - values.keys()
    if missing:
        raise BuildError("missing_variable", f"Missing variables: {sorted(missing)}")
    game = path_from(values["STELLARIS_ROOT"], PRODUCT_ROOT)
    work = path_from(values["WORK_DIR"], PRODUCT_ROOT)
    from sttv.libraries.configuration import load, destinations
    libraries_path, libraries = load(options['libraries'], values, work, game)
    directories_by_kind = {row['kind']: row['directory'] for row in libraries['libraries']}
    inline_directory = directories_by_kind['inline_script']
    scripted_effects_directory = directories_by_kind['scripted_effect']
    scripted_triggers_directory = directories_by_kind['scripted_trigger']
    script_values_directory = directories_by_kind['script_value']
    scripted_variables_directory = directories_by_kind['static_variables']
    sources = [{**spec, "directory": path_from(values[spec["variable"]], game)}
               for spec in options["sources"]]
    directories = [script_values_directory, inline_directory, scripted_effects_directory, scripted_variables_directory, scripted_triggers_directory,
                   *(spec["directory"] for spec in sources)]
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
    from sttv.storage.settings import load as load_storage
    storage = load_storage(variables_path, selected_path(options['storage'], work))
    paths = [storage.manifest, output_path(work, options['outputs']['report'], roots)]
    config_files = list(dict.fromkeys([Path(variables_path).resolve(), Path(config_path).resolve(),
                                    libraries_path, *storage.config_files]))
    parser_paths = [selected_path(options["parser"][key], work)
                    for key in ("lexical", "constructs", "logical_operators")]
    inline_config = selected_path(options["parser"]["inline_scripts"], work)
    exceptions_config = selected_path(options["parser"]["exceptions"], work)
    static_config = selected_path(options["parser"]["static_variables"], work)
    scripted_config = selected_path(options['parser']['scripted_calls'], work)
    value_config = selected_path(options['parser']['script_values'], work)
    corrections_config = selected_path(options['parser']['source_exceptions'], work)
    config_files.append(corrections_config)
    config_files.append(value_config)
    config_files.extend([*parser_paths, inline_config, exceptions_config, static_config, scripted_config])
    distinct_paths([*paths, *config_files])
    destinations(libraries, work, roots, [*paths, *config_files])
    from sttv.parallel.settings import load as load_parallel
    library_paths = [output_path(work, row['output'], roots) for row in libraries['libraries']]
    library_paths.extend(output_path(work, libraries[key], roots) for key in ('manifest', 'report'))
    parallel_path, parallel = load_parallel(options['parallel'], work, roots,
                                           [*paths, *config_files, *library_paths])
    if parallel_path not in config_files:
        config_files.append(parallel_path)
    inline_options = read_json(inline_config)
    validate_schema(inline_options, "parser_inline_scripts.schema.json")
    parser_exceptions = read_json(exceptions_config)
    validate_schema(parser_exceptions, "parser_exceptions.schema.json")
    syntax = load_syntax(*parser_paths)
    static_rules = Rules(read_json(static_config), syntax)
    scripted_options = read_json(scripted_config)
    validate_schema(scripted_options, 'parser_scripted_calls.schema.json')
    from sttv.script.values.references import validate_options
    value_options = read_json(value_config)
    validate_options(value_options, syntax)
    source_exceptions = read_json(corrections_config)
    validate_schema(source_exceptions, 'parser_source_exceptions.schema.json')
    return Settings(values, options, work, game, sources, *paths, roots, config_files,
                    syntax, inline_directory, inline_options, scripted_effects_directory,
                    scripted_variables_directory, parser_exceptions, static_rules,
                    scripted_triggers_directory, scripted_options, script_values_directory, value_options,
                    source_exceptions, Path(relpath(corrections_config, PRODUCT_ROOT)).as_posix(), libraries, parallel)


def check_sources(settings):
    directories = {settings.script_values_directory, settings.game, settings.inline_directory, settings.scripted_variables_directory,
                   settings.scripted_effects_directory, settings.scripted_triggers_directory,
                   *(spec["directory"] for spec in settings.sources)}
    for directory in sorted(directories):
        if not directory.is_dir():
            raise BuildError("source_unavailable", f"Source directory unavailable: {directory}")
