"""Read only the structural script fields used by relationship criteria."""

from decimal import Decimal, InvalidOperation

from .errors import BuildError


def fields(node, key):
    return [n['value'] for n in node.get('items', [])
            if n.get('kind') == 'assignment' and n['key']['text'] == key and n['operator'] == '=']


def scalar(node, key, default=None):
    values = fields(node, key)
    if not values:
        return default
    texts = {n.get('text') for n in values}
    if len(texts) != 1 or None in texts:
        raise BuildError('ambiguous_field', f'Expected one scalar value for {key}')
    return next(iter(texts))


def compact(node):
    """Remove provenance, preserving ordered syntax and all script field names."""
    kind = node.get('kind')
    if kind == 'scalar':
        return {'kind': kind, 'text': node['text']}
    keys = {'assignment': ('key', 'operator', 'value'), 'logical_operation': ('operator', 'body'),
            'block': ('items',), 'tagged_block': ('tag', 'block'), 'formula': ('opener', 'body'),
            'conditional': ('parameter', 'negated', 'items'), 'script_value': ('scope', 'body'),
            'scripted_trigger_test': ('operator', 'value', 'body')}.get(kind)
    if keys is None:
        raise BuildError('unsupported_node', f'Unsupported node kind: {kind}')
    def clean(value):
        if isinstance(value, dict):
            return compact(value)
        return [clean(v) for v in value] if isinstance(value, list) else value
    return {'kind': kind, **{key: clean(node[key]) for key in keys}}


def requirements(node, *, strict=True):
    """Return all IDs, mandatory IDs, and whether the expression has only AND."""
    kind = node.get('kind')
    if kind == 'scalar':
        return {node['text']}, {node['text']}, True
    if kind == 'block':
        children, operator = node['items'], 'AND'
    elif kind == 'logical_operation' and node['operator'] in ('AND', 'OR'):
        children, operator = node['body']['items'], node['operator']
        if operator == 'OR' and not children:
            raise BuildError('unsupported_requirements', 'An OR requirement cannot be empty')
    elif not strict:
        return set(), set(), False
    else:
        raise BuildError('unsupported_requirements', f'Unsupported requirement: {kind} {node.get("operator", "")}')
    rows = [requirements(n, strict=strict) for n in children]
    all_ids = set().union(*(r[0] for r in rows))
    mandatory = (set.intersection(*(r[1] for r in rows)) if operator == 'OR'
                 else set().union(*(r[1] for r in rows)))
    return all_ids, mandatory, operator == 'AND' and all(r[2] for r in rows)


def references(node):
    return requirements(node, strict=False)[0]


def prerequisite(body):
    return {'kind': 'block', 'items': fields(body, 'prerequisites')}


def checks(node, path=(), negative=False):
    if node.get('kind') == 'assignment':
        key = node['key']['text']
        if not negative:
            yield key, node['value'], node['operator'], path
        yield from checks(node['value'], path + (key,), negative)
    elif node.get('kind') == 'logical_operation':
        yield from checks(node['body'], path + (node['operator'],),
                          negative or node['operator'] in ('NOT', 'NOR', 'NAND'))
    else:
        for child in node.get('items', []):
            yield from checks(child, path, negative)


def number(value):
    try:
        result = Decimal(value)
        return result if result.is_finite() else None
    except (InvalidOperation, TypeError, ValueError):
        return None


def numeric_items(block):
    for n in block.get('items', []):
        if n.get('kind') == 'assignment' and n['operator'] == '=':
            value = number(n['value'].get('text'))
            if value is not None:
                yield n['key']['text'], value


def access(record):
    return {k: fields(record['body'], k) for k in ('prerequisites', 'potential', 'allow', 'possible')}


def unlocks(record):
    result = references(prerequisite(record['body']))
    for section in ('potential', 'allow', 'possible'):
        for block in fields(record['body'], section):
            result.update(v['text'] for k, v, op, _ in checks(block)
                          if k == 'has_technology' and op == '=' and v.get('kind') == 'scalar')
    return result
