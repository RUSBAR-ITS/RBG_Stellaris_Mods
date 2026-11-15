"""Parse whole value references and retain mapped argument boundaries."""

from sttv.common.errors import BuildError
from sttv.common.schema import validate_schema
from ..delimiters import parameters
from ..inlining.text import slice_source


def validate_options(options, syntax):
    validate_schema(options, 'parser_script_values.schema.json')
    markers = [options[key] for key in ('reference_prefix', 'scope_separator', 'argument_separator')]
    forbidden = [syntax.lexical['line_comment'], *syntax.lexical['block'].values(),
                 *syntax.lexical['operators'], *syntax.lexical['string'].values(),
                 syntax.constructs['parameters']['open'], syntax.constructs['parameters']['close'],
                 *syntax.constructs['conditional'].values(),
                 *(v for item in syntax.constructs['formulas'] for v in item.values())]
    for index, marker in enumerate(markers):
        if (any(char.isspace() or char == '\ufeff' for char in marker)
                or any(value in marker or marker in value for value in forbidden if isinstance(value, str))
                or any(value in marker or marker in value for value in markers[:index])):
            raise BuildError('script_value_configuration', 'Conflicting reference markers')


def segments(source, syntax, separator):
    protected = {p.span.start: p.span.end for p in parameters(source, 0, len(source.text), syntax, strict=True)}
    result, start, cursor = [], 0, 0
    while cursor < len(source.text):
        if cursor in protected:
            cursor = protected[cursor]
        elif source.text.startswith(separator, cursor):
            result.append((start, cursor))
            start = cursor = cursor + len(separator)
        else:
            cursor += 1
    return [*result, (start, len(source.text))]


def head_position(head, options, sensitive):
    prefix, separator = options['reference_prefix'], options['scope_separator']
    normalized = head if sensitive else head.casefold()
    marker = prefix if sensitive else prefix.casefold()
    if normalized.startswith(marker):
        return 0
    scoped = separator + marker
    position = normalized.find(scoped)
    return position + len(separator) if position >= 0 else None


def candidate(source, syntax, options, sensitive):
    end = segments(source, syntax, options['argument_separator'])[0][1]
    return head_position(source.text[:end], options, sensitive) is not None


def invocation(source, syntax, options, shared):
    parts = segments(source, syntax, options['argument_separator'])
    head = source.text[:parts[0][1]]
    position = head_position(head, options, shared['name_case_sensitive'])
    prefix, separator = options['reference_prefix'], options['scope_separator']
    scope = head[:position - len(separator)] if position else None
    name = head[position + len(prefix):]
    if (not name or parameters(source, position + len(prefix), len(head), syntax, strict=True)
            or scope is not None and any(not item for item in scope.split(separator))):
        source.fail('invalid_script_value_reference', 'Expected a name and nonempty scope segments', 0)
    if len(parts) > 1 and (source.text[parts[-1][0]:] or len(parts) < 4 or len(parts) % 2):
        source.fail('invalid_script_value_arguments', 'Expected closed name/value pairs', 0)
    bindings, arguments = {}, []
    for index in range(1, len(parts) - 1, 2):
        left, right = parts[index]
        argument_name = source.text[left:right]
        if not argument_name or parameters(source, left, right, syntax, strict=True):
            source.fail('invalid_script_value_argument', 'Expected a literal parameter name', left)
        key = argument_name if shared['parameter_case_sensitive'] else argument_name.casefold()
        if key in bindings:
            source.fail('duplicate_scripted_argument', f'Repeated argument: {argument_name}', left)
        start, end = parts[index + 1]
        argument = slice_source(source, start, end)
        bindings[key] = argument
        arguments.append(dict(name=argument_name, raw=source.original_text(start, end), value=argument.text))
    return name, scope, arguments, bindings
