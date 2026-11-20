"""Persist syntax trees without interpreting game names or evaluating values."""

from dataclasses import fields, is_dataclass

from document_package.errors import BuildError
from .nodes import (Assignment, Block, Conditional, Formula, Located,
                    LogicalOperation, Scalar, TaggedBlock, ScriptedTriggerTest, ScriptValue)

KINDS = {Scalar: "scalar", Formula: "formula", Block: "block",
         TaggedBlock: "tagged_block", Conditional: "conditional",
         Assignment: "assignment", LogicalOperation: "logical_operation",
         ScriptedTriggerTest: "scripted_trigger_test", ScriptValue: "script_value"}
CHILDREN = {"scalar": (), "formula": (), "block": ("items",),
            "conditional": ("items",), "tagged_block": ("tag", "block"),
            "assignment": ("key", "value"),
            "logical_operation": ("name", "body"), "scripted_trigger_test": ("value", "body"), "script_value": ("body",)}


def encode(value, identifier_offsets=None):
    if isinstance(value, Located):
        kind = KINDS.get(type(value))
        if kind is None:
            raise BuildError("unsupported_node", f"Cannot persist {type(value).__name__}")
        return {"kind": kind, **{field.name: encode(getattr(value, field.name), identifier_offsets)
                                 for field in fields(value) if field.name != 'environment'}}
    if is_dataclass(value):
        return {field.name: encode(getattr(value, field.name), identifier_offsets) for field in fields(value)}
    if isinstance(value, (tuple, list)):
        return [encode(item, identifier_offsets) for item in value]
    if isinstance(value, dict):
        result = {key: encode(item, identifier_offsets) for key, item in value.items()}
        if identifier_offsets:
            for key in ('id', 'parent_id', 'expansion_id', 'call_id'):
                item = result.get(key)
                if isinstance(item, str):
                    prefix, _, number = item.rpartition('_')
                    if prefix in identifier_offsets and number.isdecimal():
                        result[key] = f'{prefix}_{int(number) + identifier_offsets[prefix]}'
        return result
    return value


def serialize_document(document, identifier_offsets=None):
    return {"source": {"root": document.source.root, "file": document.source.file or "<text>"},
            "items": encode(document.items, identifier_offsets), "metadata": encode(document.metadata, identifier_offsets)}


def walk_nodes(items):
    """Yield all syntax nodes, including keys, never walking service metadata."""
    stack = [(f"/items/{index}", item) for index, item in reversed(list(enumerate(items)))]
    while stack:
        path, node = stack.pop()
        yield path, node
        children = []
        for field in CHILDREN[node["kind"]]:
            value = node[field]
            if isinstance(value, list):
                children.extend((f"{path}/{field}/{index}", item) for index, item in enumerate(value))
            else:
                children.append((f"{path}/{field}", value))
        stack.extend(reversed(children))
