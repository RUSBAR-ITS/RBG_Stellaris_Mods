"""Publish a validated database and report; track each replacement separately."""

import os

from sttv.common.persistence import save_json
from sttv.common.schema import schema_operation
from sttv.common.timing import measure


def write_report(settings, report):
    save_json(settings.report, report.data, "report.schema.json")


def publish(settings, database_temp, report):
    try:
        report.data["status"] = "success"
        report.data["database_written"] = False
        with measure(report.data['performance']['timings'], 'publish'):
            os.replace(database_temp, settings.database)
        report.data["database_written"] = True
        write_report(settings, report)
    except BaseException:
        report.data["status"] = "failed"
        if database_temp is not None and database_temp.exists():
            report.data["database_written"] = False
        raise
    finally:
        database_temp.unlink(missing_ok=True)


@schema_operation
def read_database(path):
    """Load a persisted tree without loading game or parser configuration."""
    from sttv.common.json_io import read_json
    from .validation import validate_database
    value = read_json(path)
    validate_database(value)
    return value
