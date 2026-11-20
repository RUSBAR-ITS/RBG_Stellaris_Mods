"""Configuration and publication report for a localized database set."""

from .configuration import schema as build_schema, selection
from .helpers import BOOL, HASH, NULL, RELATIVE, TEXT, array, obj, union
from . import reports, localization_report, performance
from sttv.common.datasets import KINDS


def registry():
    from .helpers import mapping
    fields = {
        'labelId': TEXT, 'directory': RELATIVE, 'recursive': BOOL, 'rootTypes': array(TEXT, uniqueItems=True),
        'identity': {'enum': ['key', 'field', 'anonymous', 'fragments']}, 'idField': union(TEXT, NULL)
    }
    optional = {'containers': array(TEXT),
        'sourceRoles': array(obj({'role': {'enum': ['objects', 'descriptor']}, 'pattern': TEXT})),
        'descriptorLink': obj({'matchField': TEXT, 'localizationField': TEXT})}
    return obj({'format_version': {'const': 2}, 'datasets': mapping(obj({**fields, **optional}, list(fields)),
        {'type': 'string', 'pattern': '^[a-z][a-z_]*$'})})


def configuration():
    build = build_schema()['properties']
    dataset = obj({'sources': build['sources'], 'outputs': obj({
        key: RELATIVE for key in ('report', 'localization_report')})})
    result = obj({'parser': build['parser'], 'libraries': selection(), 'parallel': selection(), 'datasets': obj({kind: dataset for kind in KINDS}),
                'storage': selection(), 'localization': selection(), 'report': RELATIVE})
    result['properties']['assets'] = selection()
    result['properties']['acquisition'] = selection()
    return result


def report():
    status = {'enum': ['not_started', 'success', 'failed']}
    member = obj({'database': TEXT, 'build_report': TEXT, 'localization_report': TEXT,
                  'prepared': BOOL, 'written': BOOL, 'content_hash': union(HASH, NULL),
                  'bytes': {'type': 'integer', 'minimum': 0}, 'seconds': {'type': 'number', 'minimum': 0},
                  'build_status': status, 'localization_status': status, 'performance': performance.schema(),
                  'build_counts': reports.schema()['properties']['counts'],
                  'localization_counts': localization_report.schema()['properties']['counts']})
    result = obj({'format': {'const': 'sttv.database_set_report'}, 'format_version': {'const': 1},
                'status': {'enum': ['running', 'success', 'failed']}, 'set_id': union(HASH, NULL),
                'snapshot_revision': union(HASH, NULL), 'published': BOOL,
                'datasets': obj({kind: member for kind in KINDS}, required=[]),
                'diagnostics': array(obj({'code': TEXT, 'stage': TEXT, 'message': TEXT,
                    'dataset': union({'enum': list(KINDS)}, NULL), 'node': union(TEXT, NULL)})),
                'inputs': array(obj({'path': TEXT, 'sha256': HASH, 'kind': TEXT})),
                'seconds': {'type': 'number', 'minimum': 0}, 'performance': performance.schema()})
    from .assets import report as assets_report
    properties = assets_report()['properties']
    result['properties']['assets'] = obj({key: properties[key] for key in ('status', 'counts', 'timings', 'diagnostics')})
    return result
