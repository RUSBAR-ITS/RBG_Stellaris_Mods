"""Prepared branch selection without repeated recursive schema interpretation."""

from .primitives import invalid, matches
from sttv.common.errors import BuildError


def accepts(check, value, path):
    try:
        check(value, path, None)
        return True
    except BuildError:
        return False


def union_rule(schemas, compiler):
    checks = [compiler.prepare(schema) for schema in schemas]
    resolved = [compiler.resolve(schema) for schema in schemas]
    kinds = [schema.get('properties', {}).get('kind', {}).get('const') for schema in resolved]
    if all(isinstance(kind, str) for kind in kinds) and len(set(kinds)) == len(kinds):
        table = dict(zip(kinds, checks))
        def dispatch(value, path, context):
            kind = value.get('kind') if isinstance(value, dict) else None
            check = table.get(kind) if isinstance(kind, str) else None
            if check is None:
                invalid(path, 'Unexpected node kind')
            check(value, path, context)
        return dispatch
    types = [schema.get('type') for schema in resolved]
    if all(isinstance(kind, str) for kind in types) and len(set(types)) == len(types) and not {'integer', 'number'} <= set(types):
        def by_type(value, path, context):
            for kind, check in zip(types, checks):
                if matches(value, kind):
                    check(value, path, context)
                    return
            invalid(path, 'No allowed value type')
        return by_type
    def alternatives(value, path, context):
        for check in checks:
            if accepts(check, value, path):
                if context is not None:
                    check(value, path, context)
                return
        invalid(path, 'No matching alternative')
    return alternatives


def conditional_rules(schemas, compiler):
    checks = [compiler.prepare(schema) for schema in schemas]
    cases = {}
    for schema in schemas:
        condition = schema.get('if', {})
        properties = condition.get('properties', {})
        kind_rule = properties.get('kind', {})
        kind = kind_rule.get('const')
        if (set(schema) != {'if', 'then'} or set(condition) != {'properties'}
                or set(properties) != {'kind'} or set(kind_rule) != {'const'}
                or not isinstance(kind, str) or kind in cases):
            break
        cases[kind] = compiler.prepare(schema['then'])
    else:
        def dispatch(value, path, context):
            if isinstance(value, dict) and 'kind' in value:
                kind = value['kind']
                check = cases.get(kind) if isinstance(kind, str) else None
                if check is not None:
                    check(value, path, context)
            else:
                for check in checks:
                    check(value, path, context)
        return dispatch
    def all_checks(value, path, context):
        for check in checks:
            check(value, path, context)
    return all_checks
