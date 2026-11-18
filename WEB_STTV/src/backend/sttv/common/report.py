"""Build diagnostics, separate from application database data."""

from .timing import performance

class Report:
    def __init__(self):
        self.data = {
            "format_version": 5,
            "status": "failed",
            "counts": {"selected_files": 0, "parsed_files": 0, "failed_files": 0, "nodes": 0,
                       "errors": 0, "warnings": 0,
                       'max_call_depth': 0,
                       'source_exceptions': {},
                       'parameters': dict(defaults=0, retained_fragments=0, discarded_fragments=0),
                       'scripted_calls': {kind: dict(files=0, definitions=0, local_definitions=0,
                            encountered=0, expanded=0, failed=0, tests=0)
                            for kind in ('scripted_effect', 'scripted_trigger', 'script_value')},
                       "static_variables": dict(files=0, global_definitions=0, local_definitions=0,
                                                references=0, substituted=0),
                       "inline_scripts": dict(encountered=0, expanded=0, failed=0, template_files=0, max_depth=0)},
            "sources": {},
            "inline_sources": {},
            "static_variable_sources": {},
            'scripted_effect_sources': {},
            'scripted_trigger_sources': {},
            'script_value_sources': {},
            'library_fields': {},
            'source_exceptions': [],
            "diagnostics": [],
            "database_written": False,
            'performance': performance(),
        }

    def add(self, severity, code, stage, message, **location):
        row = {
            "severity": severity, "code": code, "stage": stage,
            "message": str(message), "source": None, "file": None,
            "line": None, "field_path": None,
            "column": None, "provenance": None, "root_source": None, "call_chain": [],
        }
        row.update(location)
        self.data["diagnostics"].append(row)
        self.data["counts"][severity + "s"] += 1

    def failure(self, error, stage, **location):
        origin = getattr(error, "provenance", None)
        if origin:
            location.update(source=origin["root"], file=origin["file"],
                            line=origin["span"]["line"], column=origin["span"]["column"], provenance=origin)
        location["call_chain"] = getattr(error, "call_chain", [])
        location["root_source"] = getattr(error, "root_source", None)
        location["line"] = getattr(error, "line", None) or location.get("line")
        location["field_path"] = (
            getattr(error, "field_path", None) or location.get("field_path")
        )
        self.add("error", getattr(error, "code", "build_error"), stage,
                 str(error), **location)

    @property
    def failed(self):
        return self.data["counts"]["errors"] > 0
