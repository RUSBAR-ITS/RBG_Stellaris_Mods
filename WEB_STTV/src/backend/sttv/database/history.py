"""Validate inline history against document-local tree positions and provenance."""

from sttv.common.errors import BuildError
from sttv.script.serialization import walk_nodes


def invalid(message):
    raise BuildError("invalid_inline_history", message)


def validate_origins(value, calls):
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            call = item.get("inline_call_id")
            if call is not None and call not in calls:
                invalid(f"Unknown invocation in provenance: {call}")
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)


def validate_history(document):
    records = document["metadata"]["inline_scripts"]
    calls = {record["id"]: record for record in records}
    if len(calls) != len(records):
        invalid("Duplicate invocation identifier")
    ancestors = {}
    for identifier in calls:
        trail, current = set(), identifier
        while current is not None:
            if current in trail or current not in calls:
                invalid("Cyclic or missing invocation parent")
            trail.add(current)
            current = calls[current]["parent_id"]
        ancestors[identifier] = trail
    containers = {"/items": document["items"]}
    for path, node in walk_nodes(document["items"]):
        if "items" in node:
            containers[path + "/items"] = node["items"]
        validate_origins(node["origin"], calls)
    for record in records:
        insertion = record["insertion"]
        sequence = containers.get(insertion["container"])
        start, count = insertion["index"], insertion["count"]
        if sequence is None or start + count > len(sequence):
            invalid("Insertion does not address a valid syntax sequence range")
        for node in sequence[start:start + count]:
            call = node["origin"]["inline_call_id"]
            if record["id"] not in ancestors.get(call, set()):
                invalid("Inserted node provenance does not belong to the invocation")
        validate_origins(record["call_site"], calls)
