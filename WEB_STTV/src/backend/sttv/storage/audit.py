"""Explicit full-set verification, independent of source parsing."""

from time import perf_counter
from .reader import open_set


def audit(manifest_path):
    start, reader = perf_counter(), None
    report = {'format': 'sttv.storage_report', 'format_version': 1, 'status': 'failed',
              'manifest': str(manifest_path), 'snapshot_revision': None, 'coverage': {},
              'timings': {}, 'diagnostics': [], 'published': False}
    verified_images = 0
    try:
        reader = open_set(manifest_path)
        report['snapshot_revision'] = reader.manifest['snapshot_revision']
        from .assets import verify_asset, verify_references
        presentation = reader.manifest.get('presentation', {})
        from sttv.common.datasets import definition
        linked = {}
        for kind, identifier in reader.paths:
            if 'descriptorLink' in definition(kind):
                linked.setdefault(kind, []).append(reader.read_document(kind, identifier))
                continue
            extract = (lambda pointer, node: verify_references(node, presentation)) if kind == 'technologies' and presentation else None
            reader.project(kind, identifier, extract)
        from sttv.database_sets.descriptors import verify
        for kind, documents in linked.items():
            verify(kind, documents)
        images = presentation.get('files', {})
        for row in images.values():
            verify_asset(reader.root, row)
            verified_images += 1
        from sttv.enrichment.acquisition.storage import Index
        acquisition = reader.manifest['acquisition']
        index = Index(reader, {'revision': acquisition['configuration_revision']})
        for path in index.descriptors:
            index.document(path)
        reader.check_snapshot()
        report['status'] = 'success'
    except Exception as exc:
        report['diagnostics'].append({'code': getattr(exc, 'code', 'audit_failed'), 'message': str(exc),
            'snapshot_revision': report['snapshot_revision'], 'details': getattr(exc, 'context', {})})
    if reader:
        report['coverage'] = reader.coverage()
        report['coverage']['images'] = {'declared': len(reader.manifest.get('presentation', {}).get('files', {})),
                                        'verified': verified_images}
    report['timings']['total'] = perf_counter() - start
    return report
