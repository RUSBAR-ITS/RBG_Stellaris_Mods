"""Configuration and publication report for a localized database set."""

from .configuration import schema as build_schema, selection
from .helpers import BOOL, HASH, NULL, RELATIVE, TEXT, array, obj, union
from . import reports, localization_report, performance
from sttv.common.datasets import KINDS


def registry():
    from .helpers import mapping
    return obj({'format_version': {'const': 1}, 'datasets': mapping(obj({
        'labelId': TEXT, 'directory': RELATIVE, 'recursive': BOOL, 'rootTypes': array(TEXT, uniqueItems=True),
        'identity': {'enum': ['key', 'field', 'anonymous', 'fragments']}, 'idField': union(TEXT, NULL)
    }), {'type': 'string', 'pattern': '^[a-z][a-z_]*$'})})


def configuration():
    build = build_schema()['properties']
    dataset = obj({'sources': build['sources'], 'outputs': obj({
        key: RELATIVE for key in ('database', 'report', 'localization_report')})})
    return obj({'parser': build['parser'], 'libraries': selection(), 'parallel': selection(), 'datasets': obj({kind: dataset for kind in KINDS}),
                'localization': selection(), 'report': RELATIVE})


def report():
    status = {'enum': ['not_started', 'success', 'failed']}
    member = obj({'database': TEXT, 'build_report': TEXT, 'localization_report': TEXT,
                  'prepared': BOOL, 'written': BOOL, 'content_hash': union(HASH, NULL),
                  'bytes': {'type': 'integer', 'minimum': 0}, 'seconds': {'type': 'number', 'minimum': 0},
                  'build_status': status, 'localization_status': status, 'performance': performance.schema(),
                  'build_counts': reports.schema()['properties']['counts'],
                  'localization_counts': localization_report.schema()['properties']['counts']})
    return obj({'format': {'const': 'sttv.database_set_report'}, 'format_version': {'const': 1},
                'status': {'enum': ['running', 'success', 'failed']}, 'set_id': union(HASH, NULL),
                'datasets': obj({kind: member for kind in KINDS}, required=[]),
                'diagnostics': array(obj({'code': TEXT, 'stage': TEXT, 'message': TEXT,
                    'dataset': union({'enum': list(KINDS)}, NULL), 'node': union(TEXT, NULL)})),
                'inputs': array(obj({'path': TEXT, 'sha256': HASH, 'kind': TEXT})),
                'seconds': {'type': 'number', 'minimum': 0}, 'performance': performance.schema()})
