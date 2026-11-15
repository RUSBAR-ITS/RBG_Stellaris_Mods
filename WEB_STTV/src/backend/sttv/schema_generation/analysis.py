"""Closed observations and review-only recommendations."""

from .helpers import HASH, LINE, NULL, STRING, TEXT, array, obj, union
from .reports import diagnostic
from .rules import rule
from . import inline


def schema():
    nullable = union(TEXT, NULL)
    observation = obj({
        "id": HASH, "command": nullable, "context": nullable, "scope": nullable,
        "operator": nullable, "form": {"enum": ["scalar", "block", "definition", "documentation"]},
        "argument_kind": TEXT, "parameters": array(TEXT, uniqueItems=True),
        "inline_path": nullable,
        "documented_scopes": array(TEXT, uniqueItems=True),
        "documented_operators": array(TEXT, uniqueItems=True),
        "basis": {"enum": ["observed", "documentation"]},
        "source": TEXT, "file": TEXT, "line": LINE, "path": TEXT, "excerpt": STRING,
        "issues": array(TEXT, uniqueItems=True), "current_rule": union(rule(), NULL),
    })
    alternative = obj({
        "action": {"enum": ["add_command", "add_operator", "add_scope", "add_argument_form",
                            "add_inline_parameter", "review_block", "review_contract", "review_signature"]},
        "template": nullable, "context": nullable, "scope": nullable, "operator": nullable,
        "value_type": nullable, "parameters": array(TEXT, uniqueItems=True), "explanation": TEXT,
    })
    recommendation = obj({
        "id": HASH, "kind": TEXT,
        "target": obj({"section": {"enum": ["commands", "inline_scripts", "fields"]},
                       "context": nullable, "command": nullable}),
        "current_rule": union(rule(), NULL), "current_parameters": union(array(TEXT), NULL),
        "alternatives": array(alternative, minItems=1), "basis": array(TEXT, minItems=1, uniqueItems=True),
        "evidence": array(HASH, minItems=1, uniqueItems=True), "evidence_count": LINE,
        "contradictions": array(TEXT), "questions": array(TEXT),
        "profile_id": TEXT, "profile_fingerprint": HASH,
    })
    source = obj({
        "id": TEXT, "kind": TEXT, "path": TEXT, "enabled": {"type": "boolean"},
        "game_version": nullable, "status": {"enum": ["disabled", "read", "partial", "unavailable", "empty"]},
        "files": array(obj({"file": TEXT, "sha256": HASH})),
    })
    result = obj({
        "format_version": {"const": 1}, "status": {"enum": ["complete", "partial"]},
        "counts": obj({"inline_scripts": inline.counts()}),
        "inline_sources": {"type": "object", "additionalProperties": HASH},
        "profile_id": TEXT, "profile_revision": LINE, "profile_fingerprint": HASH,
        "sources": array(source), "observations": array(observation),
        "recommendations": array(recommendation), "diagnostics": array(diagnostic()),
    })
    result["$defs"] = {"origin": inline.origin()}
    return result
