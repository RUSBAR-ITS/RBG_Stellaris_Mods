"""Read Stellaris localization entries without YAML coercion or unescaping."""

import re

from document_package.errors import BuildError

HEADER = re.compile(r"^\s*(l_\w+):\s*(?:#.*)?$")
ENTRY = re.compile(r'^\s*([^\s:#"]+):[0-9]*\s*"')


def content(line, start):
    escaped = False
    for index in range(start, len(line)):
        char = line[index]
        if char == '"' and not escaped:
            tail = line[index + 1:].strip()
            if not tail or tail.startswith("#"):
                return line[start:index]
        escaped = char == "\\" and not escaped
    raise BuildError("localization_syntax", "Missing closing quote or unsupported trailing content")


def read_entries(path, header, encoding, snapshot):
    try:
        raw = path.read_bytes()
        snapshot.record(path, "localization", raw)
        text = raw.decode(encoding).removeprefix("\ufeff")
    except (OSError, UnicodeError) as exc:
        raise BuildError("localization_read_error", f"{path}: {exc}") from exc
    language = None
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = HEADER.fullmatch(line)
        if match:
            language = match[1]
            continue
        try:
            match = ENTRY.match(line)
            if not match or language is None:
                raise BuildError("localization_syntax", "Expected a language header or quoted entry")
            value = content(line, match.end())
        except BuildError as exc:
            raise BuildError(exc.code, f"{path}:{number}: {exc}", line=number) from exc
        if language == header:
            yield match[1], value, number
