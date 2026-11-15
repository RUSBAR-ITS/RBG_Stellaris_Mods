"""Read Stellaris localization names without interpreting their markup."""

import re
from collections import defaultdict

from sttv.common.errors import BuildError
from sttv.sources.files import read_source, source_files

ENTRY = re.compile(r'^\s*([^\s:#]+)\s*:\s*(?:[0-9]+)?\s*')


def read_value(line, start, number):
    if start >= len(line) or line[start] != '"':
        raise BuildError("invalid_localization", "Expected a quoted localization value",
                         line=number)
    index = start + 1
    while index < len(line):
        if line[index] == "\\":
            index += 2
            continue
        if line[index] == '"':
            suffix = line[index + 1:].lstrip()
            if not suffix or suffix.startswith("#"):
                return line[start + 1:index]
        index += 1
    raise BuildError("invalid_localization", "Missing closing localization quote",
                     line=number)


def parse_names(text, header, wanted):
    seen_header = False
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not seen_header:
            if not re.fullmatch(re.escape(header) + r"\s*:\s*(?:#.*)?", stripped):
                raise BuildError("language_header", f"Expected {header} header", line=number)
            seen_header = True
            continue
        match = ENTRY.match(line)
        if match and match[1] in wanted:
            yield match[1], read_value(line, match.end(), number), number
    if not seen_header:
        raise BuildError("language_header", f"Missing {header} header", line=1)


def name_records(database):
    for key, record in database["technologies"].items():
        yield key, record
        for variant in record["fields"].get("technology_swap", []):
            yield variant["name_key"], variant


def collect_names(settings, database, report):
    records = list(name_records(database))
    wanted = {key for key, _ in records}
    profile = settings.options["localization"]
    for language, spec in profile["languages"].items():
        remaining = set(wanted)
        chosen = {}
        for tier in spec["sources"]:
            if not remaining:
                break
            found = defaultdict(list)
            directory = settings.sources[tier]
            for path in source_files(directory, profile["pattern"], profile["recursive"]):
                relative = path.relative_to(directory).as_posix()
                try:
                    text = read_source(path, profile["encoding"], report)
                    for key, value, line in parse_names(text, spec["header"], remaining):
                        found[key].append((value, {"tier": tier, "file": relative,
                                                  "line": line, "key": key}))
                except (BuildError, OSError, ValueError) as exc:
                    report.failure(exc, "localization", source=tier, file=relative)
            for key, entries in found.items():
                remaining.discard(key)
                if len({value for value, _ in entries}) > 1:
                    for _, source in entries:
                        report.add("error", "localization_conflict", "localization",
                                   f"Conflicting values for {key} within {tier}",
                                   source=tier, file=source["file"], line=source["line"],
                                   definition_id=key)
                    continue
                chosen[key] = entries[0]
        for key, record in records:
            if key in chosen:
                value, source = chosen[key]
                record["name"][language] = value
                record["name_sources"][language] = source.copy()
            elif key in remaining:
                report.add("warning", "missing_translation", "localization",
                           f"No {language} name found for {key}", source="TECH_PATH",
                           file=record["source"]["file"], line=record["source"]["line"],
                           definition_id=key, field_path=f"name.{language}")
