"""Closed configuration and reporting for approved in-memory corrections."""

from .helpers import NULL, STRING, TEXT, obj, union
from . import inline


def application():
    return obj({'rule_id': TEXT, 'root_source': {'$ref': '#/$defs/origin'},
                'provenance': {'$ref': '#/$defs/origin'}, 'call_chain': inline.chain(),
                'before': union(STRING, NULL), 'after': STRING, 'value_source': TEXT})
