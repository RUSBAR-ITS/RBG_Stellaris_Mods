"""Separate parser source locations from queryable script nodes."""

from bson import BSON
from document_package.errors import BuildError


NODE_KINDS = frozenset({
    'scalar', 'formula', 'block', 'tagged_block', 'conditional', 'assignment',
    'logical_operation', 'scripted_trigger_test', 'script_value',
})
ORIGIN_FIELDS = {
    'root': 'roots', 'file': 'files', 'span': 'spans',
    'generated_span': 'spans', 'expansion_id': 'expansions',
}
TABLES = ('origins', 'spans', 'roots', 'files', 'expansions')


def transform(tree, origin, span):
    if isinstance(tree, list):
        return [transform(item, origin, span) for item in tree]
    if not isinstance(tree, dict):
        return tree
    located = tree.get('kind') in NODE_KINDS
    result = {}
    for field, value in tree.items():
        if located and value is not None and field in ('origin', 'span'):
            result[field] = origin(value) if field == 'origin' else span(value)
        else:
            result[field] = transform(value, origin, span)
    return result


def split_tree(tree, identifier):
    tables = {name: [] for name in TABLES}
    indices = {name: {} for name in TABLES}

    def intern(table, value):
        key = BSON.encode(value) if isinstance(value, dict) else value
        index = indices[table].get(key)
        if index is None:
            index = len(tables[table])
            indices[table][key] = index
            tables[table].append(value)
        return index

    def origin(value):
        row = {key: intern(ORIGIN_FIELDS[key], val) if val is not None and key in ORIGIN_FIELDS else val
               for key, val in value.items()}
        return intern('origins', row)

    compact = transform(tree, origin, lambda value: intern('spans', value))
    return compact, {'_id': identifier, **tables}


def restore_tree(document, locations):
    if BSON.encode({'_id': document['_id']}) != BSON.encode({'_id': locations['_id']}):
        raise BuildError('wrong_provenance', 'Source locations belong to another object')

    def resolve(table, index):
        values = locations.get(table)
        if not isinstance(values, list) or type(index) is not int or not 0 <= index < len(values):
            raise BuildError('broken_reference', f'Invalid {table} reference {index!r} at {document["_id"]!r}')
        return values[index]

    def origin(index):
        row = resolve('origins', index)
        if not isinstance(row, dict):
            raise BuildError('broken_reference', f'Invalid origin at {document["_id"]!r}')
        return {key: resolve(ORIGIN_FIELDS[key], val) if val is not None and key in ORIGIN_FIELDS else val
                for key, val in row.items()}

    return transform(document['tree'], origin, lambda index: resolve('spans', index))
