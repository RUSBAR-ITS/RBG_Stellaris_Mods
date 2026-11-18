"""JSON value semantics and prepared scalar constraints."""

import math
import re

from sttv.common.errors import BuildError


def invalid(path, message):
    raise BuildError('schema_error', f'{path or "/"}: {message}', field_path=path or '/')


def freeze(value):
    if isinstance(value, dict):
        return ('object', tuple(sorted((key, freeze(item)) for key, item in value.items())))
    if isinstance(value, list):
        return ('array', tuple(map(freeze, value)))
    if isinstance(value, bool):
        return ('boolean', value)
    return (('number' if isinstance(value, (int, float)) else type(value).__name__), value)


TYPES = {'object': dict, 'array': list, 'string': str, 'boolean': bool, 'null': type(None)}


def matches(value, kind):
    if kind in TYPES:
        return isinstance(value, TYPES[kind])
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return kind == 'number' or isinstance(value, int) or math.isfinite(value) and value.is_integer()


def scalar_rules(schema):
    checks = []
    if 'type' in schema:
        kinds = schema['type'] if isinstance(schema['type'], list) else [schema['type']]
        checks.append((lambda value: any(matches(value, kind) for kind in kinds), 'Unexpected value type'))
    if 'const' in schema:
        expected = freeze(schema['const'])
        checks.append((lambda value: freeze(value) == expected, 'Unexpected constant'))
    if 'enum' in schema:
        values = {freeze(item) for item in schema['enum']}
        checks.append((lambda value: freeze(value) in values, 'Value is outside the enumeration'))
    for keyword, compare, applicable in (
            ('minimum', lambda value, bound: value >= bound, lambda value: matches(value, 'number')),
            ('minLength', lambda value, bound: len(value) >= bound, lambda value: isinstance(value, str)),
            ('maxLength', lambda value, bound: len(value) <= bound, lambda value: isinstance(value, str)),
            ('minItems', lambda value, bound: len(value) >= bound, lambda value: isinstance(value, list)),
            ('maxItems', lambda value, bound: len(value) <= bound, lambda value: isinstance(value, list)),
            ('minProperties', lambda value, bound: len(value) >= bound, lambda value: isinstance(value, dict))):
        if keyword in schema:
            bound = schema[keyword]
            checks.append((lambda value, b=bound, c=compare, a=applicable: not a(value) or c(value, b), keyword))
    if 'pattern' in schema:
        pattern = re.compile(schema['pattern'])
        checks.append((lambda value: not isinstance(value, str) or pattern.search(value) is not None,
                       'String does not match the required pattern'))
    if schema.get('uniqueItems'):
        checks.append((lambda value: not isinstance(value, list) or len({freeze(v) for v in value}) == len(value),
                       'Array items must be unique'))
    return checks


def pointer(path, key):
    return f'{path}/{str(key).replace("~", "~0").replace("/", "~1")}'
