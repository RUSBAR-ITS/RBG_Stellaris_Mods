"""Expand configuration variables without loading any parser or game source."""

import re

from .errors import BuildError


def substitute(value, lookup):
    result = re.sub(r"\$\{([A-Za-z0-9_]+)\}", lambda match: lookup(match[1]), value)
    if "${" in result:
        raise BuildError("invalid_variable", "Invalid variable substitution")
    return result


def expand_variables(raw):
    if not isinstance(raw, dict) or any(
        not re.fullmatch(r"[A-Z][A-Z0-9_]*", key) or not isinstance(value, str)
        or not value for key, value in raw.items()
    ):
        raise BuildError("invalid_variables", "Variables must be named nonempty strings")
    expanded = {}

    def expand(key, trail=()):
        if key not in raw:
            raise BuildError("unknown_variable", f"Unknown variable: {key}")
        if key in trail:
            raise BuildError("variable_cycle", f"Configuration variable cycle: {key}")
        if key not in expanded:
            expanded[key] = substitute(raw[key], lambda name: expand(name, trail + (key,)))
        return expanded[key]

    for key in raw:
        expand(key)
    return expanded
