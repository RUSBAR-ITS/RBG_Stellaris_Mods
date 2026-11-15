"""Structural node contracts; game field names are unrestricted strings."""

from .helpers import BOOL, NULL, STRING, TEXT, array, obj, ref, union
from . import inline


def node(kind, properties):
    return obj({"kind": {"const": kind}, "span": inline.span(), "origin": ref("origin"), **properties})


def definitions():
    nodes = {
        "scalar": node("scalar", {"raw": STRING, "text": STRING, "quoted": BOOL,
            "parameters": array(obj({"name": TEXT, "default": union(STRING, NULL),
                                     "raw": STRING, "span": inline.span()}))}),
        "formula": node("formula", {"raw": STRING, "opener": TEXT, "body": STRING}),
        "block": node("block", {"items": array(ref("node"))}),
        "tagged_block": node("tagged_block", {"tag": ref("scalar"), "block": ref("block")}),
        "conditional": node("conditional", {"parameter": TEXT, "negated": BOOL,
                                             "items": array(ref("node"))}),
        "assignment": node("assignment", {"key": ref("scalar"), "operator": TEXT,
            "value": union(*(ref(kind) for kind in ("scalar", "formula", "block", "tagged_block")))}),
        "logical_operation": node("logical_operation", {"operator": TEXT, "name": ref("scalar"),
                                                        "assignment_operator": TEXT, "body": ref("block")}),
    }
    # Conditional dispatch avoids exploring every recursive alternative on invalid data.
    dispatch = {"type": "object", "required": ["kind"],
                "properties": {"kind": {"enum": list(nodes)}},
                "allOf": [{"if": {"properties": {"kind": {"const": kind}}}, "then": ref(kind)}
                          for kind in nodes]}
    return {**nodes, "node": dispatch, "origin": inline.origin(), "document": obj({
        "source": obj({"root": {"const": "STELLARIS_ROOT"}, "file": inline.location()["properties"]["file"]}),
        "items": array(ref("node")), "metadata": obj({"inline_scripts": array(inline.call())})})}


def schema():
    result = obj({"format": {"const": "sttv.parse_database"}, "format_version": {"const": 1},
                  "documents": array(ref("document"), minItems=1)})
    result["$defs"] = definitions()
    return result
