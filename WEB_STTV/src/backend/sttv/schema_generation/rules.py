"""Closed profile and expanded-registry declarations."""

from .helpers import BOOL, HASH, LINE, NULL, STRING, TEXT, array, mapping, obj, union

KINDS = ("boolean", "number", "integer", "identifier", "string", "enum", "block", "inline")


def value_type():
    return obj({
        "kind": {"enum": list(KINDS)}, "pattern": TEXT,
        "references": array(TEXT, uniqueItems=True), "values": array(TEXT, minItems=1, uniqueItems=True),
        "minimum": {"type": "number"}, "maximum": {"type": "number"},
    }, ["kind"])


def rule(partial=False):
    fields = {
        "type": TEXT, "scopes": union(array(TEXT, minItems=1, uniqueItems=True), NULL),
        "operators": array(TEXT, minItems=1, uniqueItems=True), "many": BOOL,
        "context": union(TEXT, NULL), "scope": union(TEXT, NULL),
    }
    return obj(fields, [] if partial else None)


def provenance():
    return array(obj({
        "id": TEXT, "kind": {"enum": ["observed", "documentation", "unverified"]},
        "file": union(TEXT, NULL), "line": union(LINE, NULL), "record": union(TEXT, NULL),
        "game_version": union(TEXT, NULL), "notes": STRING,
    }))


def shared():
    return {
        "format_version": {"const": 1}, "profile_id": TEXT, "revision": LINE,
        "game_version": union(TEXT, NULL), "provenance": provenance(),
        "value_types": mapping(value_type()), "scopes": array(TEXT, minItems=1, uniqueItems=True),
        "root_scope": TEXT,
        "inline_scripts": mapping(obj({"scalar": BOOL, "parameters": mapping(TEXT)})),
    }


def profile():
    return obj({
        **shared(),
        "contexts": mapping(obj({"conditions": BOOL, "required": array(TEXT, uniqueItems=True)})),
        "templates": mapping(obj({"extends": TEXT, "rule": rule(partial=True)}, ["rule"])),
        "command_groups": array(obj({
            "context": TEXT, "template": TEXT, "commands": array(TEXT, minItems=1, uniqueItems=True),
            "evidence": array(TEXT, uniqueItems=True),
        })),
        "overrides": array(obj({
            "context": TEXT, "command": TEXT, "rule": rule(partial=True),
            "reason": TEXT, "evidence": array(TEXT, uniqueItems=True),
        })),
    })


def registry():
    return obj({
        **shared(), "profile_fingerprint": HASH,
        "conditions": mapping(rule()),
        "contexts": mapping(obj({
            "conditions": BOOL, "required": array(TEXT, uniqueItems=True), "rules": mapping(rule()),
        })),
    })


def generation_report():
    return obj({
        "format_version": {"const": 1}, "profile_id": TEXT, "profile_fingerprint": HASH,
        "registry_path": TEXT, "registry_written": BOOL,
    })
