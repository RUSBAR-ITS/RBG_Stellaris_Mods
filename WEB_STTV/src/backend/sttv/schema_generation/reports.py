"""Declared diagnostics shared by build, analysis, and generation reports."""

from .helpers import BOOL, LINE, NULL, RELATIVE, STRING, TEXT, array, obj, union


def diagnostic():
    return obj({
        "severity": {"enum": ["error", "warning"]}, "code": TEXT, "stage": TEXT,
        "message": STRING, "source": union(TEXT, NULL), "file": union(RELATIVE, NULL),
        "line": union(LINE, NULL), "definition_id": union(TEXT, NULL),
        "field_path": union(TEXT, NULL),
    })


def schema():
    return obj({"format_version": {"const": 1}, "status": {"enum": ["success", "failed"]},
                "counts": obj({key: {"type": "integer", "minimum": 0}
                               for key in ("files", "technologies", "variants", "errors", "warnings", "skipped_inline_scripts")}),
                "database_written": BOOL, "registry_written": BOOL,
                "generation_report_written": BOOL, "diagnostics": array(diagnostic())})
