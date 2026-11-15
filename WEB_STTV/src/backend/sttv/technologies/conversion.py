"""Transform parsed definitions using closed, context-specific contracts."""

from collections import defaultdict

from sttv.technologies.contracts import AREAS, CONTRACTS, SCRIPT_CONTEXTS
from sttv.common.errors import BuildError
from sttv.script.serialization import script_block
from sttv.script.traversal import source_location
from .provenance import pointer_part


def requirement(entries, tracker=None, pointer="", container="all"):
    result = []
    for entry in entries:
        position = f"{pointer}/{container}/{len(result)}"
        if tracker:
            tracker.add(entry, position)
        if entry.key is None and isinstance(entry.value, str):
            result.append({"tech": entry.value})
        elif entry.operator == "=" and entry.key in ("OR", "AND") and isinstance(entry.value, list):
            child_key = "any" if entry.key == "OR" else "all"
            result.append(requirement(entry.value, tracker, position, child_key))
        else:
            error = BuildError("unsupported_requirement", "Unsupported prerequisite construct", line=entry.line)
            error.provenance = entry.origin
            raise error
    return {container: result}


def envelope(source):
    return {"source": source, "fields": {},
            "name": {"ru": None, "en": None},
            "name_sources": {"ru": None, "en": None}}


class Converter:
    def __init__(self, variables, rules, report, file, definition_id, tracker=None):
        self.variables = variables
        self.rules = rules
        self.report = report
        self.file = file
        self.definition_id = definition_id
        self.tracker = tracker

    def location(self, entry, path):
        origin = entry.origin
        return {"source": origin["root"], "file": origin["file"], "line": origin["span"]["line"],
                "column": origin["span"]["column"], "provenance": origin,
                "definition_id": self.definition_id, "field_path": path}

    def fields(self, entries, context, path="fields", pointer=""):
        grouped = defaultdict(list)
        contract = CONTRACTS[context]
        for entry in entries:
            if entry.key not in contract or entry.operator != "=":
                error = BuildError("unsupported_field", f"Unsupported {context} field: {entry.key}",
                                   line=entry.line, field_path=f"{path}.{entry.key}")
                error.provenance = entry.origin
                raise error
            grouped[entry.key].append(entry)
        fields = {}
        for key, group in grouped.items():
            location = f"{path}.{key}"
            values = []
            for index, entry in enumerate(group):
                try:
                    target = pointer + "/" + pointer_part(key)
                    if contract[key].multiple:
                        target += f"/{index}"
                    elif len(group) > 1:
                        target += f"/occurrences/{index}/value"
                    if self.tracker:
                        self.tracker.add(entry, target)
                    values.append(self.value(entry, contract[key].kind, location, target))
                except BuildError as exc:
                    if not hasattr(exc, "provenance") and not hasattr(exc, "source_location"):
                        exc.provenance = entry.origin
                    exc.line = exc.line or entry.line
                    exc.field_path = exc.field_path or location
                    raise
            if contract[key].multiple:
                fields[key] = values
            elif len(values) == 1:
                fields[key] = values[0]
            else:
                fields[key] = {"occurrences": [
                    {"source": source_location(entry.origin), "value": value}
                    for entry, value in zip(group, values)]}
                self.report.add("warning", "repeated_field", "conversion",
                                f"Retained {len(values)} occurrences of {key}",
                                **self.location(group[0], location))
        return fields

    def value(self, entry, kind, path, pointer=""):
        value = entry.value
        if kind in ("number", "integer") or (kind == "cost" and isinstance(value, str)):
            return self.variables.number(value, kind == "integer", self.report,
                                         self.location(entry, path))
        if kind in ("area", "identifier", "boolean"):
            if not isinstance(value, str):
                raise BuildError("invalid_scalar", f"Expected {kind}")
            if kind == "boolean":
                if value not in ("yes", "no"):
                    raise BuildError("invalid_boolean", f"Invalid boolean: {value}")
                return value == "yes"
            if kind == "area" and value not in AREAS:
                raise BuildError("invalid_area", f"Invalid area: {value}")
            return value
        if not isinstance(value, list):
            raise BuildError("invalid_block", f"Expected block for {kind}")
        if kind == "list":
            if any(item.key is not None or not isinstance(item.value, str) for item in value):
                raise BuildError("invalid_list", "Expected a list of scalar identifiers")
            if self.tracker:
                for index, item in enumerate(value):
                    self.tracker.add(item, f"{pointer}/{index}")
            return [item.value for item in value]
        if kind == "requirements":
            return requirement(value, self.tracker, pointer)
        if kind == "variant":
            names = [item for item in value if item.key == "name"]
            if len(names) != 1 or names[0].operator != "=" or not isinstance(names[0].value, str):
                raise BuildError("invalid_variant_name", "Variant needs exactly one scalar name")
            record = envelope(source_location(entry.origin))
            record["name_key"] = names[0].value
            record["fields"] = self.fields([item for item in value if item.key != "name"],
                                           "variant", f"{path}.fields", pointer + "/fields")
            if self.tracker:
                self.tracker.add(names[0], pointer + "/name_key")
            return record
        if kind in SCRIPT_CONTEXTS or kind == "cost":
            block = script_block(value, self.tracker, pointer)
            self.rules.validate(block, "calculation" if kind == "cost" else kind,
                                path=path)
            return block
        raise BuildError("unsupported_conversion", f"Unknown conversion: {kind}")
