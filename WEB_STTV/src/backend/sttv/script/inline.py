"""Expansion boundary for opaque inline calls; expansion is deliberately deferred."""

from dataclasses import dataclass

from .nodes import Source, Span


@dataclass(frozen=True)
class InlineScriptValue:
    raw: str
    form: str
    span: Span


def expand_inline_script(value: InlineScriptValue, source: Source) -> list:
    """Skip the entire invocation without reading or interpreting its payload."""
    return []
