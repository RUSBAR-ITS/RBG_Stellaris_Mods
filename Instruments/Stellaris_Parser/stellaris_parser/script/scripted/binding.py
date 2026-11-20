"""Read named-call arguments without treating argument keys as commands."""

from ..nodes import Assignment, Block, Formula, Scalar
from ..parser import parse_source
from ..inlining.text import argument_source, slice_source


def invocation(node, source, syntax, options, control):
    payload = slice_source(source, node.value.span.start, node.value.span.end)
    parsed = parse_source(payload, syntax, specials=False)
    value = parsed.items[0]
    raw = source.original_text(node.value.span.start, node.value.span.end)
    if not isinstance(value, Block):
        value_text = control(payload) if isinstance(value, Scalar) else payload.text
        form = 'boolean' if node.operator == '=' and value_text.casefold() in ('yes', 'no') else 'test'
        return form, value_text, raw, [], {}
    if node.operator != '=':
        source.fail('unsupported_scripted_call', 'Argument blocks require =', node.span.start)
    arguments, bindings = [], {}
    for item in value.items:
        if (not isinstance(item, Assignment) or item.operator != '=' or item.key.quoted
                or item.key.parameters or not isinstance(item.value, (Scalar, Formula, Block))):
            payload.fail('invalid_scripted_argument', 'Expected named textual argument', item.span.start)
        name = item.key.text
        key = name if options['parameter_case_sensitive'] else name.casefold()
        if key in bindings:
            payload.fail('duplicate_scripted_argument', f'Repeated argument: {name}', item.span.start)
        text = (argument_source(payload, item.value, syntax) if isinstance(item.value, Scalar)
                else slice_source(payload, item.value.span.start, item.value.span.end))
        bindings[key] = text
        arguments.append(dict(name=name, raw=payload.original_text(item.value.span.start, item.value.span.end),
                              value=text.text))
    return 'arguments', None, raw, arguments, bindings
