"""Configuration and persisted text contracts for localization enrichment."""

from .helpers import BOOL, LINE, NULL, RELATIVE, STRING, TEXT, array, obj, union


def configuration():
    language = obj({"header": TEXT, "sources": array(TEXT, minItems=1, uniqueItems=True)})
    return obj({
        "format_version": {"const": 1}, "database": RELATIVE, "report": RELATIVE,
        "selection": obj({"variable": TEXT, "pattern": TEXT, "recursive": BOOL}),
        "keys": obj({"variant": TEXT, "name": TEXT, "description_suffix": TEXT}),
        "languages": obj({key: language for key in ("ru", "en")}),
        "reading": obj({"pattern": TEXT, "recursive": BOOL, "encoding": TEXT}),
        "references": obj({"delimiter": {"type": "string", "minLength": 1, "maxLength": 1},
                           "key_pattern": TEXT, "max_depth": LINE, "max_characters": LINE}),
        "inherit_description": BOOL,
    })


def source():
    return obj({"tier": TEXT, "file": {**RELATIVE, "pattern": r"^(?![A-Za-z]:)(?!/)(?!.*\\)(?!.*(?:^|/)\.\.(?:/|$)).+$"},
                "line": LINE})


def field():
    return obj({"requested_key": TEXT, "key": union(TEXT, NULL),
                "raw": union(STRING, NULL), "text": union(STRING, NULL),
                "source": union(source(), NULL),
                "inherited_from": union({"type": "string", "pattern": r"^/documents/\d+/items/\d+$"}, NULL),
                "unresolved_references": array(TEXT, uniqueItems=True)})


def enrichment():
    language = obj({"name": field(), "description": field()})
    return obj({"localization": obj({key: language for key in ("ru", "en")})}, required=[])
