"""Explicit full-set verification, independent of source parsing."""

from time import perf_counter
from .reader import open_set


def audit(manifest_path):
    start, reader = perf_counter(), None
    report = {'format': 'sttv.storage_report', 'format_version': 1, 'status': 'failed',
              'manifest': str(manifest_path), 'snapshot_revision': None, 'coverage': {},
              'timings': {}, 'diagnostics': [], 'published': False}
    try:
        reader = open_set(manifest_path)
        report['snapshot_revision'] = reader.manifest['snapshot_revision']
        for kind, identifier in reader.paths:
            reader.project(kind, identifier)
        reader.check_snapshot()
        report['status'] = 'success'
    except Exception as exc:
        report['diagnostics'].append({'code': getattr(exc, 'code', 'audit_failed'), 'message': str(exc),
            'snapshot_revision': report['snapshot_revision'], 'details': getattr(exc, 'context', {})})
    if reader:
        report['coverage'] = reader.coverage()
    report['timings']['total'] = perf_counter() - start
    return report
