"""Contracts for prepared acquisition evidence and configurable semantic groups."""

from .helpers import TEXT, HASH, BOOL, RELATIVE, array, obj, mapping
from .configuration import selection

COUNT = {'type': 'integer', 'minimum': 0}
DIAGNOSTICS = array({'type': 'object'})


def sources():
    return obj({'format_version': {'const': 1}, 'context': {'const': 'playable_empire'},
        'roots': array(RELATIVE, minItems=1, uniqueItems=True), 'pattern': TEXT, 'encoding': TEXT,
        'non_executable_sources': mapping(obj({'sha256': HASH, 'reason': TEXT})),
        'directory': RELATIVE, 'effects': selection(), 'entries': selection()})


def effects():
    return obj({'commands': mapping(obj({'handler': {'enum': ['grant', 'option', 'progress', 'random', 'copy_random', 'copy_all']},
        'target': TEXT, 'scalar': BOOL, 'basis': TEXT})), 'activation': TEXT,
        **{key: array(TEXT, uniqueItems=True) for key in
           ('event_calls', 'scopes', 'transparent', 'branches', 'random', 'safe_actions', 'domain_fields')},
        'failure_field': TEXT, 'limits': obj({'max_depth': {'type': 'integer', 'minimum': 1}})})


def entries():
    return obj({'definitions': array(obj({'directory': RELATIVE,
        'type': {'enum': ['perk', 'tradition', 'crisis_path', 'crisis_level', 'event', 'on_action']},
        'effects': array(TEXT), 'gates': array(TEXT)})),
        'condition_fields': array(TEXT), 'event_id': TEXT, 'event_triggered': TEXT,
        'event_lists': array(TEXT), 'crisis_levels': TEXT, 'crisis_predicate': TEXT})


def document():
    result = obj({'format': {'const': 'sttv.acquisition_document'}, 'format_version': {'const': 1},
        'source': RELATIVE, 'records': array(obj({'record_id': HASH, 'id': TEXT, 'type': TEXT,
            'source': RELATIVE, 'pointer': TEXT, 'node': {'type': 'object'}})),
        'targets': mapping(array(HASH)), 'calls': mapping(array(HASH)),
        'coverage': obj({'parsed': BOOL, 'commands_checked': COUNT, 'diagnostics': DIAGNOSTICS})})
    result['properties']['coverage']['properties']['classification'] = obj({'type': {'const': 'documentation'}, 'sha256': HASH, 'reason': TEXT})
    return result


def manifest():
    result = obj({'format_version': {'const': 1}, 'implementation': TEXT, 'context': TEXT,
        'revision': HASH, 'configuration_revision': HASH, 'membership_revision': HASH,
        'documents': array(obj({'source': RELATIVE, 'path': RELATIVE, 'file_hash': HASH, 'byte_size': COUNT,
            'coverage': document()['properties']['coverage']})),
        'targets': mapping(array(RELATIVE)), 'calls': mapping(array(RELATIVE)),
        'coverage': obj({'parsed': BOOL, 'diagnostics': DIAGNOSTICS}),
        'statistics': obj({'reused_documents': COUNT, 'parsed_documents': COUNT, 'bytes': COUNT,
                           'seconds': {'type': 'number', 'minimum': 0}},
                          ['reused_documents', 'parsed_documents', 'bytes'])})
    result['properties']['preparation_revision'] = HASH
    return result
