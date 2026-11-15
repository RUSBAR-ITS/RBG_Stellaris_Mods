"""Report shape independent of parser build reports."""

from .helpers import BOOL, HASH, LINE, NULL, STRING, TEXT, array, mapping, obj, union
from .localization import source


def schema():
    count = {"type": "integer", "minimum": 0}
    diagnostic = obj({"severity": {"enum": ["error", "warning"]}, "code": TEXT,
        "message": STRING, "stage": TEXT, "node": union(TEXT, NULL),
        "language": union(TEXT, NULL), "field": union(TEXT, NULL),
        "requested_key": union(TEXT, NULL), "source": union(source(), NULL),
        "line": union(LINE, NULL), "chain": array(TEXT)})
    return obj({"format": {"const": "sttv.localization_report"}, "format_version": {"const": 1},
        "status": {"enum": ["success", "failed", "running"]}, "database_written": BOOL,
        "paths": obj({"database": union(TEXT, NULL), "report": union(TEXT, NULL)}),
        "database_before": union(HASH, NULL), "database_after": union(HASH, NULL),
        "settings": union({"type": "object"}, NULL),
        "inputs": array(obj({"path": TEXT, "sha256": HASH, "kind": TEXT})),
        "counts": obj({"technologies": count, "variants": count,
            "languages": mapping(mapping(obj({key: count for key in ("found", "missing", "inherited", "unresolved")})))}),
        "duplicates": array(obj({"language": TEXT, "key": TEXT, "tier": TEXT, "conflicting": BOOL,
                                  "sources": array(source(), minItems=2)})),
        "selected_sources": array(obj({"language": TEXT, "key": TEXT, "source": source()})),
        "diagnostics": array(diagnostic), "seconds": {"type": "number", "minimum": 0}})
