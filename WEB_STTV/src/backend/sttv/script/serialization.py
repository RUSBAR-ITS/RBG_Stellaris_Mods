"""Explicit projection into the current database representation, never lossy fallback."""

from dataclasses import dataclass

from sttv.common.errors import BuildError
from .nodes import Assignment, Block, InlineInvocation, LogicalOperation, Scalar
from .traversal import source_location


@dataclass(frozen=True)
class DataEntry:
    key: str | None
    operator: str | None
    value: str | list
    line: int
    parameters: tuple = ()
    origin: dict | None = None


def data_entries(document, purpose="database", syntax=None):
    def convert(item):
        if isinstance(item, InlineInvocation) and purpose == "analysis_template":
            from .inlining.text import slice_source
            from .parser import parse_source
            payload = parse_source(slice_source(document.source, item.value_span.start, item.value_span.end),
                                   syntax, specials=False).items[0]
            return DataEntry(syntax.constructs["inline_script"]["keyword"], "=", value(payload),
                             item.origin["span"]["line"], origin=item.origin)
        if isinstance(item, LogicalOperation):
            return DataEntry(item.operator, item.assignment_operator, value(item.body),
                             item.origin["span"]["line"], origin=item.origin)
        if isinstance(item, Assignment):
            fragments = item.key.parameters + (item.value.parameters if isinstance(item.value, Scalar) else ())
            return DataEntry(item.key.text, item.operator, value(item.value),
                             item.origin["span"]["line"], fragments, item.origin)
        if isinstance(item, Scalar):
            return DataEntry(None, None, item.text, item.origin["span"]["line"], item.parameters, item.origin)
        reject(item)

    def reject(item):
        error = BuildError(f"unsupported_{purpose}_form",
                           f"Cannot represent {type(item).__name__} in {purpose}",
                           line=item.origin["span"]["line"])
        error.provenance = item.origin
        raise error

    def value(item):
        if isinstance(item, Scalar):
            return item.text
        if isinstance(item, Block):
            return [convert(child) for child in item.items]
        reject(item)

    return [convert(item) for item in document.items]


def script_block(entries, tracker=None, path=""):
    if tracker:
        for index, entry in enumerate(entries):
            tracker.add(entry, f"{path}/entries/{index}")
    return {"entries": [
        {"key": entry.key, "operator": entry.operator,
         "value": script_block(entry.value, tracker, f"{path}/entries/{index}/value")
                  if isinstance(entry.value, list) else entry.value,
         "source": source_location(entry.origin)}
        for index, entry in enumerate(entries)
    ]}
