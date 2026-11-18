"""Select explicit description texts without interpreting their conditions."""

from sttv.common.errors import BuildError
from .targets import Target, assignment, entries, scalar


def text_targets(node, path, keys):
    if node['value']['kind'] == 'scalar':
        key = scalar(node['value'], path)
        yield Target(path, node, key, field_keys={'description': key}, kind='descriptions')
        return
    if node['value']['kind'] != 'block':
        raise BuildError('invalid_target', 'Unsupported description form', field_path=path)
    items = node['value']['items']
    excluded = keys.get('description_excluded', ['trigger', 'limit', 'exclusive_trigger'])
    for i, child in enumerate(items):
        if not assignment(child):
            continue
        name = child['key']['text']
        child_path = f'{path}/value/items/{i}'
        if name == keys['text_field']:
            value = scalar(child['value'], child_path)
            yield Target(child_path, child, value, field_keys={'description': value}, kind='descriptions')
        elif name not in excluded and child['value']['kind'] == 'block':
            yield from text_targets(child, child_path, keys)


def descriptions(base, keys):
    matches = entries(base.node, keys['description_field'])
    if not matches:
        return
    if not keys.get('description_nodes') and len(matches) == 1 and matches[0][1]['value']['kind'] == 'scalar':
        base.field_keys['description'] = scalar(matches[0][1]['value'], base.path)
        return
    for i, child in matches:
        path = f'{base.path}/value/items/{i}'
        texts = entries(child, keys['text_field']) if child['value']['kind'] == 'block' else []
        if not keys.get('description_nodes') and len(texts) == 1:
            key = scalar(texts[0][1]['value'], path)
            yield Target(path, child, key, field_keys={'description': key}, kind='descriptions')
        else:
            yield from text_targets(child, path, keys)


def child_targets(base, keys):
    for spec in keys.get('child_text_fields', []):
        for i, child in entries(base.node, spec['field']):
            path = f'{base.path}/value/items/{i}'
            key = scalar(child['value'], path)
            yield Target(path, child, key, field_keys={spec['role']: key}, kind='descriptions')
    for name in keys.get('endpoint_fields', []):
        value = entries(base.node, name)
        if len(value) != 1:
            raise BuildError('invalid_target', f'Expected one transition endpoint: {name}', field_path=base.path)
        i, child = value[0]
        path = f'{base.path}/value/items/{i}'
        key = scalar(child['value'], path)
        yield Target(path, child, key, field_keys={
            'name': key, 'description': key + keys['endpoint_description_suffix']}, kind='descriptions')
