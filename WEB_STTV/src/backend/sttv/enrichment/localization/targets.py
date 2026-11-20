"""Small selectors shared by root and nested localization targets."""

from dataclasses import dataclass, field

from sttv.common.errors import BuildError


@dataclass
class Target:
    path: str
    node: dict
    key: str
    parent: object = None
    field_keys: dict = field(default_factory=dict)
    fallback: tuple | None = None
    kind: str = 'technologies'
    candidates: dict = field(default_factory=dict)
    candidate_sources: dict = field(default_factory=dict)


def assignment(node, key=None):
    return (node['kind'] == 'assignment' and node['operator'] == '='
            and (key is None or node['key']['text'] == key))


def entries(node, key):
    return [(i, child) for i, child in enumerate(node['value'].get('items', [])) if assignment(child, key)]


def scalar(node, path):
    if node.get('kind') != 'scalar' or not node.get('text'):
        raise BuildError('invalid_target', 'Expected one nonempty scalar key', field_path=path)
    return node['text']


def one_field(node, key, path, required=True):
    matches = entries(node, key)
    if len(matches) > 1 or (required and not matches):
        raise BuildError('invalid_target', f'Expected one field: {key}', field_path=path)
    if not matches:
        return None
    i, child = matches[0]
    ref = f'{path}/value/items/{i}'
    return scalar(child['value'], ref), ref


def variants(base, keys):
    for i, child in entries(base.node, keys['variant']):
        path = f'{base.path}/value/items/{i}'
        if child['value']['kind'] != 'block':
            raise BuildError('invalid_target', 'Variant must be a block', field_path=path)
        name, _ = one_field(child, keys['name'], path)
        yield Target(path, child, name, base,
                     {'name': name, 'description': name + keys['description_suffix']}, kind='variants')
