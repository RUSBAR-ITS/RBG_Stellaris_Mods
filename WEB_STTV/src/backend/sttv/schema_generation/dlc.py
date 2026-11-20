"""DLC partial-evaluation settings and persisted profile contracts."""

from .helpers import BOOL, HASH, TEXT, LINE, array, obj, mapping
from .configuration import selection
from sttv.common.datasets import KINDS

PROFILE = obj({'known': array(TEXT, uniqueItems=True), 'enabled': array(TEXT, uniqueItems=True),
               'catalog_revision': HASH})
VISIBILITY = obj({'visible': BOOL, 'reasons': array(obj({'code': TEXT, 'pointer': TEXT})),
                  'evidence': array({'type': 'object'})})


def configuration():
    result = obj({'format': {'const': 'sttv.dlc_rules'}, 'format_version': {'const': 2},
        'predicates': array(TEXT, uniqueItems=True, minItems=1), 'constants': mapping(mapping(BOOL)),
        'wrappers': array(TEXT, uniqueItems=True), 'ignored_wrapper_fields': array(TEXT, uniqueItems=True),
        **{key: TEXT for key in ('potential_field', 'weight_field', 'modifier_field', 'factor_field')},
        'unsupported_actions': array(TEXT, uniqueItems=True),
        'catalog': obj({'database': {'const': 'dlcs'}, 'name_field': TEXT}),
        'context': {'const': 'playable_empire'}, 'groups': array(selection(), minItems=1),
        'required_datasets': array({'enum': list(KINDS)}, uniqueItems=True),
        'limits': obj({key: LINE for key in ('max_depth', 'max_nodes', 'max_steps')}),
        'government_requirements': mapping(TEXT),
        'scopes': mapping(obj({'from': array(TEXT, minItems=1), 'to': TEXT}))})
    result['properties']['rules'] = array(rule())
    result['properties']['acquisition'] = {'type': 'object'}
    return result


def rule():
    result = obj({'id': TEXT, 'enabled': BOOL, 'predicates': array(TEXT, uniqueItems=True),
        'handler': {'enum': ['object', 'ship_category', 'tradition', 'observe', 'technology']},
        'database': {'enum': list(KINDS)}, 'contexts': array(TEXT, minItems=1, uniqueItems=True),
        'purpose': {'enum': ['selection', 'acquisition', 'observation']},
        'gates': array(obj({'field': TEXT, 'context': {'enum': ['country', 'government', 'species']}})),
        'source': TEXT, 'diagnostic_code': TEXT})
    result['properties'].update(selector=obj({'field': TEXT, 'value': TEXT, 'default': TEXT}),
        providers=obj({'rule': TEXT, 'fields': array(TEXT, minItems=1, uniqueItems=True)}))
    return result


def group():
    return obj({'rules': array(rule(), minItems=1)})
