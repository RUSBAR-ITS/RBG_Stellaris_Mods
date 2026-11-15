"""Resolve mixed sequence ranges and single-value addresses after expansion."""

from dataclasses import fields

from .nodes import Located
from .traversal import sequences


def node_paths(node, path):
    yield id(node), path
    for field in fields(node):
        value = getattr(node, field.name)
        if isinstance(value, Located):
            yield from node_paths(value, path + '/' + field.name)
        elif field.name == 'items':
            for index, child in enumerate(value):
                yield from node_paths(child, f'{path}/items/{index}')


def finalize(document, records):
    containers = {id(items): path for path, items in sequences(document.items)}
    addresses = {}
    if any('_node' in record for record in records):
        for index, node in enumerate(document.items):
            addresses.update(node_paths(node, f'/items/{index}'))
    for record in records:
        if '_node' in record:
            record['insertion'] = dict(node=addresses[id(record.pop('_node'))])
        else:
            record['insertion'] = dict(container=containers[id(record.pop('_items'))],
                                      index=record.pop('_index'), count=record.pop('_count'))
