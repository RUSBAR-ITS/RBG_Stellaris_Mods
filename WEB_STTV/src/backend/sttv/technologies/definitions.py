"""Collect the three permitted technology-definition collections."""

from sttv.technologies.conversion import Converter, envelope
from sttv.common.errors import BuildError
from sttv.script.parser import parse_text
from sttv.script.diagnostics import annotate_error
from sttv.script.serialization import data_entries
from sttv.script.rules import ScriptRules
from sttv.sources.files import read_source, source_files
from sttv.script.variables import Variables
from sttv.script.traversal import source_location
from sttv.sources.expansion import expansion_context, independent_sources
from .provenance import Projection, pointer_part


def collect_definitions(settings, report, registry):
    database = {"format_version": 2, "technologies": {}, "categories": {},
                "tiers": {}, "file_variables": {}, "metadata": {"inline_scripts": []}}
    expansion = expansion_context(settings, report)
    report.data["counts"]["inline_scripts"] = expansion.counts
    rules = ScriptRules(registry)
    seen_files = set()
    for collection, profile in settings.options["definitions"].items():
        directory = (settings.technology / profile["subdirectory"]).resolve()
        for path in independent_sources(source_files(directory, profile["pattern"], profile["recursive"]), settings):
            relative = path.relative_to(settings.technology).as_posix()
            location = {"source": "TECH_PATH", "file": relative}
            stage = "parsing"
            try:
                if path.resolve() in seen_files:
                    raise BuildError("source_overlap", "Definition source profiles overlap")
                seen_files.add(path.resolve())
                document = parse_text(read_source(path, profile["encoding"], report), settings.syntax, relative,
                                      expansion=expansion, root="TECH_PATH")
                stage = "conversion"
                tracker = Projection(document.metadata["inline_scripts"])
                database["metadata"]["inline_scripts"].extend(tracker.records.values())
                nodes = data_entries(document)
                variables = Variables(nodes)
                if variables.definitions:
                    database["file_variables"][relative] = variables.definitions
                    for index, entry in enumerate(n for n in nodes if n.key and n.key.startswith("@")):
                        tracker.add(entry, f"/file_variables/{pointer_part(relative)}/{index}")
            except (BuildError, OSError, ValueError) as exc:
                if stage == "conversion":
                    annotate_error(exc, document)
                report.failure(exc, stage, **location)
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
                    converter = Converter(variables, rules, report, relative, node.key, tracker)
                    source = source_location(node.origin)
                    record = (envelope(source) if collection == "technologies"
                              else {"source": source, "fields": {}})
                    pointer = f"/{collection}/{pointer_part(node.key)}"
                    tracker.add(node, pointer)
                    record["fields"] = converter.fields(node.value, collection, pointer=pointer + "/fields")
                    database[collection][node.key] = record
                except BuildError as exc:
                    if not hasattr(exc, "provenance") and not hasattr(exc, "source_location"):
                        exc.provenance = node.origin
                    annotate_error(exc, document)
                    report.failure(exc, "conversion", **record_location)
    report.data["counts"]["technologies"] = len(database["technologies"])
    report.data["inline_sources"] = dict(sorted(expansion.templates.manifest.items()))
    report.data["counts"]["variants"] = sum(
        len(record["fields"].get("technology_swap", []))
        for record in database["technologies"].values())
    return database
