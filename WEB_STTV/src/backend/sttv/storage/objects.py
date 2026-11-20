"""Index game objects without copying their syntax trees."""

from sttv.common.datasets import definition
from sttv.common.errors import BuildError
from sttv.common.object_selection import selected_nodes


def object_row(kind, identifier, pointer, node):
    spec = definition(kind)
    if node.get('kind') != 'assignment' or node.get('value', {}).get('kind') != 'block':
        return None
    key = node['key']['text']
    if spec['rootTypes'] and key not in spec['rootTypes']:
        return None
    identity = key
    if spec['identity'] == 'field':
        values = [n['value'].get('text') for n in node['value']['items']
                  if n['kind'] == 'assignment' and n['key']['text'] == spec['idField']]
        if len(values) != 1 or not isinstance(values[0], str) or not values[0]:
            raise BuildError('missing_object_id', f'{kind}/{identifier}{pointer}: invalid identity')
        identity = values[0]
    if spec['identity'] == 'anonymous':
        identity = None
    return {'id': identity, 'type': key, 'document_id': identifier, 'pointer': pointer}


def index_document(kind, identifier, items, source=None):
    return [object_row(kind, identifier, pointer, node)
            for pointer, node in selected_nodes(kind, items, source)]


def check_objects(kind, rows, documents):
    ids, addresses = {}, set()
    for row in rows:
        address = row['document_id'], row['pointer']
        if address in addresses or row['document_id'] not in documents:
            raise BuildError('invalid_object_index', f'{kind}: repeated or unknown object address: {address}')
        addresses.add(address)
        spec = definition(kind)
        if (row['id'] is None) != (spec['identity'] == 'anonymous'):
            raise BuildError('invalid_object_index', f'{kind}: invalid anonymous identity')
        if row['id'] is not None:
            if row['id'] in ids and spec['identity'] != 'fragments':
                raise BuildError('duplicate_object', f'{kind}/{row["id"]}: {ids[row["id"]]} and {address}')
            ids.setdefault(row['id'], []).append(address)
    return ids
