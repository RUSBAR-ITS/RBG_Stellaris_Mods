"""Collect selected source documents without domain projection or enrichment."""

from sttv.script.parser import parse_text
from sttv.script.serialization import serialize_document, walk_nodes
from sttv.sources.expansion import expansion_context
from sttv.sources.files import selected_files, read_source
from .validation import FORMAT, FORMAT_VERSION


def collect(settings, report):
    database = {"format": FORMAT, "format_version": FORMAT_VERSION, "documents": []}
    expansion = expansion_context(settings, report)
    files = selected_files(settings)
    report.data["counts"]["selected_files"] = len(files)
    for path, encoding in files:
        relative = path.relative_to(settings.game).as_posix()
        try:
            text = read_source(path, encoding, report, relative)
            parsed = parse_text(text, settings.syntax, relative, expansion=expansion)
            document = serialize_document(parsed)
            database["documents"].append(document)
            report.data["counts"]["nodes"] += sum(1 for _ in walk_nodes(document["items"]))
            report.data["counts"]["parsed_files"] += 1
        except Exception as exc:
            report.data["counts"]["failed_files"] += 1
            report.failure(exc, "parsing", source="STELLARIS_ROOT", file=relative)
        finally:
            report.data["counts"]["inline_scripts"] = dict(expansion.counts)
            report.data["inline_sources"] = dict(sorted(expansion.templates.manifest.items()))
    return database
