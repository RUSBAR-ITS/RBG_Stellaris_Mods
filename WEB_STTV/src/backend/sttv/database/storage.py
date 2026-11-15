"""Publish a validated database and report; track each replacement separately."""

import os

from sttv.common.persistence import prepare_json, save_json


def write_report(settings, report):
    save_json(settings.report, report.data, "report.schema.json")


def publish(settings, database, report):
    database_temp = report_temp = None
    try:
        database_temp = prepare_json(settings.database, database, "database.schema.json")
        report.data["status"] = "success"
        report.data["database_written"] = True
        report_temp = prepare_json(settings.report, report.data, "report.schema.json")
        report.data["database_written"] = False
        os.replace(database_temp, settings.database)
        report.data["database_written"] = True
        os.replace(report_temp, settings.report)
    except BaseException:
        report.data["status"] = "failed"
        if database_temp is not None and database_temp.exists():
            report.data["database_written"] = False
        raise
    finally:
        for temporary in (database_temp, report_temp):
            if temporary is not None:
                temporary.unlink(missing_ok=True)


def read_database(path):
    """Load a persisted tree without loading game or parser configuration."""
    from sttv.common.json_io import read_json
    from .validation import validate_database
    value = read_json(path)
    validate_database(value)
    return value
