"""Select indexed objects using the dataset's configured container path."""

import re
from fnmatch import fnmatchcase
from .datasets import definition


def source_role(kind, source):
    roles = definition(kind).get('sourceRoles')
    if roles is None:
        return 'objects'
    path = source['file'].replace('\\', '/')
    matches = [role['role'] for role in roles if fnmatchcase(path, role['pattern'])]
    if len(matches) != 1:
        from .errors import BuildError
        raise BuildError('source_role', f'{kind}: expected one source role for {path}')
    return matches[0]


def selected_nodes(kind, items, source=None, prefix='/items'):
    if source is not None and source_role(kind, source) == 'descriptor':
        return
    spec = definition(kind)
    containers = spec.get('containers', [])

    def walk(values, path, depth):
        for index, node in enumerate(values):
            if node.get('kind') != 'assignment' or node.get('value', {}).get('kind') != 'block':
                continue
            pointer = f'{path}/{index}'
            if depth < len(containers):
                if node['key']['text'] == containers[depth]:
                    yield from walk(node['value']['items'], pointer + '/value/items', depth + 1)
            elif not spec['rootTypes'] or node['key']['text'] in spec['rootTypes']:
                yield pointer, node
    yield from walk(items, prefix, 0)


def pointer_indices(kind, pointer, source):
    if source_role(kind, source) == 'descriptor':
        return None
    depth = len(definition(kind).get('containers', []))
    if not re.fullmatch(r'/items/(0|[1-9]\d*)' + r'(?:/value/items/(0|[1-9]\d*))' * depth, pointer):
        return None
    return tuple(int(part) for part in re.findall(r'/items/(\d+)', pointer))
