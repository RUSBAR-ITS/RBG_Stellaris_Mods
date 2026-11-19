"""Localized-field diagnostics and reproducible provenance inventories."""

from sttv.common.datasets import KINDS


def new_report():
    return {"format": "sttv.localization_report", "format_version": 2,
            "status": "running", "database_written": False,
            "paths": {"database": None, "report": None},
            "database_before": None, "database_after": None, "settings": None,
            "inputs": [], "counts": {**dict.fromkeys((*KINDS, 'variants', 'descriptions', 'objects', 'targets'), 0), 'languages': {}},
            "duplicates": [], "selected_sources": [], "diagnostics": [], "seconds": 0.0}


def diagnostic(report, severity, code, message, stage, **context):
    row = {"severity": severity, "code": code, "message": str(message), "stage": stage,
           "node": None, "language": None, "field": None, "requested_key": None,
           "source": None, "line": None, "chain": []}
    row.update(context)
    report["diagnostics"].append(row)


def failure(report, exc, stage, **context):
    details = dict(getattr(exc, "context", {}))
    known = {'node', 'language', 'field', 'requested_key', 'source', 'line', 'chain'}
    if 'document_id' in details:
        known.discard('source')
    extra = {key: value for key, value in details.items() if key not in known}
    details = {key: value for key, value in details.items() if key in known}
    details.update(context)
    if extra:
        details['details'] = extra
    details.setdefault("line", getattr(exc, "line", None))
    diagnostic(report, "error", getattr(exc, "code", "localization_error"), exc, stage, **details)


def failed(report):
    return any(item["severity"] == "error" for item in report["diagnostics"])


def count_field(report, language, field, value):
    fields = report["counts"]["languages"].setdefault(language, {})
    counts = fields.setdefault(field, dict.fromkeys(("found", "missing", "inherited", "unresolved"), 0))
    counts["found" if value["key"] is not None else "missing"] += 1
    counts["inherited"] += int(value["inherited_from"] is not None)
    counts["unresolved"] += int(bool(value["unresolved_references"]))
