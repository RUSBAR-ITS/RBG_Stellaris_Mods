"""Deterministic expansion of explicit rule profiles; no source inference."""

from copy import deepcopy
from hashlib import sha256
import json
from jsonschema import Draft202012Validator

from sttv.common.json_io import read_json
from sttv.common.schema import schema_validator, validate_schema
from .validation import fail, validate_registry, validate_rule


def fingerprint(profile):
    encoded = json.dumps(profile, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


def load_profile(path):
    profile = read_json(path)
    validate_profile(profile)
    return profile


def expanded_templates(profile):
    templates, resolved = profile["templates"], {}

    def resolve(name, trail=()):
        path = f"templates.{name}"
        if name not in templates:
            fail("rule_reference", f"Unknown template: {name}", path)
        if name in trail:
            fail("template_cycle", f"Cyclic template inheritance: {name}", path)
        if name not in resolved:
            template = templates[name]
            base = resolve(template["extends"], trail + (name,)) if "extends" in template else {}
            resolved[name] = {**base, **template["rule"]}
        return resolved[name]

    for name in templates:
        resolve(name)
    return resolved


def generate_registry(profile):
    validate_schema(profile, "profile.schema.json")
    templates = expanded_templates(profile)
    registry = {key: deepcopy(profile[key]) for key in (
        "format_version", "profile_id", "revision", "game_version", "provenance",
        "value_types", "scopes", "root_scope", "inline_scripts")}
    registry["profile_fingerprint"] = fingerprint(profile)
    registry["conditions"] = {}
    registry["contexts"] = {name: {**deepcopy(spec), "rules": {}}
                            for name, spec in profile["contexts"].items()}
    evidence = [item["id"] for item in profile["provenance"]]
    if len(evidence) != len(set(evidence)):
        fail("duplicate_evidence", "Provenance identifiers must be unique", "provenance")

    def destination(context, path):
        if context == "$conditions":
            return registry["conditions"]
        if context not in registry["contexts"]:
            fail("rule_reference", f"Unknown context: {context}", path + ".context")
        return registry["contexts"][context]["rules"]

    def check_evidence(item, path):
        if not set(item["evidence"]) <= set(evidence):
            fail("rule_reference", "Unknown evidence reference", path + ".evidence")

    for index, group in enumerate(profile["command_groups"]):
        path = f"command_groups.{index}"
        check_evidence(group, path)
        rules = destination(group["context"], path)
        if group["template"] not in templates:
            fail("rule_reference", "Unknown group template", path + ".template")
        rule = templates[group["template"]]
        for name in group["commands"]:
            if name in rules and rules[name] != rule:
                fail("rule_conflict", f"Incompatible definitions of {name}", path)
            rules[name] = deepcopy(rule)
    changed = set()
    for index, override in enumerate(profile["overrides"]):
        path = f"overrides.{index}"
        check_evidence(override, path)
        rules = destination(override["context"], path)
        name = override["command"]
        key = (override["context"], name)
        if key in changed:
            fail("rule_conflict", "Multiple overrides of one command", path)
        if name not in rules:
            fail("rule_reference", "Override target is absent", path)
        changed.add(key)
        rules[name] = {**rules[name], **override["rule"]}
    validate_registry(registry)
    # Unused templates are checked too; they cannot hide malformed definitions.
    shape = schema_validator("registry.schema.json").schema["properties"]["conditions"]["additionalProperties"]
    template_validator = Draft202012Validator(shape)
    for name, rule in templates.items():
        error = next(template_validator.iter_errors(rule), None)
        if error:
            fail("invalid_template", error.message, f"templates.{name}.rule")
        validate_rule(rule, registry, f"templates.{name}.rule")
    return registry


def validate_profile(profile):
    generate_registry(profile)
    return {"valid": True, "profile_id": profile["profile_id"], "fingerprint": fingerprint(profile)}
