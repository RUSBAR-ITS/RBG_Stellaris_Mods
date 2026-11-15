"""Explicit projection into the current database representation, never lossy fallback."""

from dataclasses import dataclass

from .nodes import Assignment, Block, Scalar


@dataclass(frozen=True)
class DataEntry:
    key: str | None
    operator: str | None
    value: str | list
    line: int
    parameters: tuple = ()


def data_entries(document, purpose="database"):
    def convert(item):
        if isinstance(item, Assignment):
            fragments = item.key.parameters + (item.value.parameters if isinstance(item.value, Scalar) else ())
            return DataEntry(item.key.text, item.operator, value(item.value), item.span.line, fragments)
        if isinstance(item, Scalar):
            return DataEntry(None, None, item.text, item.span.line, item.parameters)
        reject(item)

    def reject(item):
        document.source.fail(f"unsupported_{purpose}_form",
                             f"Cannot represent {type(item).__name__} in {purpose}", item.span.start)

    def value(item):
        if isinstance(item, Scalar):
            return item.text
        if isinstance(item, Block):
            return [convert(child) for child in item.items]
        reject(item)

    return [convert(item) for item in document.items]


def script_block(entries):
    return {"entries": [
        {"key": entry.key, "operator": entry.operator,
         "value": script_block(entry.value) if isinstance(entry.value, list) else entry.value,
         "line": entry.line}
        for entry in entries
    ]}
