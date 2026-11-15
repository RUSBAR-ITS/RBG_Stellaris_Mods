"""Expand named bodies while preserving trigger result boundaries."""

from dataclasses import asdict

from ..nodes import Block, LogicalOperation, Scalar, ScriptedTriggerTest
from ..parser import parse_source
from ..inlining.substitution import substitute
from ..traversal import walk
from ..variables.rules import fail
from .binding import invocation


def logical(name, items, node, origin, syntax):
    actual = syntax.logical_name(name)
    if actual is None:
        raise ValueError(f'Missing required logical operator: {name}')
    label = Scalar(name, name, False, (), node.span, origin=origin)
    body = Block(items, node.span, origin=origin)
    return LogicalOperation(actual, label, syntax.logical_operators['assignment_operator'], body,
                            node.span, origin=origin)


def remove_directives(items, context):
    kept, removed, boundaries = [], [], [0]
    names = context.library.options['definition_directives']
    for item in items:
        if isinstance(item, Scalar) and not item.quoted and item.text in names:
            removed.append(item.text)
        else:
            kept.append(item)
        boundaries.append(len(kept))
    for record in context.records:
        if record.get('_items') is items:
            start, count = record['_index'], record['_count']
            record['_index'] = boundaries[start]
            record['_count'] = boundaries[start + count] - boundaries[start]
    items[:] = kept
    return removed


def expand_named(context, definition, node, source, syntax, record):
    options = context.library.options
    form, value, raw, arguments, bindings = invocation(node, source, syntax, options,
                                                       lambda text: context.control(text, syntax))
    record.update(target=dict(name=definition.name, file=definition.node.origin['file'],
                              span=asdict(definition.node.span)),
                  invocation=dict(operator=node.operator, form=form, raw=raw),
                  arguments=arguments, directives=[])
    if definition.kind == 'scripted_effect' and (form == 'test' or form == 'boolean' and value.casefold() != 'yes'):
        source.fail('unsupported_scripted_call', 'Effects require yes or an argument block', node.span.start)
    expanded, used = substitute(definition.source, bindings, syntax, options, record['id'],
                                lambda text: context.control(text, syntax), context.parameter_counts)
    document = parse_source(expanded, syntax)
    context.account(document.items)
    context.remember(document)
    context.sequence(document.items, expanded, syntax)
    record['directives'] = remove_directives(document.items, context)
    if context.variables:
        for item in walk(document.items):
            if context.variables.rules.declaration(item):
                fail('nested_static_declaration', 'Static declarations are not allowed in a named body', item.key)
    context.unused(bindings, used, definition.name, record, node)
    if definition.kind == 'scripted_effect':
        return document.items
    origin = dict(node.origin, expansion_id=record['id'], synthetic=True)
    if form == 'test':
        context.library.counts['scripted_trigger']['tests'] += 1
        context.account_extra(2)
        value = context.children(node.value, source, syntax)
        return [ScriptedTriggerTest(node.operator, value,
                Block(document.items, node.span, origin=origin), node.span, origin=origin)]
    positive = logical('AND', document.items, node, origin, syntax)
    context.account_extra(3)
    if form == 'boolean' and value.casefold() == 'no':
        context.account_extra(3)
        return [logical('NOT', [positive], node, origin, syntax)]
    return [positive]
