"""Prepare one localized member through the operation's persistent file pool."""

from sttv.common.timing import measure
from sttv.enrichment.localization.settings import load_settings
from sttv.enrichment.localization.snapshot import Snapshot
from sttv.sources.settings import check_sources
from sttv.common.datasets import definition


def prepare_member(kind, settings, variables, localization, outputs, build_report, loc_report, inputs, publication, pool):
    metrics = build_report.data['performance']
    with measure(metrics['timings'], 'prepare_sources'):
        check_sources(settings)
        snapshot = Snapshot(loc_report)
        local = load_settings(variables, localization, snapshot, kind,
            settings.database.relative_to(settings.work).as_posix(), outputs['localization_report'])
        loc_report['settings'] = local.options
        loc_report['paths'] = {'database': str(local.database), 'report': str(local.report)}
    linked = 'descriptorLink' in definition(kind)
    results = pool.build(kind, settings, build_report, None if linked else local, loc_report)
    if linked:
        from .descriptors import prepare
        build_report.data['counts']['catalog'] = prepare(kind, results, local, build_report, loc_report)
    else:
        inventory = {'objects': sum(len(row['fragment']['objects']) for row in results)}
        if kind == 'civics':
            from sttv.common.json_io import read_json
            from sttv.common.object_selection import selected_nodes
            inventory['origins'] = 0
            for result in results:
                document = read_json(result['fragment']['path'])
                inventory['origins'] += sum(any(child['kind'] == 'assignment' and child['key']['text'] == 'is_origin'
                    and child['value'].get('text', '').casefold() == 'yes' for child in node['value']['items'])
                    for _, node in selected_nodes(kind, document['items'], document['source']))
        build_report.data['counts']['catalog'] = inventory
    with measure(metrics['timings'], 'store_documents'):
        members = [publication.accept(row['fragment'], kind) for row in results]
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
    return members
