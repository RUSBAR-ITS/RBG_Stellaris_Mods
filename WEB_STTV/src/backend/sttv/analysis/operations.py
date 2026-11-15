"""Programmatic source analysis and separately requested report persistence."""

from hashlib import sha256
from pathlib import Path

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.paths import distinct_paths, output_path
from sttv.common.persistence import save_json
from sttv.common.report import Report
from sttv.common.schema import validate_schema
from sttv.rules.compiler import generate_registry, load_profile
from sttv.script.parser import parse_text
from sttv.script.serialization import data_entries
from sttv.rules.validation import validate_registry_syntax
from sttv.sources.files import source_files
from .adapters import documentation, script_definitions
from .recommendations import recommend, validate_recommendation_profile
from .sources import selected_sources
from .walker import Walker


def analyze(settings, config_path, profile=None):
    options = read_json(config_path)
    validate_schema(options, "analysis.schema.json")
    profile = load_profile(settings.profile) if profile is None else profile
    registry = generate_registry(profile)
    validate_registry_syntax(registry, settings.syntax)
    diagnostics = Report()
    result = {
        "format_version": 1, "status": "complete",
        "profile_id": profile["profile_id"], "profile_revision": profile["revision"],
        "profile_fingerprint": registry["profile_fingerprint"],
        "sources": [], "observations": [], "recommendations": [], "diagnostics": [],
        "counts": {"skipped_inline_scripts": 0},
    }
    for source in selected_sources(settings, options):
        manifest = {key: source[key] for key in ("id", "kind", "path", "enabled", "game_version")}
        manifest.update(status="disabled" if not source["enabled"] else "read", files=[])
        result["sources"].append(manifest)
        if not source["enabled"]:
            continue
        version = source["game_version"]
        if version is None:
            diagnostics.add("warning", "unknown_version", "analysis",
                            "Source version is not established", source=source["id"])
        elif profile["game_version"] and version != profile["game_version"]:
            diagnostics.add("warning", "version_mismatch", "analysis",
                            f"Source version {version}; profile version {profile['game_version']}",
                            source=source["id"])
        directory = Path(source["path"])
        try:
            if not directory.is_dir():
                manifest["status"] = "unavailable"
                raise BuildError("source_unavailable", f"Source directory unavailable: {directory}")
            files = list(source_files(directory, source["pattern"], source["recursive"]))
            if not files:
                manifest["status"] = "empty"
                raise BuildError("empty_source", "Enabled source contains no matching files")
        except (BuildError, OSError) as exc:
            diagnostics.failure(exc, "analysis", source=source["id"])
            manifest["status"] = "partial" if manifest["status"] == "read" else manifest["status"]
            continue
        for path in files:
            relative = path.relative_to(directory).as_posix()
            try:
                raw = path.read_bytes()
                manifest["files"].append({"file": relative, "sha256": sha256(raw).hexdigest()})
                text = raw.decode(source["encoding"])
                walker = Walker(registry, source["id"], relative, text, options["excerpt_length"])
                if source["kind"] == "engine_documentation":
                    rows = documentation(walker, text, settings.syntax)
                else:
                    document = parse_text(text, settings.syntax, relative)
                    result["counts"]["skipped_inline_scripts"] += len(document.skipped_inline_scripts)
                    nodes = data_entries(document, purpose="analysis")
                    rows = (walker.technologies(nodes, source["kind"])
                            if source["kind"] in settings.options["definitions"]
                            else script_definitions(walker, nodes, source["kind"], relative))
                result["observations"].extend(rows)
            except (BuildError, OSError, ValueError, RecursionError) as exc:
                manifest["status"] = "partial"
                diagnostics.failure(exc, "analysis", source=source["id"], file=relative)
    result["recommendations"] = recommend(result["observations"], profile, registry, options["max_examples"])
    result["diagnostics"] = diagnostics.data["diagnostics"]
    if diagnostics.failed:
        result["status"] = "partial"
    validate_schema(result, "analysis_report.schema.json")
    return result


def save_analysis(settings, config_path, result):
    options = read_json(config_path)
    validate_schema(options, "analysis.schema.json")
    validate_schema(result, "analysis_report.schema.json")
    validate_recommendation_profile(result, load_profile(settings.profile))
    sources = selected_sources(settings, options)
    roots = [*settings.protected, *(Path(item["path"]) for item in sources if item["enabled"])]
    path = output_path(settings.work, options["output"], roots)
    distinct_paths([path, settings.profile, settings.registry, settings.database, settings.report,
                    settings.generation_report, *settings.config_files, Path(config_path).resolve()])
    return save_json(path, result, "analysis_report.schema.json")
