"""Read referenced templates only; cache bytes within one operation."""

from hashlib import sha256
from pathlib import Path, PurePosixPath

from sttv.common.errors import BuildError
from ..nodes import Source


def template_name(name, extension):
    name = name.replace("\\", "/")
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ":" in name or ".." in path.parts:
        raise BuildError("invalid_inline_path", f"Invalid template path: {name}")
    return path.as_posix() + extension


class FileTemplates:
    def __init__(self, directory, options):
        self.directory = Path(directory).resolve()
        self.options, self.cache, self.manifest = options, {}, {}

    def identity(self, name):
        relative = template_name(name, self.options["extension"])
        path = (self.directory / relative).resolve()
        if not path.is_relative_to(self.directory):
            raise BuildError("invalid_inline_path", f"Template escapes source root: {name}")
        return str(path).casefold(), relative, path

    def read(self, name):
        key, relative, path = self.identity(name)
        if key not in self.cache:
            try:
                raw = path.read_bytes()
            except FileNotFoundError as exc:
                raise BuildError("missing_inline_template", f"Missing template: {relative}") from exc
            except OSError as exc:
                raise BuildError("inline_read_error", str(exc)) from exc
            self.manifest[relative] = sha256(raw).hexdigest()
            try:
                text = raw.decode(self.options["encoding"])
            except (UnicodeError, LookupError) as exc:
                raise BuildError("inline_encoding", f"{relative}: {exc}") from exc
            self.cache[key] = Source(text, relative, "INLINE_SCRIPTS_DIR")
        return self.cache[key]


class MemoryTemplates:
    def __init__(self, templates, options):
        self.templates, self.options = templates, options
        self.manifest = {}

    def identity(self, name):
        relative = template_name(name, self.options["extension"])
        return relative.casefold(), relative, None

    def read(self, name):
        _, relative, _ = self.identity(name)
        if relative not in self.templates:
            raise BuildError("missing_inline_template", f"Missing template: {relative}")
        text = self.templates[relative]
        self.manifest[relative] = sha256(text.encode("utf-8")).hexdigest()
        return Source(text, relative, "INLINE_SCRIPTS_DIR")
