"""Validate nested commands using an explicitly supplied registry."""

from collections import Counter

from sttv.common.errors import BuildError
from .values import validate_scalar


class ScriptRules:
    def __init__(self, registry):
        self.registry = registry

    def lookup(self, context, key):
        spec = self.registry["contexts"].get(context)
        if spec is None:
            return None
        rule = spec["rules"].get(key)
        if rule is None and spec["conditions"]:
            rule = self.registry["conditions"].get(key)
        return rule

    def validate(self, block, context, scope=None, path="fields"):
        if scope is None:
            scope = self.registry["root_scope"]
        spec = self.registry["contexts"][context]
        counts = Counter()
        for item in block["entries"]:
            key = item["key"]
            rule = self.lookup(context, key)
            location = f"{path}.{key}"
            if rule is None:
                raise BuildError("unsupported_command", f"Unsupported {context} command: {key}",
                                 line=item["line"], field_path=location)
            counts[key] += 1
            if counts[key] > 1 and not rule["many"]:
                raise BuildError("repeated_argument", f"Repeated argument: {key}",
                                 line=item["line"], field_path=location)
            try:
                if rule["scopes"] is not None and scope not in rule["scopes"]:
                    raise BuildError("invalid_scope", f"{key} is not supported in {scope}")
                if item["operator"] not in rule["operators"]:
                    raise BuildError("invalid_operator", f"Invalid operator for {key}")
                self.value(item["value"], rule, scope, location)
            except BuildError as exc:
                exc.line = exc.line or item["line"]
                exc.field_path = exc.field_path or location
                raise
        missing = set(spec["required"]) - counts.keys()
        if missing:
            raise BuildError("missing_argument", f"Missing arguments: {sorted(missing)}",
                             field_path=path)

    def value(self, value, rule, scope, path):
        spec = self.registry["value_types"][rule["type"]]
        if spec["kind"] == "block":
            if not isinstance(value, dict):
                raise BuildError("invalid_argument", "Expected a script block")
            self.validate(value, rule["context"], rule["scope"] or scope, path)
        elif spec["kind"] == "inline":
            self.inline(value, scope, path)
        else:
            validate_scalar(value, spec)

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
            validate_scalar(item, self.registry["value_types"][spec["parameters"][key]])
