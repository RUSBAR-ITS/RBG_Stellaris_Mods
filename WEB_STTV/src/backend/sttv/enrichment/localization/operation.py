"""Coordinate in-place localization with validated atomic database publication."""

import os
from pathlib import Path
from time import perf_counter

from sttv.common.paths import PRODUCT_ROOT
from sttv.common.persistence import prepare_json, save_json
from sttv.database.validation import validate_database
from .attachment import attach
from .index import LocalizationIndex
from .references import Resolver
from .report import failed, failure, new_report
from .selection import select_targets
from .settings import load_settings
from .snapshot import Snapshot, digest


def enrich_localization(variables_path=None, config_path=None):
    variables_path = Path(variables_path) if variables_path else PRODUCT_ROOT / "global_variables.json"
    config_path = Path(config_path) if config_path else PRODUCT_ROOT / "config/enrichment/localization.json"
    start, report, settings, temporary = perf_counter(), new_report(), None, None
    snapshot, stage = Snapshot(report), "configuration"
    try:
        settings = load_settings(variables_path, config_path, snapshot)
        report["paths"] = {"database": str(settings.database), "report": str(settings.report)}
        report["settings"] = settings.options
        stage = "database"
        database = snapshot.json(settings.database, "database")
        report["database_before"] = snapshot.entries[settings.database]
        validate_database(database)
        stage = "selection"
        targets = select_targets(database, settings)
        stage = "sources"
        index = LocalizationIndex(settings, snapshot, report)
        stage = "enrichment"
        attach(database, targets, settings, Resolver(index, settings.options["references"]), report)
        report["selected_sources"] = [index.selected[key] for key in sorted(index.selected)]
        if not failed(report):
            stage = "publication"
            temporary = prepare_json(settings.database, database, validator=validate_database)
            checksum = digest(temporary)
            snapshot.verify()
            index.verify_files()
            os.replace(temporary, settings.database)
            report["database_written"] = True
            report["database_after"] = checksum
    except Exception as exc:
        failure(report, exc, stage)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    report["status"] = "failed" if failed(report) else "success"
    report["seconds"] = round(perf_counter() - start, 3)
    if settings is not None:
        try:
            save_json(settings.report, report, "localization_report.schema.json")
        except Exception as exc:
            report["status"] = "failed"
            failure(report, exc, "report")
    return report
