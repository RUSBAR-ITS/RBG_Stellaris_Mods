"""Configured concurrency and operation-owned staging directories."""

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.paths import output_path, selected_path
from sttv.common.schema import validate_schema


def load(reference, work, protected, destinations):
    path = selected_path(reference, work)
    options = read_json(path)
    validate_schema(options, 'parallel.schema.json')
    directory = output_path(work, options['staging_directory'], protected).resolve()
    for target in [*destinations, path]:
        target = target.resolve()
        if directory == target or directory.is_relative_to(target) or target.is_relative_to(directory):
            raise BuildError('parallel_path_collision', f'Staging overlaps another path: {target}')
    if directory == work.resolve():
        raise BuildError('unsafe_output', 'Staging must be a subdirectory of WORK_DIR')
    return path, {**options, 'directory': directory}
