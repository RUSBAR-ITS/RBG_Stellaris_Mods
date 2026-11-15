"""Build diagnostics and read-only input manifests."""

from .helpers import BOOL, HASH, LINE, NULL, RELATIVE, STRING, TEXT, array, mapping, obj, union
from . import inline


def diagnostic():
    return obj({
        "severity": {"enum": ["error", "warning"]}, "code": TEXT, "stage": TEXT,
        "message": STRING, "source": union(TEXT, NULL), "file": union(RELATIVE, NULL),
        "line": union(LINE, NULL), "field_path": union(TEXT, NULL),
        "column": union(LINE, NULL), "provenance": union({"$ref": "#/$defs/origin"}, NULL),
        "root_source": union({"$ref": "#/$defs/origin"}, NULL), "call_chain": inline.chain(),
    })


def schema():
    result = obj({"format_version": {"const": 2}, "status": {"enum": ["success", "failed"]},
                  "counts": obj({**{key: {"type": "integer", "minimum": 0} for key in
                                    ("selected_files", "parsed_files", "failed_files", "nodes", "errors", "warnings")},
                                 "inline_scripts": inline.counts()}),
                  "sources": mapping(HASH, RELATIVE), "inline_sources": mapping(HASH, RELATIVE),
                  "database_written": BOOL, "diagnostics": array(diagnostic())})
    result["$defs"] = {"origin": inline.origin()}
    return result
