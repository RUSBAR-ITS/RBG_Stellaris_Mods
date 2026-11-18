"""Resolve configurable library sources and workspace artifacts."""

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.paths import selected_path, path_from, output_path, distinct_paths
from sttv.common.schema import validate_schema

KINDS = ('inline_script', 'scripted_effect', 'scripted_trigger', 'script_value', 'static_variables')


def load(selection, values, work, game):
    path = selected_path(selection, work)
    options = read_json(path)
    validate_schema(options, 'libraries.schema.json')
    entries = options['libraries']
    if len({row['id'] for row in entries}) != len(entries) or sorted(row['kind'] for row in entries) != sorted(KINDS):
        raise BuildError('library_configuration', 'Each supported library kind must occur exactly once, with unique IDs')
    for row in entries:
        variable = row['source']['variable']
        if variable not in values:
            raise BuildError('missing_variable', f'Missing library variable: {variable}')
        directory = path_from(values[variable], game)
        if not directory.is_relative_to(game):
            raise BuildError('unsafe_source', f'Library escapes STELLARIS_ROOT: {variable}')
        row['directory'] = directory
    return path, options


def destinations(options, work, roots, other_paths):
    paths = [output_path(work, row['output'], roots) for row in options['libraries']]
    paths.extend(output_path(work, options[key], roots) for key in ('manifest', 'report'))
    locks = {path.parent / '.sttv-libraries.lock' for path in paths}
    distinct_paths([*paths, *other_paths, *locks])
    physical = {}
    for path in [*paths, *other_paths]:
        if path.exists():
            stat = path.stat()
            identity = stat.st_dev, stat.st_ino
            if identity in physical:
                raise BuildError('output_collision', f'Library paths alias each other: {path}, {physical[identity]}')
            physical[identity] = path
    return paths


def reading(settings, kind):
    return next(row['source'] for row in settings.libraries['libraries'] if row['kind'] == kind)
