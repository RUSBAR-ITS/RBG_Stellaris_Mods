"""Perform one parameter substitution pass before structural parsing."""

from ..delimiters import parameters
from ..lexer import Lexer
from .text import MappedSource, Piece


def substitute(source, bindings, syntax, options, call_id):
    pieces, cursor, used = [], 0, set()
    for token in Lexer(source, syntax).tokens():
        if token.kind in ("comment", "bom"):
            continue
        if token.kind == "conditional":
            source.fail("unsupported_inline_conditional", "Conditional template fragments are unsupported", token.span.start)
        for parameter in parameters(source, token.span.start, token.span.end, syntax, strict=False):
            if parameter.default is not None:
                source.fail("unsupported_inline_default", "Default template parameters are unsupported", parameter.span.start)
            name = parameter.name if options["parameter_case_sensitive"] else parameter.name.casefold()
            if name not in bindings:
                source.fail("missing_inline_parameter", f"Missing argument: {parameter.name}", parameter.span.start)
            start, end = parameter.span.start, parameter.span.end
            pieces.append(Piece(source.text[cursor:start], source, cursor, start))
            argument = bindings[name]
            pieces.append(Piece(argument.text, source, start, end, argument))
            used.add(name)
            cursor = end
    pieces.append(Piece(source.text[cursor:], source, cursor, len(source.text)))
    result = MappedSource(pieces, source, call_id)
    for token in Lexer(result, syntax).tokens():
        if token.kind == "comment":
            continue
        if token.kind == "conditional":
            result.fail("unsupported_inline_conditional", "Conditional template fragments are unsupported", token.span.start)
        remaining = parameters(result, token.span.start, token.span.end, syntax, strict=False)
        if remaining:
            result.fail("unresolved_inline_parameter", f"Unresolved parameter: {remaining[0].name}", remaining[0].span.start)
    return result, used
