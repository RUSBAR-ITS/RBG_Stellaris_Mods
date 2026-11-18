"""Perform one parameter substitution pass before structural parsing."""

from ..delimiters import parameters
from ..lexer import Lexer
from ..parameters.conditions import select
from .text import MappedSource, Piece


def substitute(source, bindings, syntax, options, call_id, control=None, counters=None, missing=None):
    counters = counters if counters is not None else dict(defaults=0, retained_fragments=0, discarded_fragments=0)
    source, used = select(source, bindings, syntax, options, call_id,
                          control or (lambda argument: argument.text), counters)
    plan = getattr(source, 'plan', None)
    if plan is not None and not plan['parameter_count']:
        return MappedSource([Piece(source.text, source, 0, len(source.text))], source, call_id), used
    pieces, cursor = [], 0
    bindings = dict(bindings)
    for token in Lexer(source, syntax).tokens():
        if token.kind in ("comment", "bom"):
            continue
        for parameter in parameters(source, token.span.start, token.span.end, syntax, strict=False):
            name = parameter.name if options["parameter_case_sensitive"] else parameter.name.casefold()
            start, end = parameter.span.start, parameter.span.end
            pieces.append(Piece(source.text[cursor:start], source, cursor, start))
            if name not in bindings and parameter.default is None and missing is not None:
                correction = missing(parameter, token, source, bindings)
                if correction is not None:
                    bindings[name], dependencies = correction
                    used.update(dependencies)
            if name in bindings:
                argument = bindings[name]
                pieces.append(Piece(argument.text, source, start, end, argument))
                used.add(name)
            elif parameter.default is not None:
                pieces.append(Piece(parameter.default, source, start, end))
                counters['defaults'] += 1
            else:
                source.fail("missing_inline_parameter", f"Missing argument: {parameter.name}", start)
            cursor = end
    pieces.append(Piece(source.text[cursor:], source, cursor, len(source.text)))
    result = MappedSource(pieces, source, call_id)
    for token in Lexer(result, syntax).tokens():
        if token.kind == "comment":
            continue
        remaining = parameters(result, token.span.start, token.span.end, syntax, strict=False)
        if remaining:
            result.fail("unresolved_inline_parameter", f"Unresolved parameter: {remaining[0].name}", remaining[0].span.start)
    return result, used
