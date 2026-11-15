"""Orchestrate one complete build without a UI or game-source mutation."""

from .definitions import collect_definitions
from .localization import collect_names
from .report import Report
from .settings import check_sources, load_settings
from .storage import publish, write_report
from .validation import validate_database


def build(variables_path, config_path):
    report = Report()
    settings = None
    stage = "configuration"
    try:
        settings = load_settings(variables_path, config_path)
        check_sources(settings)
        stage = "definitions"
        database = collect_definitions(settings, report)
        if not report.failed:
            stage = "localization"
            collect_names(settings, database, report)
        if not report.failed:
            stage = "validation"
            validate_database(database)
        if not report.failed:
            stage = "storage"
            publish(settings, database, report)
    except Exception as exc:
        report.data["status"] = "failed"
        report.failure(exc, stage)
    if report.failed and settings is not None:
        try:
            write_report(settings, report)
        except Exception as exc:
            report.failure(exc, "report")
    return report.data
