"""Prepare the supported database schema subset into validation closures."""

from sttv.common.errors import BuildError
from .choices import accepts, conditional_rules, union_rule
from .primitives import invalid, pointer, scalar_rules

KEYWORDS = {'$schema', '$defs', '$ref', 'type', 'const', 'enum', 'required', 'properties',
            'additionalProperties', 'items', 'minimum', 'minLength', 'maxLength', 'pattern',
            'minItems', 'maxItems', 'minProperties', 'uniqueItems', 'anyOf', 'allOf', 'if', 'then', 'else', 'propertyNames'}


class Compiler:
    def __init__(self, schema):
        self.schema, self.cache, self.retained = schema, {}, []
        definitions = schema.get('$defs', {})
        self.node_schemas = {id(value) for value in definitions.values()
                             if 'kind' in value.get('properties', {}) and 'span' in value.get('properties', {})}
        self.origin = id(definitions.get('origin'))
        for value in definitions.values():
            self.prepare(value)
        self.check = self.prepare(schema)

    def resolve(self, schema):
        if set(schema) == {'$ref'}:
            reference = schema['$ref']
            if not reference.startswith('#/$defs/') or reference[8:] not in self.schema.get('$defs', {}):
                raise BuildError('unsupported_schema', f'Unsupported schema reference: {reference}')
            return self.schema['$defs'][reference[8:]]
        return schema

    def prepare(self, schema):
        if isinstance(schema, bool):
            def boolean(value, path, context):
                if not schema:
                    invalid(path, 'Value is forbidden')
            return boolean
        if not isinstance(schema, dict) or set(schema) - KEYWORDS:
            raise BuildError('unsupported_schema', f'Unsupported schema constraints: {set(schema) - KEYWORDS}')
        identity = id(schema)
        if identity in self.cache:
            return self.cache[identity]
        self.retained.append(schema)
        pending = []
        def deferred(value, path='', context=None):
            return pending[0](value, path, context)
        self.cache[identity] = deferred
        pending.append(self.build(schema))
        return deferred

    def build(self, schema):
        checks = scalar_rules(schema)
        actions = []
        if '$ref' in schema:
            actions.append(self.prepare(self.resolve({'$ref': schema['$ref']})))
        if 'anyOf' in schema:
            actions.append(union_rule(schema['anyOf'], self))
        if 'allOf' in schema:
            actions.append(conditional_rules(schema['allOf'], self))
        if 'if' in schema:
            condition = self.prepare(schema['if'])
            yes, no = self.prepare(schema.get('then', True)), self.prepare(schema.get('else', True))
            def conditional(value, path, context):
                (yes if accepts(condition, value, path) else no)(value, path, context)
            actions.append(conditional)
        properties = {name: self.prepare(value) for name, value in schema.get('properties', {}).items()}
        required = set(schema.get('required', []))
        allowed = set(properties)
        extra = schema.get('additionalProperties', True)
        additional = self.prepare(extra) if isinstance(extra, dict) else None
        item = self.prepare(schema['items']) if 'items' in schema else None
        key_check = self.prepare(schema['propertyNames']) if 'propertyNames' in schema else None
        node, origin = id(schema) in self.node_schemas, id(schema) == self.origin
        def validate(value, path, context):
            for check, message in checks:
                if not check(value):
                    invalid(path, message)
            if isinstance(value, dict):
                if key_check is not None:
                    for name in value:
                        key_check(name, pointer(path, name), None)
                missing = required - value.keys()
                if missing:
                    invalid(path, f'Missing required fields: {sorted(missing)}')
                if extra is False and value.keys() - allowed:
                    invalid(path, f'Unexpected fields: {sorted(value.keys() - allowed)}')
                for name, check in properties.items():
                    if name in value:
                        check(value[name], pointer(path, name), context)
                if additional is not None:
                    for name in value.keys() - allowed:
                        additional(value[name], pointer(path, name), context)
            if item is not None and isinstance(value, list):
                for index, child in enumerate(value):
                    item(child, f'{path}/{index}', context)
            for action in actions:
                action(value, path, context)
            if context is not None:
                if node:
                    context.node(path, value)
                elif origin:
                    context.origin(path, value)
        return validate
