"""Declared diagnostics shared by build, analysis, and generation reports."""

from .helpers import BOOL, HASH, LINE, NULL, RELATIVE, STRING, TEXT, array, mapping, obj, union
from . import inline


def diagnostic():
    return obj({
        "severity": {"enum": ["error", "warning"]}, "code": TEXT, "stage": TEXT,
        "message": STRING, "source": union(TEXT, NULL), "file": union(RELATIVE, NULL),
        "line": union(LINE, NULL), "definition_id": union(TEXT, NULL),
        "field_path": union(TEXT, NULL),
        "column": union(LINE, NULL), "provenance": union({"$ref": "#/$defs/origin"}, NULL),
        "root_source": union({"$ref": "#/$defs/origin"}, NULL), "call_chain": inline.chain(),
    })


def schema():
    result = obj({"format_version": {"const": 1}, "status": {"enum": ["success", "failed"]},
                "counts": obj({**{key: {"type": "integer", "minimum": 0}
                               for key in ("files", "technologies", "variants", "errors", "warnings")},
                               "inline_scripts": inline.counts()}),
                "inline_sources": mapping(HASH, RELATIVE),
                "database_written": BOOL, "registry_written": BOOL,
                "generation_report_written": BOOL, "diagnostics": array(diagnostic())})
    result["$defs"] = {"origin": inline.origin()}
    return result
