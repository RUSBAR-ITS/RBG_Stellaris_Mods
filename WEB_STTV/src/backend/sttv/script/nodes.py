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
    def __init__(self, text, file=None, root="STELLARIS_ROOT", call_id=None):
        self.text, self.file = text, file
        self.root, self.call_id = root, call_id
        self.lines = [0, *(i + 1 for i, char in enumerate(text) if char == "\n")]
        self.environment = None

    def environment_at(self, start, end):
        return self.environment

    def original_text(self, start, end):
        return self.text[start:end]

    def origin(self, start, end):
        from dataclasses import asdict
        return {"root": self.root, "file": self.file or "<text>",
                "span": asdict(self.span(start, end)), "expansion_id": self.call_id}

    def span(self, start, end):
        first, last = bisect_right(self.lines, start), bisect_right(self.lines, end)
        return Span(start, end, first, start - self.lines[first - 1] + 1,
                    last, end - self.lines[last - 1] + 1)

    def fail(self, code, message, offset):
        origin = self.origin(offset, offset)
        span = origin["span"]
        location = f"{origin['file']}:{span['line']}:{span['column']}"
        error = BuildError(code, f"{location}: {message}", line=span["line"])
        error.column, error.offset, error.file = span["column"], offset, origin["file"]
        error.provenance = origin
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


@dataclass(frozen=True, kw_only=True)
class Located:
    origin: dict | None = None
    environment: object = None


@dataclass(frozen=True)
class Scalar(Located):
    raw: str
    text: str
    quoted: bool
    parameters: tuple[Parameter, ...]
    span: Span


@dataclass(frozen=True)
class Formula(Located):
    raw: str
    opener: str
    body: str
    span: Span


@dataclass(frozen=True)
class Block(Located):
    items: list
    span: Span


@dataclass(frozen=True)
class ScriptValue(Located):
    scope: str | None
    body: Block
    span: Span


@dataclass(frozen=True)
class TaggedBlock(Located):
    tag: Scalar
    block: Block
    span: Span


@dataclass(frozen=True)
class Conditional(Located):
    parameter: str
    negated: bool
    items: list
    span: Span


@dataclass(frozen=True)
class Assignment(Located):
    key: Scalar
    operator: str
    value: Scalar | Formula | Block | TaggedBlock | ScriptValue
    span: Span


@dataclass(frozen=True)
class LogicalOperation(Located):
    operator: str
    name: Scalar
    assignment_operator: str
    body: Block
    span: Span


@dataclass(frozen=True)
class InlineInvocation(Located):
    raw: str
    form: str
    span: Span
    value_span: Span


@dataclass(frozen=True)
class ScriptedTriggerTest(Located):
    operator: str
    value: Scalar | Formula | ScriptValue
    body: Block
    span: Span


@dataclass(frozen=True)
class Document:
    source: Source
    tokens: list[Token]
    items: list
    metadata: dict
