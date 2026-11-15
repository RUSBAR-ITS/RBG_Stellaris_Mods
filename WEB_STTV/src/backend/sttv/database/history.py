"""Validate mixed expansion history against local tree positions and provenance."""

from sttv.common.errors import BuildError
from sttv.script.serialization import walk_nodes


def invalid(message):
    raise BuildError("invalid_inline_history", message)


def validate_origins(value, calls):
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            call = item.get("expansion_id")
            if call is not None and call not in calls:
                invalid(f"Unknown invocation in provenance: {call}")
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)


def validate_history(document):
    records = document["metadata"]["expansions"]
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
    containers, nodes = {"/items": document["items"]}, {}
    for path, node in walk_nodes(document["items"]):
        nodes[path] = node
        if node['kind'] == 'script_value':
            record = calls.get(node['origin']['expansion_id'], {})
            if record.get('kind') != 'script_value' or record.get('insertion') != {'node': path}:
                invalid('Calculation node is missing its own history entry')
        if "items" in node:
            containers[path + "/items"] = node["items"]
        validate_origins(node["origin"], calls)
    for record in records:
        insertion = record["insertion"]
        if record['kind'] == 'script_value':
            node = nodes.get(insertion.get('node'))
            if (node is None or node['kind'] != 'script_value'
                    or node['origin']['expansion_id'] != record['id']):
                invalid('Value insertion does not address its calculation node')
            validate_origins(record['call_site'], calls)
            continue
        sequence = containers.get(insertion["container"])
        start, count = insertion["index"], insertion["count"]
        if sequence is None or start + count > len(sequence):
            invalid("Insertion does not address a valid syntax sequence range")
        for node in sequence[start:start + count]:
            call = node["origin"]["expansion_id"]
            if record["id"] not in ancestors.get(call, set()):
                invalid("Inserted node provenance does not belong to the invocation")
        validate_origins(record["call_site"], calls)
