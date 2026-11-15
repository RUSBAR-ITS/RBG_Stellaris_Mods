"""Transform parsed definitions using closed, context-specific contracts."""

from collections import defaultdict

from .contracts import CONTRACTS, MULTIPLE, SCRIPT_CONTEXTS
from .errors import BuildError
from .parser import script_block


def requirement(entries):
    result = []
    for entry in entries:
        if entry.key is None and isinstance(entry.value, str):
            result.append({"tech": entry.value})
        elif entry.operator == "=" and entry.key in ("OR", "AND") and isinstance(entry.value, list):
            children = requirement(entry.value)["all"]
            result.append({"any" if entry.key == "OR" else "all": children})
        else:
            raise BuildError("unsupported_requirement", "Unsupported prerequisite construct",
                             line=entry.line)
    return {"all": result}


def envelope(source):
    return {"source": source, "fields": {},
            "name": {"ru": None, "en": None},
            "name_sources": {"ru": None, "en": None}}


class Converter:
    def __init__(self, variables, rules, report, file, definition_id):
        self.variables = variables
        self.rules = rules
        self.report = report
        self.file = file
        self.definition_id = definition_id

    def location(self, line, path):
        return {"source": "TECH_PATH", "file": self.file, "line": line,
                "definition_id": self.definition_id, "field_path": path}

    def fields(self, entries, context, path="fields"):
        grouped = defaultdict(list)
        contract = CONTRACTS[context]
        for entry in entries:
            if entry.key not in contract or entry.operator != "=":
                raise BuildError("unsupported_field", f"Unsupported {context} field: {entry.key}",
                                 line=entry.line, field_path=f"{path}.{entry.key}")
            grouped[entry.key].append(entry)
        fields = {}
        for key, group in grouped.items():
            location = f"{path}.{key}"
            values = []
            for entry in group:
                try:
                    values.append(self.value(entry, contract[key], location))
                except BuildError as exc:
                    exc.line = exc.line or entry.line
                    exc.field_path = exc.field_path or location
                    raise
            if key in MULTIPLE:
                fields[key] = values
            elif len(values) == 1:
                fields[key] = values[0]
            else:
                fields[key] = {"occurrences": [
                    {"line": entry.line, "value": value}
                    for entry, value in zip(group, values)]}
                self.report.add("warning", "repeated_field", "conversion",
                                f"Retained {len(values)} occurrences of {key}",
                                **self.location(group[0].line, location))
        return fields

    def value(self, entry, kind, path):
        value = entry.value
        if kind in ("number", "integer") or (kind == "cost" and isinstance(value, str)):
            return self.variables.number(value, kind == "integer", self.report,
                                         self.location(entry.line, path))
        if kind in ("area", "identifier", "boolean"):
            if not isinstance(value, str):
                raise BuildError("invalid_scalar", f"Expected {kind}")
            if kind == "boolean":
                if value not in ("yes", "no"):
                    raise BuildError("invalid_boolean", f"Invalid boolean: {value}")
                return value == "yes"
            if kind == "area" and value not in ("physics", "society", "engineering"):
                raise BuildError("invalid_area", f"Invalid area: {value}")
            return value
        if not isinstance(value, list):
            raise BuildError("invalid_block", f"Expected block for {kind}")
        if kind == "list":
            if any(item.key is not None or not isinstance(item.value, str) for item in value):
                raise BuildError("invalid_list", "Expected a list of scalar identifiers")
            return [item.value for item in value]
        if kind == "requirements":
            return requirement(value)
        if kind == "variant":
            names = [item for item in value if item.key == "name"]
            if len(names) != 1 or names[0].operator != "=" or not isinstance(names[0].value, str):
                raise BuildError("invalid_variant_name", "Variant needs exactly one scalar name")
            record = envelope({"file": self.file, "line": entry.line})
            record["name_key"] = names[0].value
            record["fields"] = self.fields([item for item in value if item.key != "name"],
                                           "variant", f"{path}.fields")
            return record
        if kind in SCRIPT_CONTEXTS or kind == "cost":
            block = script_block(value)
            self.rules.validate(block, "calculation" if kind == "cost" else kind,
                                path=path)
            return block
        raise BuildError("unsupported_conversion", f"Unknown conversion: {kind}")
