"""Mapped text retains template notation and substituted argument provenance."""

from bisect import bisect_right
from dataclasses import asdict, dataclass

from ..nodes import Source


@dataclass
class Piece:
    text: str
    source: Source
    start: int
    end: int
    argument: Source | None = None


class MappedSource(Source):
    def __init__(self, pieces, base, call_id=None):
        super().__init__("".join(piece.text for piece in pieces), base.file, base.root, call_id)
        self.pieces, self.base = pieces, base
        self.starts = []
        offset = 0
        for piece in pieces:
            self.starts.append(offset)
            offset += len(piece.text)

    def environment_at(self, start, end):
        environments = []
        for piece, left, right in self.portions(start, end):
            if right <= left:
                continue
            value = (piece.argument.environment_at(left, right) if piece.argument is not None
                     else piece.source.environment_at(piece.start + left, piece.start + right))
            for environment in value if isinstance(value, tuple) else (value,):
                if environment is not None and environment not in environments:
                    environments.append(environment)
        return environments[0] if len(environments) == 1 else tuple(environments) or self.environment

    def portions(self, start, end):
        first = max(0, bisect_right(self.starts, start) - 1)
        for index in range(first, len(self.pieces)):
            piece, offset = self.pieces[index], self.starts[index]
            if offset > end or (offset == end and end > start):
                break
            left, right = max(0, start - offset), min(len(piece.text), end - offset)
            if right >= left:
                yield piece, left, right

    def original_text(self, start, end):
        result = []
        for piece, left, right in self.portions(start, end):
            if piece.argument is not None and (left != 0 or right != len(piece.text)):
                result.append(piece.argument.original_text(left, right))
            elif piece.argument is None and len(piece.text) == piece.end - piece.start:
                result.append(piece.source.original_text(piece.start + left, piece.start + right))
            else:
                result.append(piece.source.original_text(piece.start, piece.end))
        return "".join(result)

    def origin(self, start, end):
        fragments = []
        for piece, left, right in self.portions(start, end):
            if piece.argument is not None:
                origin = piece.argument.origin(left, right)
                origin = dict(origin, placeholder=piece.source.origin(piece.start, piece.end))
            else:
                origin = piece.source.origin(piece.start + left, piece.start + right)
            if origin not in fragments:
                fragments.append(origin)
        origin = dict(fragments[0] if fragments else self.base.origin(0, 0))
        origin.update(expansion_id=self.call_id, generated_span=asdict(self.span(start, end)))
        if len(fragments) > 1:
            origin['fragments'] = fragments
        return origin


def slice_source(source, start, end):
    return MappedSource([Piece(source.text[start:end], source, start, end)], source, source.call_id)


def argument_source(source, scalar, syntax):
    width = len(syntax.lexical["string"]["quote"]) if scalar.quoted else 0
    start, end = scalar.span.start + width, scalar.span.end - width
    if not scalar.quoted:
        return slice_source(source, start, end)
    quote, escape = syntax.lexical["string"]["quote"], syntax.lexical["string"]["escape"]
    pieces, cursor, chunk = [], start, start
    while cursor < end:
        if source.text.startswith(escape, cursor):
            after = cursor + len(escape)
            marker = next((v for v in (quote, escape) if source.text.startswith(v, after)), None)
            if marker:
                pieces.append(Piece(source.text[chunk:cursor], source, chunk, cursor))
                pieces.append(Piece(marker, source, after, after + len(marker)))
                cursor = chunk = after + len(marker)
                continue
        cursor += 1
    pieces.append(Piece(source.text[chunk:end], source, chunk, end))
    return MappedSource(pieces, source, source.call_id)
