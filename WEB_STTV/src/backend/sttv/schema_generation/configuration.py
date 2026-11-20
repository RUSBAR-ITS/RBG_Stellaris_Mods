"""Schemas for source selection and parser configuration."""

from .helpers import BOOL, RELATIVE, TEXT, array, obj


def selection(*bases):
    return obj({"base": {"enum": ["product", "work", *bases]}, "path": RELATIVE})


def schema():
    source = obj({"variable": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$"},
                  "pattern": TEXT, "recursive": BOOL, "encoding": TEXT})
    return obj({
        "libraries": selection(),
        "parallel": selection(),
        "storage": selection(),
        "sources": array(source, minItems=1),
        "parser": obj({key: selection("parser") for key in
                       ("lexical", "constructs", "logical_operators", "inline_scripts", "exceptions",
                        "static_variables", "scripted_calls", "script_values", "source_exceptions")}),
        "outputs": obj({"report": RELATIVE}),
    })
