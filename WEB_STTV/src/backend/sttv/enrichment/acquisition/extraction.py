"""Retain execution paths and guards; omit unrelated syntax, never provenance as code."""

from sttv.enrichment.technology_tree.ast import compact, scalar
from sttv.storage.identity import digest


def key(node):
    return node.get('key', {}).get('text', '').casefold()


def reference_target(text):
    return text if text and not any(mark in text for mark in ('$', '@', ':')) else '*'


def walk(node, path=''):
    yield path, node
    for field in ('value', 'body', 'block'):
        child = node.get(field)
        if isinstance(child, dict):
            yield from walk(child, path + '/' + field)
    for i, child in enumerate(node.get('items', [])):
        yield from walk(child, f'{path}/items/{i}')


def extract(document, options):
    effects, entries = options['effects'], options['entries']
    signals = set(effects['commands']) | set(effects['event_calls']) | {effects['activation']}
    signals.update(entries['event_lists'])
    guards = set(entries['condition_fields'])
    source = document['source']['file']
    spec = next((s for s in entries['definitions'] if source.startswith(s['directory'] + '/')), None)
    if spec and spec['type'] == 'crisis_path':
        signals.add(entries['crisis_levels'])
    records, index, calls = [], {}, {}
    found, retained = [], []
    relevant_nodes = set()

    def mark(node, declaration=False):
        present = not declaration and key(node) in signals
        for field in ('value', 'body', 'block'):
            if isinstance(node.get(field), dict):
                present = mark(node[field]) or present
        for child in node.get('items', []):
            present = mark(child) or present
        if present:
            relevant_nodes.add(id(node))
        return present

    def prune(node, path, condition=False):
        name = key(node)
        if condition or name in guards:
            return compact(node)
        # Preserve all command arguments; arbitrary dynamic targets cannot be discarded.
        declaration = spec and spec['type'] == 'event' and path.count('/') == 2
        if name in signals and not declaration:
            retained.append(path)
            return compact(node)
        if name and name not in effects['branches'] and id(node) not in relevant_nodes and path.count('/') > 2 and node.get('value', {}).get('kind') == 'block':
            return {'kind': 'assignment', 'key': compact(node['key']), 'operator': node['operator'],
                    'value': {'kind': 'scalar', 'text': '__unanalysed_effect__'}}
        result = compact(node) if node.get('kind') == 'scalar' else {'kind': node.get('kind')}
        for field in ('operator', 'negated'):
            if field in node:
                result[field] = node[field]
        for field in ('key', 'parameter', 'tag'):
            if field in node:
                result[field] = compact(node[field])
        for field in ('value', 'body', 'block'):
            if isinstance(node.get(field), dict):
                result[field] = prune(node[field], path + '/' + field)
        if 'items' in node:
            result['items'] = [prune(n, f'{path}/items/{i}') for i, n in enumerate(node['items'])]
        return result

    for i, node in enumerate(document['items']):
        declaration = spec and spec['type'] == 'event'
        mark(node, declaration)
        pointer = f'/items/{i}'
        relevant = [(p, n) for p, n in walk(node, pointer) if key(n) in signals and not (declaration and p == pointer)]
        if not relevant and not (spec and spec['type'] == 'crisis_level' and node.get('kind') == 'assignment'):
            continue
        found.extend(p for p, _ in relevant)
        # Condition/argument subtrees are retained verbatim, including nested signals.
        body = prune(node, pointer)
        retained_paths = {p for p, n in walk(body, pointer) if key(n) in signals and not (declaration and p == pointer)}
        if {p for p, _ in relevant} != retained_paths:
            raise ValueError('Acquisition extraction lost a command or call')
        identity = node.get('key', {}).get('text', '')
        if spec and spec['type'] == 'event':
            identity = scalar(node.get('value', {}), entries['event_id'], identity)
        record_id = digest([source, pointer])
        records.append({'record_id': record_id, 'id': identity, 'type': spec['type'] if spec else 'unknown',
                        'source': source, 'pointer': pointer, 'node': body})
        if spec and spec['type'] == 'crisis_level':
            calls.setdefault('crisis_level_definition', []).append(record_id)
        for path, item in relevant:
            name, value = key(item), item.get('value', {})
            if name in effects['commands']:
                rule = effects['commands'][name]
                target = value.get('text') if value.get('kind') == 'scalar' else scalar(value, rule['target'])
                target = '*' if rule['handler'] in ('random', 'copy_random', 'copy_all') else reference_target(target)
                index.setdefault(target, []).append(record_id)
            else:
                calls.setdefault(name, []).append(record_id)
    return {'format': 'sttv.acquisition_document', 'format_version': 1, 'source': source,
            'records': records, 'targets': {k: sorted(set(v)) for k, v in index.items()},
            'calls': {k: sorted(set(v)) for k, v in calls.items()},
            'coverage': {'parsed': True, 'commands_checked': len(found), 'diagnostics': []}}
