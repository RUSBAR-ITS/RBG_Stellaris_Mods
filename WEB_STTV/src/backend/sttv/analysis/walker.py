"""Walk supported source trees and retain uncertainty across unknown blocks."""

from collections import Counter

from sttv.common.errors import BuildError
from sttv.script.serialization import script_block
from sttv.script.rules import ScriptRules
from sttv.script.values import validate_scalar
from sttv.technologies.contracts import CONTRACTS, SCRIPT_CONTEXTS
from .observations import finish, observation


class Walker:
    def __init__(self, registry, source, file, text, excerpt_length):
        self.rules = ScriptRules(registry)
        self.registry = registry
        self.location = {"source": source, "file": file}
        self.lines = text.splitlines()
        self.length = excerpt_length
        self.rows = []

    def record(self, node, context, scope, path, **changes):
        return observation(node, context, scope, {**self.location, "path": path},
                           self.lines, self.length, **changes)

    def commands(self, nodes, context, scope, path):
        counts = Counter(node.key for node in nodes)
        for index, node in enumerate(nodes):
            location = f"{path}.{node.key or '<bare>'}[{index}]"
            row = self.record(node, context, scope, location)
            rule = self.rules.lookup(context, node.key)
            row["current_rule"] = rule
            if rule is None:
                row["issues"].append("unsupported_command" if context else "unknown_context")
            else:
                if scope is None:
                    row["issues"].append("unknown_scope")
                elif rule["scopes"] is not None and scope not in rule["scopes"]:
                    row["issues"].append("invalid_scope")
                if node.operator not in rule["operators"]:
                    row["issues"].append("invalid_operator")
                if counts[node.key] > 1 and not rule["many"]:
                    row["issues"].append("repeated_argument")
                spec = self.registry["value_types"][rule["type"]]
                if spec["kind"] == "inline":
                    row["inline_path"] = next((child.value for child in node.value
                                               if child.key == "script" and isinstance(child.value, str)),
                                              None) if isinstance(node.value, list) else node.value
                try:
                    if spec["kind"] == "inline":
                        self.rules.inline(script_block(node.value) if isinstance(node.value, list)
                                          else node.value, scope, location)
                    elif spec["kind"] != "block":
                        validate_scalar(node.value, spec)
                    elif not isinstance(node.value, list):
                        raise BuildError("invalid_argument", "Expected a block")
                    else:
                        required = self.registry["contexts"][rule["context"]]["required"]
                        if not set(required) <= {child.key for child in node.value}:
                            row["issues"].append("missing_argument")
                except BuildError as exc:
                    row["issues"].append(exc.code)
            if isinstance(node.value, list):
                row["parameters"] = sorted({child.key for child in node.value if child.key})
                if row["inline_path"]:
                    row["parameters"] = [key for key in row["parameters"] if key != "script"]
            self.rows.append(finish(row))
            if isinstance(node.value, list):
                kind = self.registry["value_types"][rule["type"]]["kind"] if rule else None
                if kind == "inline":
                    continue
                child_context = rule["context"] if kind == "block" else None
                # An unknown parent can change scope; never carry country through it.
                child_scope = (rule["scope"] or scope) if kind == "block" else None
                self.commands(node.value, child_context, child_scope, location)

    def fields(self, nodes, context, path):
        for index, node in enumerate(nodes):
            if context == "variant" and node.key == "name":
                continue
            location = f"{path}.{node.key}[{index}]"
            field = CONTRACTS[context].get(node.key)
            if field is None:
                row = self.record(node, context, None, location, issues=["unsupported_field"])
                self.rows.append(finish(row))
                continue
            if not isinstance(node.value, list):
                continue
            if field.kind == "variant":
                self.fields(node.value, "variant", location)
            elif field.kind in SCRIPT_CONTEXTS or field.kind == "cost":
                script_context = "calculation" if field.kind == "cost" else field.kind
                self.commands(node.value, script_context, self.registry["root_scope"], location)

    def technologies(self, nodes, collection):
        for node in nodes:
            if node.key and node.key.startswith("@"):
                continue
            if not node.key or node.operator != "=" or not isinstance(node.value, list):
                raise BuildError("invalid_definition", "Expected a named definition block", line=node.line)
            self.fields(node.value, collection, node.key)
        return self.rows
