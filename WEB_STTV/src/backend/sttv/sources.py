"""Deterministic file discovery and read-only source access."""

from .errors import BuildError


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


def read_source(path, encoding, report):
    try:
        content = path.read_text(encoding=encoding)
    except (OSError, UnicodeError) as exc:
        raise BuildError("source_read_error", str(exc)) from exc
    report.data["counts"]["files"] += 1
    return content
