"""Strict JSON reading and deterministic serialization."""

import json
import math
from pathlib import Path

from .errors import BuildError


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise BuildError("duplicate_json_key", f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise BuildError("invalid_number", f"Non-finite JSON number: {value}")


def read_json(path):
    return json.loads(
        Path(path).read_text(encoding="utf-8-sig"),
        object_pairs_hook=unique_object,
        parse_constant=reject_constant,
    )


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True,
                      allow_nan=False) + "\n"


def numeric_value(text, integer=False):
    try:
        value = int(text) if integer else float(text)
    except (ValueError, TypeError, OverflowError) as exc:
        raise BuildError("invalid_number", f"Expected a numeric value: {text}") from exc
    if not math.isfinite(value):
        raise BuildError("invalid_number", f"Non-finite numeric value: {text}")
    return int(value) if value == int(value) else value
