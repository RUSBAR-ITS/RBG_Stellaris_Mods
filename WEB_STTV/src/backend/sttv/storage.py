"""Prepare validated files and publish without exposing partial JSON."""

import os
import tempfile
from pathlib import Path

from .json_io import json_text, read_json
from .schema import validate_schema


def prepare_json(path, value, schema):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         prefix=path.name + ".", suffix=".tmp",
                                         dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(json_text(value))
            handle.flush()
            os.fsync(handle.fileno())
        validate_schema(read_json(temporary), schema)
        return temporary
    except BaseException:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise


def write_report(settings, report):
    temporary = prepare_json(settings.report, report.data, "report.schema.json")
    try:
        os.replace(temporary, settings.report)
    finally:
        temporary.unlink(missing_ok=True)


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
