"""Orchestrate a build using the selected profile, without running the analyzer."""

from sttv.technologies.definitions import collect_definitions
from sttv.localization.names import collect_names
from sttv.common.report import Report
from sttv.sources.settings import check_sources, load_settings
from sttv.database.storage import publish, write_report
from sttv.database.validation import validate_database
from sttv.rules.operations import generate


def build(variables_path, config_path):
    report = Report()
    settings = None
    stage = "configuration"
    try:
        settings = load_settings(variables_path, config_path)
        check_sources(settings)
        stage = "rules"
        registry, _ = generate(settings)
        report.data["registry_written"] = True
        report.data["generation_report_written"] = True
        version = settings.options["rules"]["game_version"]
        if version and registry["game_version"] and version != registry["game_version"]:
            report.add("warning", "version_mismatch", stage,
                       f"Source version {version}; profile version {registry['game_version']}")
        stage = "definitions"
        database = collect_definitions(settings, report, registry)
        if not report.failed:
            stage = "localization"
            collect_names(settings, database, report)
        if not report.failed:
            stage = "validation"
            validate_database(database, registry)
        if not report.failed:
            stage = "storage"
            publish(settings, database, report)
    except Exception as exc:
        report.data["status"] = "failed"
        if getattr(exc, "result", {}).get("registry_written"):
            report.data["registry_written"] = True
        report.failure(exc, stage)
    if report.failed and settings is not None:
        try:
            write_report(settings, report)
        except Exception as exc:
            report.failure(exc, "report")
    return report.data
