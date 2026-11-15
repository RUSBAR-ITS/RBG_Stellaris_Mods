"""Database schema generated directly from the converter's field contract."""

from sttv.technologies.contracts import AREAS, CONTRACTS, SCRIPT_CONTEXTS, SCRIPT_OPERATORS
from .helpers import (BOOL, IDENTIFIER, LINE, NULL, NUMBER, RELATIVE, STRING, TEXT,
                      VARIABLE_NAME, array, mapping, obj, ref, repeated, union)
from . import inline


def fields(context):
    variable = obj({"variable": VARIABLE_NAME, "resolved": union(NUMBER, NULL)})
    integer = union({"type": "integer"}, obj({
        "variable": VARIABLE_NAME, "resolved": union({"type": "integer"}, NULL)}))
    kinds = {
        "area": {"enum": list(AREAS)}, "number": union(NUMBER, variable),
        "integer": integer, "cost": union(NUMBER, variable, ref("script")),
        "identifier": IDENTIFIER, "boolean": BOOL, "list": array(IDENTIFIER),
        "requirements": ref("requirement"), "variant": ref("variant"),
        **{kind: ref("script") for kind in SCRIPT_CONTEXTS},
    }
    return obj({name: array(kinds[field.kind], minItems=1) if field.multiple
                else repeated(kinds[field.kind]) for name, field in CONTRACTS[context].items()}, [])


def record(context):
    value = obj({
        "source": ref("source"), "fields": fields(context),
        "name": obj({lang: union(STRING, NULL) for lang in ("ru", "en")}),
        "name_sources": obj({lang: union(ref("localization_source"), NULL) for lang in ("ru", "en")}),
        **({"name_key": TEXT} if context == "variant" else {}),
    })
    value["allOf"] = [
        {"if": {"properties": {"name": {"properties": {lang: NULL}}}},
         "then": {"properties": {"name_sources": {"properties": {lang: NULL}}}},
         "else": {"properties": {"name_sources": {
             "properties": {lang: ref("localization_source")}}}}}
        for lang in ("ru", "en")]
    return value


def schema():
    entry = obj({"key": union(TEXT, NULL), "operator": {"enum": [*sorted(SCRIPT_OPERATORS), None]},
                 "value": union(STRING, ref("script")), "source": ref("source")})
    entry["allOf"] = [{"if": {"properties": {"key": NULL}},
                      "then": {"properties": {"operator": NULL}},
                      "else": {"properties": {"operator": STRING}}}]
    defs = {
        "script": obj({"entries": array(entry)}),
        "source": inline.location(),
        "origin": inline.origin(),
        "localization_source": obj({"tier": TEXT, "file": RELATIVE, "line": LINE, "key": TEXT}),
        "requirement": union(obj({"tech": IDENTIFIER}), obj({"all": array(ref("requirement"))}),
                             obj({"any": array(ref("requirement"))})),
        "technology": record("technologies"), "variant": record("variant"),
        "category": obj({"source": ref("source"), "fields": fields("categories")}),
        "tier": obj({"source": ref("source"), "fields": fields("tiers")}),
    }
    result = obj({"format_version": {"const": 2}, "technologies": mapping(ref("technology")),
                  "metadata": obj({"inline_scripts": array(inline.call())}),
                  "categories": mapping(ref("category")),
                  "tiers": mapping(ref("tier"), {"pattern": "^[0-9]+$"}),
                  "file_variables": mapping(array(obj({
                      "name": VARIABLE_NAME, "value": STRING, "source": ref("source")})), RELATIVE)})
    result["$defs"] = defs
    return result
