"""Build diagnostics, separate from application database data."""


class Report:
    def __init__(self):
        self.data = {
            "format_version": 1,
            "status": "failed",
            "counts": {"files": 0, "technologies": 0, "variants": 0,
                       "errors": 0, "warnings": 0},
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
        }
        row.update(location)
        self.data["diagnostics"].append(row)
        self.data["counts"][severity + "s"] += 1

    def failure(self, error, stage, **location):
        location["line"] = getattr(error, "line", None) or location.get("line")
        location["field_path"] = (
            getattr(error, "field_path", None) or location.get("field_path")
        )
        self.add("error", getattr(error, "code", "build_error"), stage,
                 str(error), **location)

    @property
    def failed(self):
        return self.data["counts"]["errors"] > 0
