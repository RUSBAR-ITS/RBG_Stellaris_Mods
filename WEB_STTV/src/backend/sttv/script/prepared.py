"""Reusable lexical plans and constant syntax, without invocation state."""

from dataclasses import asdict
from bisect import bisect_left

from .delimiters import parameters
from .lexer import Lexer


def prepare(source, syntax):
    if getattr(source, 'plan', None) is not None:
        return source
    rows, parameter_count, conditional = [], 0, False
    for token in Lexer(source, syntax).tokens():
        found = () if token.kind in ('comment', 'bom') else parameters(
            source, token.span.start, token.span.end, syntax, strict=False)
        rows.append({'start': token.span.start, 'end': token.span.end, 'kind': token.kind,
                     'parameters': [asdict(p) for p in found]})
        parameter_count += len(found)
        conditional |= token.kind == 'conditional'
    source.plan = {'tokens': rows, 'parameter_count': parameter_count,
                   'conditional': conditional, 'items': None}
    install(source)
    if not parameter_count and not conditional:
        from .parser import Parser
        from sttv.common.errors import BuildError
        try:
            source.plan['items'] = Parser(source, syntax).sequence()[0]
        except BuildError:
            # Syntax errors in unused inline bodies retain their call-time boundary.
            pass
    return source


def install(source):
    from .nodes import Parameter, Span
    plan = getattr(source, 'plan', None)
    source.lexical_plan, source.parameter_plan = {}, {}
    source.lexical_starts = []
    if plan is None:
        return
    for row in plan['tokens']:
        start, end = row['start'], row['end']
        source.lexical_plan[start] = (row['kind'], end)
        if row['kind'] not in ('comment', 'bom'):
            found = tuple(Parameter(p['name'], p['default'], p['raw'], Span(**p['span']))
                          for p in row['parameters'])
            source.parameter_plan[start, end] = found
    source.lexical_starts = sorted(source.lexical_plan)


def mapped_plan(result, pieces):
    """Reuse complete tokens only; relex both sides of every edited boundary."""
    if len(pieces) == 1:
        piece = pieces[0]
        if piece.argument is None and piece.start == 0 and piece.end == len(piece.source.text):
            result.plan = getattr(piece.source, 'plan', None)
            result.lexical_plan = getattr(piece.source, 'lexical_plan', {})
            result.parameter_plan = getattr(piece.source, 'parameter_plan', {})
            result.lexical_starts = getattr(piece.source, 'lexical_starts', [])
            return
    result.lexical_plan, result.parameter_plan = {}, {}
    offset = 0
    for piece in pieces:
        source = piece.source
        unchanged = piece.argument is None and piece.text == source.text[piece.start:piece.end]
        if unchanged:
            delta = offset - piece.start
            starts = getattr(source, 'lexical_starts', [])
            for start in starts[bisect_left(starts, piece.start):bisect_left(starts, piece.end)]:
                kind, end = source.lexical_plan[start]
                if start < piece.start or end > piece.end:
                    continue
                if (start == piece.start and offset > 0) or (end == piece.end and offset + len(piece.text) < len(result.text)):
                    continue
                a, b = start + delta, end + delta
                result.lexical_plan[a] = kind, b
                found = getattr(source, 'parameter_plan', {}).get((start, end))
                if found is not None:
                    from dataclasses import replace
                    result.parameter_plan[a, b] = tuple(replace(p, span=result.span(
                        p.span.start + delta, p.span.end + delta)) for p in found)
        offset += len(piece.text)
    result.lexical_starts = sorted(result.lexical_plan)
