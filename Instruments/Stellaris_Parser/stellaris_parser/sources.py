"""Discover effective files in ordered game and mod roots."""

import os
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

from document_package.errors import BuildError
from document_package.package import confined


def relative_path(value, allow_root=False):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected a nonempty source-relative path")
    path = PureWindowsPath(value)
    if path.drive or path.root or '..' in path.parts or (not allow_root and not path.parts):
        raise ValueError(f"Invalid source-relative path: {value}")
    return Path(*path.parts)


@dataclass(frozen=True)
class SourceFile:
    relative: str
    path: Path
    size: int


class Sources:
    def __init__(self, roots):
        self.roots = roots
        if not roots or any(not root.is_dir() for root in roots):
            raise BuildError('missing_root', 'Each source root must be an existing directory')

    def find(self, relative):
        relative = relative_path(relative)
        for root in self.roots:
            path = confined(root, relative)
            if path.is_file():
                return path
        raise BuildError('source_unavailable', f'Missing source: {relative}')

    def matching(self, patterns, *, skip, exclude):
        found = {}
        missing = {p for p in patterns if not any(c in str(p) for c in '*?[')}
        for root in self.roots:
            for pattern in patterns:
                for path in root.glob(pattern.as_posix()):
                    relative = path.relative_to(root)
                    if not path.is_file():
                        continue
                    missing.discard(relative)
                    if relative in found or relative in exclude or any(relative.is_relative_to(d) for d in skip):
                        continue
                    if relative.suffix.lower() not in ('.txt', '.dlc'):
                        continue
                    path = confined(root, relative)
                    found[relative] = SourceFile(relative.as_posix(), path, path.stat().st_size)
        missing.difference_update(exclude)
        if missing:
            raise BuildError('source_unavailable', f'Missing source: {min(missing)}')
        return found

    def collect(self, directories, pattern, *, skip=(), exclude=(), required=False):
        found, seen_dirs = {}, set()
        skip, exclude = set(skip), set(exclude)
        for root in self.roots:
            for directory in directories:
                start = root if directory == Path('.') else confined(root, directory)
                if not start.is_dir():
                    continue
                seen_dirs.add(directory)
                if any(directory.is_relative_to(item) for item in skip):
                    continue
                for folder, children, names in os.walk(start, onerror=_raise_walk_error):
                    parent = Path(folder).relative_to(root)
                    children[:] = [name for name in children if parent / name not in skip]
                    for name in names:
                        relative = parent / name
                        if relative in found or relative in exclude or not relative.match(pattern):
                            continue
                        path = confined(root, relative)
                        if path.is_file():
                            found[relative] = SourceFile(relative.as_posix(), path, path.stat().st_size)
        if required and (missing := set(directories) - seen_dirs):
            raise BuildError('source_unavailable', f'Missing source directory: {min(missing)}')
        return found


def _raise_walk_error(error):
    raise error
