"""Validate nested commands against the declared context and scope registry."""

import re
from collections import Counter

from .errors import BuildError
from .json_io import numeric_value, read_json
from .schema import PRODUCT_ROOT


class ScriptRules:
    def __init__(self):
        self.registry = read_json(PRODUCT_ROOT / "schemas" / "script_rules.json")

    def validate(self, block, context, scope="country", path="fields"):
        spec = self.registry["contexts"][context]
        counts = Counter()
        for item in block["entries"]:
            key = item["key"]
            rule = spec["rules"].get(key)
            if rule is None and spec.get("conditions", False):
                rule = self.registry["conditions"].get(key)
            location = f"{path}.{key}"
            if rule is None:
                raise BuildError("unsupported_command", f"Unsupported {context} command: {key}",
                                 line=item["line"], field_path=location)
            counts[key] += 1
            if counts[key] > 1 and not rule.get("many", True):
                raise BuildError("repeated_argument", f"Repeated argument: {key}",
                                 line=item["line"], field_path=location)
            try:
                if scope not in rule.get("scopes", [scope]):
                    raise BuildError("invalid_scope", f"{key} is not supported in {scope}")
                if item["operator"] not in rule.get("operators", ["="]):
                    raise BuildError("invalid_operator", f"Invalid operator for {key}")
                self.value(item["value"], rule, scope, location)
            except BuildError as exc:
                exc.line = exc.line or item["line"]
                exc.field_path = exc.field_path or location
                raise
        missing = set(spec.get("required", [])) - counts.keys()
        if missing:
            raise BuildError("missing_argument", f"Missing arguments: {sorted(missing)}",
                             field_path=path)

    def value(self, value, rule, scope, path):
        kind = rule["kind"]
        if kind == "block":
            if not isinstance(value, dict):
                raise BuildError("invalid_argument", "Expected a script block")
            self.validate(value, rule["context"], rule.get("scope", scope), path)
            return
        if kind == "inline":
            self.inline(value, scope, path)
            return
        if not isinstance(value, str):
            raise BuildError("invalid_argument", f"Expected scalar {kind}")
        if kind == "boolean":
            valid = value in ("yes", "no")
        elif kind == "identifier":
            valid = bool(re.fullmatch(r"[A-Za-z0-9_:.?/-]+", value))
        elif kind == "enum":
            valid = value in rule["values"]
        elif kind in ("number", "integer"):
            if re.fullmatch(r"@[A-Za-z0-9_]+|(?:value|trigger):[A-Za-z0-9_.:]+", value):
                valid = True
            else:
                numeric_value(value, integer=kind == "integer")
                valid = True
        elif kind == "string":
            valid = bool(value)
        else:
            raise BuildError("invalid_rules", f"Unknown declared argument kind: {kind}")
        if not valid:
            raise BuildError("invalid_argument", f"Invalid {kind} argument: {value}")

    def inline(self, value, scope, path):
        if isinstance(value, str):
            name, fields = value, {}
        else:
            fields = {}
            for entry in value["entries"]:
                key = entry["key"]
                if key in fields or entry["operator"] != "=" or not isinstance(entry["value"], str):
                    raise BuildError("invalid_inline", "Invalid or repeated inline argument",
                                     line=entry["line"])
                fields[key] = entry["value"]
            name = fields.pop("script", None)
        spec = self.registry["inline_scripts"].get(name)
        if spec is None:
            raise BuildError("unsupported_inline", f"Unsupported inline script: {name}")
        if set(fields) != set(spec["parameters"]):
            raise BuildError("invalid_inline", f"Wrong parameters for inline script: {name}")
        if isinstance(value, str) and not spec["scalar"]:
            raise BuildError("invalid_inline", "This inline script requires a block")
        for key, item in fields.items():
            self.value(item, {"kind": spec["parameters"][key]}, scope, f"{path}.{key}")
