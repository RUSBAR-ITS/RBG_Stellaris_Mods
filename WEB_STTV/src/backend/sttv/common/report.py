"""Build diagnostics, separate from application database data."""


class Report:
    def __init__(self):
        self.data = {
            "format_version": 3,
            "status": "failed",
            "counts": {"selected_files": 0, "parsed_files": 0, "failed_files": 0, "nodes": 0,
                       "errors": 0, "warnings": 0,
                       "static_variables": dict(files=0, global_definitions=0, local_definitions=0,
                                                references=0, substituted=0),
                       "inline_scripts": dict(encountered=0, expanded=0, failed=0, template_files=0, max_depth=0)},
            "sources": {},
            "inline_sources": {},
            "static_variable_sources": {},
            "diagnostics": [],
            "database_written": False,
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
