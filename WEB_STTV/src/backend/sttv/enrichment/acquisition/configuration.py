"""Load explicit acquisition sources and semantic handlers."""

from sttv.common.json_io import read_json
from sttv.common.paths import selected_path
from sttv.common.schema import validate_schema
from sttv.storage.identity import digest

REVISION = 'sttv.acquisition.v1'


def load(selection, work, read=None):
    def fetch(path, schema):
        if read is not None:
            return read(path, schema)
        data = read_json(path)
        validate_schema(data, schema)
        return data
    source = selected_path(selection, work)
    result = fetch(source, 'acquisition_sources.schema.json')
    files = [source]
    for key in ('effects', 'entries'):
        path = selected_path(result[key], work)
        files.append(path)
        result = {**result, key: fetch(path, f'acquisition_{key}.schema.json')}
    result['revision'] = digest({'implementation': REVISION, 'configuration': result})
    return result, files
