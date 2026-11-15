"""Schemas for source selection and parser configuration."""

from .helpers import BOOL, RELATIVE, TEXT, array, obj


def selection():
    return obj({"base": {"enum": ["product", "work"]}, "path": RELATIVE})


def schema():
    source = obj({"variable": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$"},
                  "pattern": TEXT, "recursive": BOOL, "encoding": TEXT})
    return obj({
        "sources": array(source, minItems=1),
        "parser": obj({key: selection() for key in
                       ("lexical", "constructs", "logical_operators", "inline_scripts", "exceptions",
                        "static_variables", "scripted_calls", "script_values")}),
        "outputs": obj({"database": RELATIVE, "report": RELATIVE}),
    })
