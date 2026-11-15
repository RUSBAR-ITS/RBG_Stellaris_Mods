"""Track projected values without exposing service metadata as game fields."""

from sttv.common.errors import BuildError


def pointer_part(value):
    return value.replace("~", "~0").replace("/", "~1")


class Projection:
    def __init__(self, records):
        self.records = {item["id"]: {k: v for k, v in item.items() if k != "insertion"} for item in records}
        for item in self.records.values():
            item["result_paths"] = []

    def add(self, entry, path):
        call = entry.origin.get("inline_call_id") if entry.origin else None
        while call:
            record = self.records[call]
            if path not in record["result_paths"]:
                record["result_paths"].append(path)
            call = record["parent_id"]


def resolve_pointer(value, pointer):
    if not pointer.startswith("/"):
        raise BuildError("invalid_result_path", f"Invalid result pointer: {pointer}")
    try:
        for part in pointer[1:].split("/"):
            key = part.replace("~1", "/").replace("~0", "~")
            value = value[int(key)] if isinstance(value, list) else value[key]
    except (ValueError, IndexError, KeyError, TypeError) as exc:
        raise BuildError("invalid_result_path", f"Missing result pointer: {pointer}") from exc
    return value


def validate_history(database):
    calls = database["metadata"]["inline_scripts"]
    seen = set()
    for record in calls:
        if record["id"] in seen or (record["parent_id"] is not None and record["parent_id"] not in seen):
            raise BuildError("invalid_inline_history", "Duplicate invocation or invalid parent order")
        seen.add(record["id"])
        for pointer in record["result_paths"]:
            if pointer.startswith("/metadata"):
                raise BuildError("invalid_result_path", "Results cannot point into metadata")
            resolve_pointer(database, pointer)

    def visit(value):
        if isinstance(value, dict):
            if "inline_call_id" in value and value["inline_call_id"] is not None and value["inline_call_id"] not in seen:
                raise BuildError("invalid_inline_history", "Unknown invocation in source provenance")
            for key, child in value.items():
                if key != "metadata":
                    visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    visit(database)
