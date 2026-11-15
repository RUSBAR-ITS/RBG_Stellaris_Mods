"""Strict JSON reading and deterministic serialization."""

import json
from pathlib import Path

from sttv.common.errors import BuildError


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
    try:
        return json.loads(
            Path(path).read_text(encoding="utf-8-sig"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BuildError("json_read_error", f"{path}: {exc}",
                         line=getattr(exc, "lineno", None)) from exc


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True,
                      allow_nan=False) + "\n"

