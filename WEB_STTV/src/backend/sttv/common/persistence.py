"""Validate and reread JSON before replacing one output file."""

import os
import tempfile
from pathlib import Path

from .json_io import json_text, read_json
from .errors import BuildError
from .schema import validate_schema


def prepare_json(path, value, schema=None, validator=None):
    check = validator if validator is not None else lambda data: validate_schema(data, schema)
    check(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         prefix=path.name + ".", suffix=".tmp",
                                         dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(json_text(value))
            handle.flush()
            os.fsync(handle.fileno())
        check(read_json(temporary))
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
