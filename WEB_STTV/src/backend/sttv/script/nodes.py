"""Lossless syntax nodes, independent of the technology database contract."""

from bisect import bisect_right
from dataclasses import dataclass

from sttv.common.errors import BuildError


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    line: int
    column: int
    end_line: int
    end_column: int


class Source:
    def __init__(self, text, file=None):
        self.text, self.file = text, file
        self.lines = [0, *(i + 1 for i, char in enumerate(text) if char == "\n")]

    def span(self, start, end):
        first, last = bisect_right(self.lines, start), bisect_right(self.lines, end)
        return Span(start, end, first, start - self.lines[first - 1] + 1,
                    last, end - self.lines[last - 1] + 1)

    def fail(self, code, message, offset):
        span = self.span(offset, offset)
        location = f"{self.file or '<text>'}:{span.line}:{span.column}"
        error = BuildError(code, f"{location}: {message}", line=span.line)
        error.column, error.offset, error.file = span.column, offset, self.file
        raise error


@dataclass(frozen=True)
class Token:
    kind: str
    raw: str
    span: Span


@dataclass(frozen=True)
class Parameter:
    name: str
    default: str | None
    raw: str
    span: Span


@dataclass(frozen=True)
class Scalar:
    raw: str
    text: str
    quoted: bool
    parameters: tuple[Parameter, ...]
    span: Span


@dataclass(frozen=True)
class Formula:
    raw: str
    opener: str
    body: str
    span: Span


@dataclass(frozen=True)
class Block:
    items: list
    span: Span


@dataclass(frozen=True)
class TaggedBlock:
    tag: Scalar
    block: Block
    span: Span


@dataclass(frozen=True)
class Conditional:
    parameter: str
    negated: bool
    items: list
    span: Span


@dataclass(frozen=True)
class Assignment:
    key: Scalar
    operator: str
    value: Scalar | Formula | Block | TaggedBlock
    span: Span


@dataclass(frozen=True)
class Document:
    source: Source
    tokens: list[Token]
    items: list
