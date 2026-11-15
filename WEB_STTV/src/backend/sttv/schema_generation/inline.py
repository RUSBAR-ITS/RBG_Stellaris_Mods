"""Closed contracts for inline settings, history, and source provenance."""

from .helpers import BOOL, LINE, NULL, RELATIVE, STRING, TEXT, array, obj, union


def configuration():
    return obj({"format_version": {"const": 1},
                "path_field": {"type": "string", "pattern": "^[A-Za-z_][A-Za-z0-9_]*$"},
                "parameter_case_sensitive": BOOL,
                "extension": {"type": "string", "pattern": "^\\.[A-Za-z0-9]+$"},
                "encoding": TEXT, "max_depth": {"type": "integer", "minimum": 1}})


def counts():
    return obj({key: {"type": "integer", "minimum": 0} for key in
                ("encountered", "expanded", "failed", "template_files", "max_depth")})


def location():
    return obj({"root": {"enum": ["STELLARIS_ROOT", "TECH_PATH", "INLINE_SCRIPTS_DIR"]},
                "file": RELATIVE, "line": LINE, "column": LINE,
                "inline_call_id": union(TEXT, NULL)})


def span():
    return obj({key: {"type": "integer", "minimum": 0 if key in ("start", "end") else 1}
                for key in ("start", "end", "line", "column", "end_line", "end_column")})


def origin():
    properties = {key: val for key, val in location()["properties"].items() if key not in ("line", "column")}
    properties.update(span=span(), generated_span=span(), fragments=array({"$ref": "#/$defs/origin"}),
                      placeholder={"$ref": "#/$defs/origin"})
    return obj(properties, ["root", "file", "span", "inline_call_id"])


def call():
    return obj({"id": TEXT, "parent_id": union(TEXT, NULL),
                "call_site": {"$ref": "#/$defs/origin"}, "form": {"enum": ["reference", "block"]},
                "script": obj({"raw": STRING, "value": TEXT}), "template": RELATIVE,
                "arguments": array(obj({"name": TEXT, "raw": STRING, "value": STRING})),
                "insertion": obj({"container": TEXT, "index": {"type": "integer", "minimum": 0},
                                  "count": {"type": "integer", "minimum": 0}})})


def chain():
    return array(obj({"id": TEXT, "template": union(RELATIVE, NULL),
                      "call_site": {"$ref": "#/$defs/origin"}}))
