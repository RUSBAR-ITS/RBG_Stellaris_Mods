"""Schemas for explicit builder and analyzer input configuration."""

from .helpers import BOOL, NULL, RELATIVE, STRING, TEXT, array, obj, union


def selection():
    return obj({"base": {"enum": ["product", "work"]}, "path": RELATIVE})


def schema():
    profile = obj({"variable": {"const": "TECH_PATH"}, "subdirectory": STRING,
                   "pattern": TEXT, "recursive": BOOL, "encoding": {"const": "utf-8-sig"}})
    language = obj({"header": TEXT, "sources": array(TEXT, minItems=1, uniqueItems=True)})
    return obj({
        "definitions": obj({key: profile for key in ("technologies", "categories", "tiers")}),
        "localization": obj({"pattern": TEXT, "recursive": BOOL, "encoding": {"const": "utf-8-sig"},
                             "languages": obj({key: language for key in ("ru", "en")})}),
        "parser": obj({key: selection() for key in ("lexical", "constructs")}),
        "outputs": obj({"database": RELATIVE, "report": RELATIVE}),
        "rules": obj({"profile": selection(), "registry": RELATIVE, "report": RELATIVE,
                      "game_version": union(TEXT, NULL)}),
    })


def analysis():
    source = obj({
        "id": TEXT, "kind": {"enum": ["engine_documentation", "scripted_triggers", "inline_scripts"]},
        "path": TEXT, "pattern": TEXT, "recursive": BOOL,
        "encoding": {"const": "utf-8-sig"}, "enabled": BOOL,
        "game_version": union(TEXT, NULL),
    })
    return obj({"format_version": {"const": 1}, "sources": array(source),
                "output": RELATIVE, "max_examples": {"type": "integer", "minimum": 1},
                "excerpt_length": {"type": "integer", "minimum": 1, "maximum": 500}})
