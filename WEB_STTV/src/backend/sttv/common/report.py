"""Build diagnostics, separate from application database data."""


class Report:
    def __init__(self):
        self.data = {
            "format_version": 1,
            "status": "failed",
            "counts": {"files": 0, "technologies": 0, "variants": 0,
                       "errors": 0, "warnings": 0,
                       "inline_scripts": dict(encountered=0, expanded=0, failed=0, template_files=0, max_depth=0)},
            "inline_sources": {},
            "diagnostics": [],
            "database_written": False,
            "registry_written": False,
            "generation_report_written": False,
        }

    def add(self, severity, code, stage, message, **location):
        row = {
            "severity": severity, "code": code, "stage": stage,
            "message": str(message), "source": None, "file": None,
            "line": None, "definition_id": None, "field_path": None,
            "column": None, "provenance": None, "root_source": None, "call_chain": [],
        }
        row.update(location)
        self.data["diagnostics"].append(row)
        self.data["counts"][severity + "s"] += 1

    def failure(self, error, stage, **location):
        compact = getattr(error, "source_location", None)
        if compact:
            location.update(source=compact["root"], file=compact["file"],
                            line=compact["line"], column=compact["column"])
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
