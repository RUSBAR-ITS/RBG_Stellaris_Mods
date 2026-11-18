"""Configuration and persisted text contracts for localization enrichment."""

from .helpers import BOOL, LINE, NULL, RELATIVE, STRING, TEXT, array, obj, union
from .configuration import selection
from sttv.common.datasets import KINDS


def target():
    keys = {"variant": union(TEXT, NULL), "name": TEXT, "description_suffix": union(TEXT, NULL),
            'description_field': union(TEXT, NULL), 'text_field': TEXT, 'fallback_field': union(TEXT, NULL)}
    optional = {'name_prefix': STRING, 'name_field': TEXT, 'omit_name': BOOL, 'description_nodes': BOOL,
                'description_excluded': array(TEXT), 'endpoint_fields': array(TEXT), 'endpoint_description_suffix': TEXT,
                'child_text_fields': array(obj({'field': TEXT, 'role': {'enum': ['name', 'description']}}))}
    return obj({
        "selection": obj({"variable": TEXT, "pattern": TEXT, "recursive": BOOL}),
        "keys": obj({**keys, **optional}, required=list(keys)),
    })


def configuration():
    language = obj({"header": TEXT, "sources": array(TEXT, minItems=1, uniqueItems=True)})
    result = obj({
        "format_version": {"const": 3},
        'targets': obj({kind: selection() for kind in KINDS}),
        "languages": obj({key: language for key in ("ru", "en")}),
        "reading": obj({"pattern": TEXT, "recursive": BOOL, "encoding": TEXT}),
        "references": obj({"delimiter": {"type": "string", "minLength": 1, "maxLength": 1},
                           "key_pattern": TEXT, "max_depth": LINE, "max_characters": LINE}),
        "inherit_description": BOOL,
    })
    result['properties'].update(database=RELATIVE, report=RELATIVE)
    return result


def source():
    return obj({"tier": TEXT, "file": {**RELATIVE, "pattern": r"^(?![A-Za-z]:)(?!/)(?!.*\\)(?!.*(?:^|/)\.\.(?:/|$)).+$"},
                "line": LINE})


def field():
    result = obj({"requested_key": TEXT, "key": union(TEXT, NULL),
                "raw": union(STRING, NULL), "text": union(STRING, NULL),
                "source": union(source(), NULL),
                "inherited_from": union({"type": "string", "pattern": r"^/documents/\d+/items/\d+$"}, NULL),
                "unresolved_references": array(TEXT, uniqueItems=True)})
    result['properties']['fallback'] = obj({'kind': {'const': 'component_set'},
                                            'source_ref': TEXT})
    return result


def enrichment():
    language = obj({"name": field(), "description": field()}, required=[])
    language['minProperties'] = 1
    return obj({"localization": obj({key: language for key in ("ru", "en")})}, required=[])
