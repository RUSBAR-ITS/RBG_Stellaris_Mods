"""Read inline arguments as scalars, without logical-operator classification."""

from ..nodes import Assignment, Block, Scalar
from ..parser import parse_source
from ..syntax import matches
from .text import argument_source, slice_source


def invocation(node, source, syntax, options):
    payload = slice_source(source, node.value_span.start, node.value_span.end)
    document = parse_source(payload, syntax, specials=False)
    if len(document.items) != 1:
        payload.fail("invalid_inline", "Expected one inline payload", 0)
    value = document.items[0]
    if node.form == "reference":
        if not isinstance(value, Scalar):
            payload.fail("invalid_inline", "Expected a scalar path", 0)
        return argument_source(payload, value, syntax), payload.original_text(0, len(payload.text)), [], {}
    if not isinstance(value, Block):
        payload.fail("invalid_inline", "Expected an argument block", 0)
    path, raw_path, arguments, bindings = None, None, [], {}
    sensitive = options["parameter_case_sensitive"]
    for item in value.items:
        if (not isinstance(item, Assignment) or item.operator != "="
                or item.key.quoted or item.key.parameters or not isinstance(item.value, Scalar)):
            payload.fail("invalid_inline", "Inline arguments must be named scalars using =", item.span.start)
        name = item.key.text
        text = argument_source(payload, item.value, syntax)
        raw = payload.original_text(item.value.span.start, item.value.span.end)
        if matches(name, options["path_field"], syntax.constructs["inline_script"]["case_sensitive"]):
            if path is not None:
                payload.fail("duplicate_inline_path", "Repeated inline path field", item.span.start)
            path, raw_path = text, raw
        else:
            key = name if sensitive else name.casefold()
            if key in bindings:
                payload.fail("duplicate_inline_argument", f"Repeated argument: {name}", item.span.start)
            bindings[key] = text
            arguments.append({"name": name, "raw": raw, "value": text.text})
    if path is None or not path.text:
        payload.fail("invalid_inline_path", "An inline call needs a nonempty path", 0)
    return path, raw_path, arguments, bindings
