"""Structural node contracts; game field names are unrestricted strings."""

from .helpers import BOOL, HASH, NULL, STRING, TEXT, array, obj, ref, union
from . import inline, localization
from sttv.common.datasets import KINDS


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
            "value": union(*(ref(kind) for kind in ("scalar", "formula", "block", "tagged_block", "script_value")))}),
        "logical_operation": node("logical_operation", {"operator": TEXT, "name": ref("scalar"),
                                                        "assignment_operator": TEXT, "body": ref("block")}),
        'script_value': node('script_value', {'scope': union(TEXT, NULL), 'body': ref('block')}),
        'scripted_trigger_test': node('scripted_trigger_test', {'operator': TEXT,
                                       'value': union(ref('scalar'), ref('formula'), ref('script_value')), 'body': ref('block')}),
    }
    nodes["assignment"]["properties"]["enrichments"] = localization.enrichment()
    # Conditional dispatch avoids exploring every recursive alternative on invalid data.
    dispatch = {"type": "object", "required": ["kind"],
                "properties": {"kind": {"enum": list(nodes)}},
                "allOf": [{"if": {"properties": {"kind": {"const": kind}}}, "then": ref(kind)}
                          for kind in nodes]}
    return {**nodes, "node": dispatch, "origin": inline.origin(), "document": obj({
        "source": obj({"root": {"const": "STELLARIS_ROOT"}, "file": inline.location()["properties"]["file"]}),
        "items": array(ref("node")), "metadata": obj({"expansions": array(inline.call())})})}


def schema():
    result = obj({"format": {"const": "sttv.parse_database"}, "format_version": {"const": 6},
                  "documents": array(ref("document"), minItems=1)})
    result['properties']['dataset'] = obj({'kind': {'enum': list(KINDS)},
                                            'set_id': HASH})
    result["$defs"] = definitions()
    return result
