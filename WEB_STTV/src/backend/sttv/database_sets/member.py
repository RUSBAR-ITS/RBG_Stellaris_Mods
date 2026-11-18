"""Prepare one localized member through the operation's persistent file pool."""

from sttv.common.timing import measure
from sttv.enrichment.localization.settings import load_settings
from sttv.enrichment.localization.snapshot import Snapshot
from sttv.sources.settings import check_sources


def prepare_member(kind, settings, variables, localization, outputs, build_report, loc_report, inputs, staging, pool):
    metrics = build_report.data['performance']
    with measure(metrics['timings'], 'prepare_sources'):
        check_sources(settings)
        snapshot = Snapshot(loc_report)
        local = load_settings(variables, localization, snapshot, kind, outputs['database'], outputs['localization_report'])
        loc_report['settings'] = local.options
        loc_report['paths'] = {'database': str(local.database), 'report': str(local.report)}
    path, checksum, results = pool.build(kind, settings, build_report, local, loc_report)
    staging.paths[kind] = path
    inputs.capture_build(settings, build_report)
    inputs.observe(loc_report['inputs'])
    seen = set()
    for result in results:
        for directory, reading, paths in result['localization_files']:
            identity = (directory, tuple(sorted(reading.items())), tuple(paths))
            if identity not in seen:
                seen.add(identity)
                inputs.localizations.append((directory, reading, paths))
    build_report.data['status'], loc_report['status'] = 'success', 'success'
    return checksum
