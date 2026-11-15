"""Coordinate-preserving observations; no evaluation of game conditions."""

import re

from sttv.rules.compiler import fingerprint


def argument_kind(value):
    if isinstance(value, list):
        return "block"
    if value in ("yes", "no"):
        return "boolean"
    if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value):
        return "number"
    if value.startswith(("@", "value:", "trigger:", "$")):
        return "reference"
    if re.fullmatch(r"[A-Za-z0-9_:.?/-]+", value):
        return "identifier"
    return "string"


def observation(node, context, scope, location, lines, length, **changes):
    row = {
        "command": node.key, "context": context, "scope": scope, "operator": node.operator,
        "form": "block" if isinstance(node.value, list) else "scalar",
        "argument_kind": argument_kind(node.value), "parameters": [],
        "inline_path": None,
        "documented_scopes": [], "documented_operators": [], "basis": "observed",
        **location, "line": node.line,
        "excerpt": lines[node.line - 1].strip()[:length] if node.line <= len(lines) else "",
        "issues": [], "current_rule": None, **changes,
    }
    row["id"] = fingerprint(row)
    return row


def finish(row):
    row["issues"] = sorted(set(row["issues"]))
    row["id"] = fingerprint({key: value for key, value in row.items() if key != "id"})
    return row
