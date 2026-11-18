"""Build diagnostics and read-only input manifests."""

from .helpers import BOOL, HASH, LINE, NULL, RELATIVE, STRING, TEXT, array, mapping, obj, union
from . import inline, static_variables, scripted, source_exceptions, performance


def diagnostic():
    return obj({
        "severity": {"enum": ["error", "warning"]}, "code": TEXT, "stage": TEXT,
        "message": STRING, "source": union(TEXT, NULL), "file": union(RELATIVE, NULL),
        "line": union(LINE, NULL), "field_path": union(TEXT, NULL),
        "column": union(LINE, NULL), "provenance": union({"$ref": "#/$defs/origin"}, NULL),
        "root_source": union({"$ref": "#/$defs/origin"}, NULL), "call_chain": inline.chain(),
    })


def schema():
    result = obj({"format_version": {"const": 5}, "status": {"enum": ["success", "failed"]},
                  "counts": obj({**{key: {"type": "integer", "minimum": 0} for key in
                                    ("selected_files", "parsed_files", "failed_files", "nodes", "errors", "warnings")},
                                 "inline_scripts": inline.counts(), "static_variables": static_variables.counts(),
                                 'scripted_calls': scripted.counts(), 'parameters': scripted.parameters(),
                                 'source_exceptions': mapping({'type': 'integer', 'minimum': 0}),
                                 'max_call_depth': {'type': 'integer', 'minimum': 0}}),
                  "sources": mapping(HASH, RELATIVE), "inline_sources": mapping(HASH, RELATIVE),
                  "static_variable_sources": mapping(HASH, RELATIVE),
                  'scripted_effect_sources': mapping(HASH, RELATIVE),
                  'scripted_trigger_sources': mapping(HASH, RELATIVE),
                  'script_value_sources': mapping(HASH, RELATIVE),
                  'library_fields': mapping(mapping(STRING), RELATIVE),
                  'source_exceptions': array(source_exceptions.application()),
                  "database_written": BOOL, "diagnostics": array(diagnostic()), 'performance': performance.schema()})
    result["$defs"] = {"origin": inline.origin()}
    return result
