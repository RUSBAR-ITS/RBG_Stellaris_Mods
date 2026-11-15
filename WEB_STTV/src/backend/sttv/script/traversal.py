"""Traverse syntax only; service metadata is never part of the working tree."""

from dataclasses import fields, replace

from .nodes import Located


def locate(node, source):
    changes = {"origin": source.origin(node.span.start, node.span.end)}
    for field in fields(node):
        value = getattr(node, field.name)
        if isinstance(value, Located):
            changes[field.name] = locate(value, source)
        elif field.name == "items":
            changes[field.name] = [locate(child, source) for child in value]
    return replace(node, **changes)


def sequences(items, path="/items"):
    yield path, items
    for index, node in enumerate(items):
        yield from node_sequences(node, f"{path}/{index}")


def node_sequences(node, path):
    for field in fields(node):
        value = getattr(node, field.name)
        if field.name == "items":
            yield from sequences(value, path + "/items")
        elif isinstance(value, Located):
            yield from node_sequences(value, path + "/" + field.name)


def walk(items):
    for _, sequence in sequences(items):
        yield from sequence


def source_location(origin):
    return {"root": origin["root"], "file": origin["file"],
            "line": origin["span"]["line"], "column": origin["span"]["column"],
            "inline_call_id": origin["inline_call_id"]}
