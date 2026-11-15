"""Collect the three permitted technology-definition collections."""

from .conversion import Converter, envelope
from .errors import BuildError
from .parser import parse_text
from .script_rules import ScriptRules
from .sources import read_source, source_files
from .variables import Variables


def collect_definitions(settings, report):
    database = {"format_version": 1, "technologies": {}, "categories": {},
                "tiers": {}, "file_variables": {}}
    rules = ScriptRules()
    seen_files = set()
    for collection, profile in settings.options["definitions"].items():
        directory = (settings.technology / profile["subdirectory"]).resolve()
        for path in source_files(directory, profile["pattern"], profile["recursive"]):
            relative = path.relative_to(settings.technology).as_posix()
            location = {"source": "TECH_PATH", "file": relative}
            try:
                if path.resolve() in seen_files:
                    raise BuildError("source_overlap", "Definition source profiles overlap")
                seen_files.add(path.resolve())
                nodes = parse_text(read_source(path, profile["encoding"], report))
                variables = Variables(nodes)
                if variables.definitions:
                    database["file_variables"][relative] = variables.definitions
            except (BuildError, OSError, ValueError) as exc:
                report.failure(exc, "parsing", **location)
                continue
            for node in nodes:
                if node.key and node.key.startswith("@"):
                    continue
                record_location = dict(location, line=node.line, definition_id=node.key)
                try:
                    if not node.key or node.operator != "=" or not isinstance(node.value, list):
                        raise BuildError("invalid_definition", "Expected a named definition block")
                    if node.key in database[collection]:
                        raise BuildError("duplicate_definition", f"Duplicate ID: {node.key}")
                    converter = Converter(variables, rules, report, relative, node.key)
                    source = {"file": relative, "line": node.line}
                    record = (envelope(source) if collection == "technologies"
                              else {"source": source, "fields": {}})
                    record["fields"] = converter.fields(node.value, collection)
                    database[collection][node.key] = record
                except BuildError as exc:
                    report.failure(exc, "conversion", **record_location)
    report.data["counts"]["technologies"] = len(database["technologies"])
    report.data["counts"]["variants"] = sum(
        len(record["fields"].get("technology_swap", []))
        for record in database["technologies"].values())
    return database
