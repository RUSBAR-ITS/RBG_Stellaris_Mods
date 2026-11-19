"""Convert producer-local localization pointers into persistent document references."""

import re

from sttv.common.errors import BuildError


def nodes(document):
    stack = list(document['items'])
    while stack:
        node = stack.pop()
        if not isinstance(node, dict) or 'kind' not in node:
            continue
        yield node
        stack.extend(node.get('items', []))
        for key in ('value', 'body', 'block', 'key', 'name', 'tag'):
            if isinstance(node.get(key), dict):
                stack.append(node[key])


def node_ref(kind, identifier, pointer):
    return {'database': kind, 'document_id': identifier, 'pointer': pointer}


def diagnostics(report, kind, identifier, start=0):
    for row in report['diagnostics'][start:]:
        pointer = row.get('node')
        if isinstance(pointer, str) and pointer.startswith('/documents/'):
            row['node'] = node_ref(kind, identifier, re.sub(r'^/documents/\d+', '', pointer))


def finalize(document, kind, identifier):
    def convert(value):
        if isinstance(value, dict):
            return value
        pointer = re.sub(r'^/documents/\d+', '', value)
        if not pointer.startswith('/items/'):
            raise BuildError('invalid_reference', f'Invalid producer pointer: {value}')
        return node_ref(kind, identifier, pointer)
    for node in nodes(document):
        for fields in node.get('enrichments', {}).get('localization', {}).values():
            for field in fields.values():
                if field['inherited_from'] is not None:
                    field['inherited_from'] = convert(field['inherited_from'])
                if 'fallback' in field:
                    field['fallback']['source_ref'] = convert(field['fallback']['source_ref'])
