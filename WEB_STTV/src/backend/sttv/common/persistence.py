"""Validate prepared JSON once before replacing one output file."""

import os
import json
import tempfile
from pathlib import Path

from .errors import BuildError
from .schema import validate_schema


def prepare_json(path, value, schema=None, validator=None, compact=False):
    check = validator if validator is not None else lambda data: validate_schema(data, schema)
    check(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         prefix=path.name + ".", suffix=".tmp",
                                         dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            if compact:
                json.dump(value, handle, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':'), allow_nan=False)
                handle.write('\n')
            else:
                json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
                handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        return temporary
    except BaseException:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise


def save_json(path, value, schema=None, validator=None):
    temporary = None
    try:
        temporary = prepare_json(path, value, schema, validator)
        os.replace(temporary, path)
    except OSError as exc:
        raise BuildError("write_error", f"{path}: {exc}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return {"path": str(path), "written": True}
