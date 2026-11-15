"""Replace a scalar reference with one scoped calculation node."""

from dataclasses import asdict

from ..nodes import Block, ScriptValue, Source
from ..inlining.text import slice_source
from ..inlining.substitution import substitute
from ..parser import parse_source
from ..traversal import walk
from ..variables.rules import fail
from .references import candidate, invocation


class AliasSource(Source):
    def __init__(self, value, node, environment):
        super().__init__(value.raw, node.origin['file'], node.origin['root'])
        self.site, self.environment = node.origin, environment

    def origin(self, start, end):
        return dict(self.site, generated_span=asdict(self.span(start, end)))


def reference_source(context, node, source, syntax):
    if node.quoted:
        return None
    payload = slice_source(source, node.span.start, node.span.end)
    if context.variables and (name := context.variables.rules.reference(node)):
        value = context.variables.resolve(node, name, source.environment)
        if value.quoted:
            return None
        payload = AliasSource(value, node, node.environment or source.environment)
    if not candidate(payload, syntax, context.library.value_options, context.library.options['name_case_sensitive']):
        return None
    if context.variables and context.variables.rules.reference(node):
        context.variables.counts['references'] += 1
        context.variables.counts['substituted'] += 1
    return payload


def expand_value(context, node, payload, syntax, record, frame):
    library = context.library
    name, scope, arguments, bindings = invocation(payload, syntax, library.value_options, library.options)
    key = library.key(name)
    context.identify(frame, ('script_value', key), name, 'scripted_cycle')
    definition = library.values.get(key)
    if definition is None:
        fail('unknown_script_value', f'Unknown script value: {name}', node)
    record.update(target=dict(name=definition.name, file=definition.node.origin['file'],
                              span=asdict(definition.node.span)),
                  invocation=dict(operator=None, form='arguments' if arguments else 'reference', raw=payload.text),
                  arguments=arguments, directives=[])
    expanded, used = substitute(definition.source, bindings, syntax, library.options, record['id'],
                                lambda text: context.control(text, syntax), context.parameter_counts)
    document = parse_source(expanded, syntax)
    context.account(document.items)
    context.remember(document)
    context.sequence(document.items, expanded, syntax)
    if context.variables:
        for item in walk(document.items):
            if context.variables.rules.declaration(item):
                fail('nested_static_declaration', 'Static declarations are not allowed in a named body', item.key)
    context.unused(bindings, used, name, record, node)
    origin = dict(node.origin, expansion_id=record['id'], synthetic=True)
    context.account_extra(2)
    result = ScriptValue(scope, Block(document.items, node.span, origin=origin), node.span, origin=origin)
    record['_node'] = result
    return result
