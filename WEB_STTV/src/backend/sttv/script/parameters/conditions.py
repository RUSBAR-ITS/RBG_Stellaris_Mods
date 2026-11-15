"""Select template fragments without binding or opening discarded content."""

from ..lexer import Lexer
from ..inlining.text import MappedSource, Piece


def select(source, bindings, syntax, options, call_id, control, counters):
    pieces, stack, used, cursor = [], [True], set(), 0
    spec = syntax.constructs['conditional']
    for token in Lexer(source, syntax).tokens():
        if token.kind not in ('conditional', 'conditional_close'):
            continue
        if stack[-1]:
            pieces.append(Piece(source.text[cursor:token.span.start], source, cursor, token.span.start))
        if token.kind == 'conditional':
            header = token.raw[len(spec['open']):-len(spec['header_close'])]
            negative = header.startswith(spec['negation'])
            name = header.removeprefix(spec['negation'])
            key = name if options['parameter_case_sensitive'] else name.casefold()
            enabled = False
            if stack[-1]:
                argument = bindings.get(key)
                if argument is not None:
                    used.add(key)
                enabled = argument is not None and control(argument).casefold() != 'no'
                enabled = not enabled if negative else enabled
                counters['retained_fragments' if enabled else 'discarded_fragments'] += 1
            stack.append(stack[-1] and enabled)
        else:
            if len(stack) == 1:
                source.fail('invalid_conditional', 'Unexpected conditional closer', token.span.start)
            stack.pop()
        cursor = token.span.end
    if len(stack) != 1:
        source.fail('unterminated_conditional', 'Unterminated conditional fragment', cursor)
    if cursor == 0:
        return source, used
    pieces.append(Piece(source.text[cursor:], source, cursor, len(source.text)))
    return MappedSource(pieces, source, call_id), used
