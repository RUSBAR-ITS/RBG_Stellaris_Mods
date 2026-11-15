"""Coordinate read-only parsing and publication of a syntax-tree database."""

from sttv.common.report import Report
from sttv.sources.settings import check_sources, load_settings
from sttv.database.collection import collect
from sttv.database.storage import publish, write_report
from sttv.database.validation import validate_database


def build(variables_path, config_path):
    report, settings, stage = Report(), None, "configuration"
    try:
        settings = load_settings(variables_path, config_path)
        check_sources(settings)
        stage = "parsing"
        database = collect(settings, report)
        if not report.failed:
            stage = "validation"
            validate_database(database)
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
