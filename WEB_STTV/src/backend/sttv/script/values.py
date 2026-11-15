"""Scalar forms implemented by the parser and configurable type descriptors."""

import re

from sttv.common.errors import BuildError
from sttv.common.json_io import numeric_value


def validate_scalar(value, spec):
    kind = spec["kind"]
    if not isinstance(value, str):
        raise BuildError("invalid_argument", f"Expected scalar {kind}")
    if kind == "boolean":
        valid = value in ("yes", "no")
    elif kind == "identifier":
        valid = bool(re.fullmatch(spec["pattern"], value))
    elif kind == "enum":
        valid = value in spec["values"]
    elif kind in ("number", "integer"):
        if any(re.fullmatch(pattern, value) for pattern in spec.get("references", [])):
            return
        number = numeric_value(value, integer=kind == "integer")
        valid = spec.get("minimum", float("-inf")) <= number <= spec.get("maximum", float("inf"))
    elif kind == "string":
        valid = bool(value) and ("pattern" not in spec or bool(re.fullmatch(spec["pattern"], value)))
    else:
        raise BuildError("invalid_rules", f"Not a scalar argument kind: {kind}")
    if not valid:
        raise BuildError("invalid_argument", f"Invalid {kind} argument: {value}")
