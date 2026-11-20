"""Technology tree configuration and optional persisted enrichment contracts."""

from .helpers import BOOL, HASH, NULL, TEXT, RELATIVE, array, obj, mapping, union
from .configuration import selection
from .dlc import PROFILE, VISIBILITY, configuration as dlc_rules

ID = {'type': 'string', 'pattern': '^[a-z][a-z0-9_]*$'}
VARIANT = {'type': 'string', 'pattern': r'^(base|swap:[1-9][0-9]*)$'}
FACTS = mapping(mapping(mapping(BOOL)))
RESULT = obj({'parent_tech': union(TEXT, NULL), 'children': array(TEXT, uniqueItems=True),
              'status': {'enum': ['root', 'resolved', 'ambiguous']}})
RESULT['properties']['visibility'] = VISIBILITY


def configuration():
    return obj({'format': {'const': 'sttv.technology_tree_config'}, 'format_version': {'const': 1},
        **{key: selection() for key in ('storage', 'dataset_registry', 'technology_targets', 'rules', 'combination', 'dlc_rules')},
        'report': RELATIVE, 'staging_directory': RELATIVE})


def profile():
    return obj({'format': {'const': 'sttv.technology_tree_profile'}, 'format_version': {'const': 1},
                'id': ID, 'facts': FACTS})


def combination():
    result = obj({'format': {'const': 'sttv.technology_tree_combination'}, 'format_version': {'const': 1},
                'id': ID, 'mode': {'const': 'reference'}, 'profile': selection(), 'variants': mapping(VARIANT)})
    result['properties']['dlc'] = obj({'enabled': array(TEXT, uniqueItems=True)})
    return result


def metadata():
    from .technology_tree_rules import schema
    entry = obj({'mode': {'const': 'reference'},
        'parameters': obj({'mode': {'const': 'reference'}, 'profile': FACTS, 'variants': mapping(VARIANT)}),
        'source_set_id': HASH,
        'inputs': array(obj({'kind': TEXT, 'algorithm': {'const': 'sttv.dataset_sources.v1'}, 'hash': HASH})),
        'rules_snapshot': schema(), 'implementation_revision': TEXT,
        **{key: HASH for key in ('input_revision', 'rules_revision', 'parameters_revision',
                                'calculation_revision', 'result_revision')}})
    entry['properties']['parameters']['properties']['dlc'] = PROFILE
    entry['properties']['dlc_rules_snapshot'] = dlc_rules()
    return obj({'format_version': {'const': 1}, 'combinations': mapping(entry, ID)})


def report():
    # Evidence contains structural excerpts, not an unrestricted executable contract.
    detail = {'type': 'object'}
    result = obj({'format': {'const': 'sttv.technology_tree_report'}, 'format_version': {'const': 1},
        'status': {'enum': ['success', 'success_with_warnings', 'failed']},
        'action': {'enum': ['reused', 'computed', None]}, 'database_written': BOOL,
        'paths': mapping(TEXT), 'combination': union(detail, NULL), 'rules': union(detail, NULL),
        'revisions': detail, 'counts': mapping({'type': 'integer', 'minimum': 0}),
        'timings': mapping({'type': 'number', 'minimum': 0}),
        'bytes': mapping({'type': 'integer', 'minimum': 0}), 'coverage': detail, 'decisions': array(detail),
        'diagnostics': array(detail), 'ambiguities': array(detail), 'file_hashes': detail,
        'error': union(obj({'code': TEXT, 'message': TEXT, 'details': detail}, required=['code', 'message']), NULL)})
    result['properties']['memory'] = detail
    result['properties']['dlc_analysis'] = detail
    return result
