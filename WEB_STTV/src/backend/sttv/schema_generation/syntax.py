"""Closed declarations for lexical notation and implemented construct switches."""

from .helpers import BOOL, TEXT, array, obj


def lexical():
    return obj({
        "format_version": {"const": 1}, "allow_initial_bom": BOOL,
        "whitespace": array({"type": "string", "minLength": 1, "maxLength": 1},
                            minItems=1, uniqueItems=True),
        "line_comment": TEXT,
        "string": obj({"quote": TEXT, "escape": TEXT, "multiline": BOOL}),
        "operators": array(TEXT, minItems=1, uniqueItems=True),
        "block": obj({"open": TEXT, "close": TEXT}),
    })


def constructs():
    return obj({
        "format_version": {"const": 1}, "bare_values": BOOL,
        "anonymous_blocks": BOOL, "mixed_blocks": BOOL,
        "tagged_blocks": array(TEXT, uniqueItems=True),
        "parameters": obj({"open": TEXT, "close": TEXT, "default_separator": TEXT}),
        "formulas": array(obj({"open": TEXT, "close": TEXT}), minItems=1, uniqueItems=True),
        "conditional": obj({"open": TEXT, "header_close": TEXT,
                            "body_close": TEXT, "negation": TEXT}),
        "inline_script": obj({"keyword": TEXT, "case_sensitive": BOOL}),
    })


def logical_operators():
    return obj({"format_version": {"const": 1}, "case_sensitive": BOOL,
                "assignment_operator": TEXT, "operators": array(TEXT, uniqueItems=True)})
