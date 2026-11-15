"""Semantic checks shared by profile expansion and offline registry use."""

import re

from sttv.common.errors import BuildError
from sttv.common.schema import validate_schema
from sttv.technologies.contracts import SCRIPT_CONTEXTS, SCRIPT_OPERATORS


def fail(code, message, path):
    raise BuildError(code, message, field_path=path)


def validate_types(types):
    for name, spec in types.items():
        path = f"value_types.{name}"
        kind = spec["kind"]
        allowed = {"kind"}
        if kind in ("identifier", "string"):
            allowed.add("pattern")
        if kind in ("number", "integer"):
            allowed.update(("references", "minimum", "maximum"))
        if kind == "enum":
            allowed.add("values")
            if not spec.get("values"):
                fail("invalid_type", "An enum requires values", path)
        if set(spec) - allowed:
            fail("invalid_type", f"Constraints do not apply to {kind}", path)
        if kind == "identifier" and "pattern" not in spec:
            fail("invalid_type", "An identifier requires a pattern", path)
        if spec.get("minimum", float("-inf")) > spec.get("maximum", float("inf")):
            fail("invalid_type", "Minimum exceeds maximum", path)
        for pattern in [spec["pattern"]] if "pattern" in spec else spec.get("references", []):
            try:
                re.compile(pattern)
            except re.error as exc:
                fail("invalid_type", str(exc), path)


def validate_rule(rule, registry, path):
    if rule["type"] not in registry["value_types"]:
        fail("rule_reference", "Unknown value type", path + ".type")
    kind = registry["value_types"][rule["type"]]["kind"]
    scopes = set(registry["scopes"])
    if rule["scopes"] is not None and not set(rule["scopes"]) <= scopes:
        fail("rule_reference", "Unknown accepted scope", path + ".scopes")
    if rule["scope"] is not None and rule["scope"] not in scopes:
        fail("rule_reference", "Unknown scope transition", path + ".scope")
    if not set(rule["operators"]) <= SCRIPT_OPERATORS:
        fail("unsupported_operator", "Operator is not representable in the database contract", path + ".operators")
    if kind == "block":
        if rule["context"] not in registry["contexts"]:
            fail("rule_reference", "A block requires a known context", path + ".context")
    elif rule["context"] is not None or rule["scope"] is not None:
        fail("invalid_rule", "Only blocks can change context or scope", path)


def validate_registry(registry):
    validate_schema(registry, "registry.schema.json")
    validate_types(registry["value_types"])
    if registry["root_scope"] not in registry["scopes"]:
        fail("rule_reference", "Unknown root scope", "root_scope")
    missing = (SCRIPT_CONTEXTS | {"calculation"}) - registry["contexts"].keys()
    if missing:
        fail("rule_reference", f"Missing application contexts: {sorted(missing)}", "contexts")
    for context, spec in registry["contexts"].items():
        available = set(spec["rules"])
        if spec["conditions"]:
            available.update(registry["conditions"])
        if not set(spec["required"]) <= available:
            fail("rule_reference", "Required arguments have no rules", f"contexts.{context}.required")
        for command, item in spec["rules"].items():
            validate_rule(item, registry, f"contexts.{context}.rules.{command}")
    for command, item in registry["conditions"].items():
        validate_rule(item, registry, f"conditions.{command}")
    for name, spec in registry["inline_scripts"].items():
        for parameter, type_name in spec["parameters"].items():
            path = f"inline_scripts.{name}.parameters.{parameter}"
            if type_name not in registry["value_types"]:
                fail("rule_reference", "Unknown inline parameter type", path)
            if registry["value_types"][type_name]["kind"] in ("block", "inline"):
                fail("invalid_inline", "Inline parameters must be scalar", path)


def validate_registry_syntax(registry, syntax):
    rules = [*registry["conditions"].values(),
             *(rule for context in registry["contexts"].values() for rule in context["rules"].values())]
    operators = {operator for rule in rules for operator in rule["operators"]}
    missing = operators - set(syntax.lexical["operators"])
    if missing:
        fail("syntax_registry_mismatch", f"Registry operators absent from syntax: {sorted(missing)}",
             "parser.lexical.operators")
