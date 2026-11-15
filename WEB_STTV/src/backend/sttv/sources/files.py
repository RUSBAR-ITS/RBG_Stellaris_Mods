"""Deterministic file discovery and read-only source access."""

from hashlib import sha256

from sttv.common.errors import BuildError
from .expansion import independent_sources


def source_files(directory, pattern, recursive):
    if "/" in pattern or "\\" in pattern or pattern in ("", ".", ".."):
        raise BuildError("invalid_pattern", "Source pattern must be a filename pattern")
    files = directory.rglob(pattern) if recursive else directory.glob(pattern)
    for path in sorted(files, key=lambda item: item.relative_to(directory).as_posix()):
        if not path.is_file():
            continue
        if not path.resolve().is_relative_to(directory.resolve()):
            raise BuildError("unsafe_source", f"File link escapes source directory: {path.name}")
        yield path


def selected_files(settings):
    selected = {}
    for spec in settings.sources:
        files = source_files(spec["directory"], spec["pattern"], spec["recursive"])
        for path in independent_sources(files, settings):
            stat = path.stat()
            identity = (stat.st_dev, stat.st_ino)
            if identity in selected:
                previous, encoding = selected[identity]
                if encoding != spec["encoding"]:
                    raise BuildError("source_conflict", f"Conflicting encodings for source: {path}")
                path = min(previous, path, key=lambda item: item.as_posix())
            selected[identity] = (path, spec["encoding"])
    if not selected:
        raise BuildError("empty_sources", "No independent source files selected")
    return sorted(selected.values(), key=lambda item: item[0].relative_to(settings.game).as_posix())


def read_source(path, encoding, report, relative, manifest='sources'):
    try:
        raw = path.read_bytes()
        report.data[manifest][relative] = sha256(raw).hexdigest()
        return raw.decode(encoding).replace("\r\n", "\n").replace("\r", "\n")
    except (OSError, UnicodeError, LookupError) as exc:
        raise BuildError("source_read_error", str(exc)) from exc
