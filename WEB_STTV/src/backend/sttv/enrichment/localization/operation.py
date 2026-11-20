"""Refresh localized documents through an atomic manifest publication."""

from copy import deepcopy
from pathlib import Path
from time import perf_counter

from sttv.common.paths import PRODUCT_ROOT, selected_path
from sttv.common.schema import schema_operation
from sttv.common.persistence import save_json
from sttv.common.timing import performance
from sttv.storage import open_set
from sttv.storage.identity import source_hash
from sttv.storage.manifest import finalize
from sttv.storage.publication import Publication
from sttv.storage.settings import load
from sttv.storage.writing import prepare, write_document
from sttv.storage.references import diagnostics
from .attachment import attach
from .index import LocalizationIndex
from .references import Resolver
from .report import failed, failure, new_report
from .selection import select_targets
from .settings import load_settings
from .snapshot import Snapshot
from sttv.common.datasets import definition


def refresh(settings, snapshot, report, storage, kind):
    with Publication(storage) as publication:
        reader = open_set(storage.manifest)
        manifest = deepcopy(reader.manifest)
        report['database_before'] = manifest['snapshot_revision']
        index = LocalizationIndex(settings, snapshot, report)
        resolver = Resolver(index, settings.options['references'])
        identities = {}
        linked, descriptors = {}, {}
        if 'descriptorLink' in definition(kind):
            from sttv.database_sets.descriptors import relationships
            linked = {doc['document_id']: doc for doc in reader.iter_documents(kind)}
            _, descriptors, _ = relationships(kind, linked.values())
        for position, descriptor in enumerate(manifest['datasets'][kind]['documents']):
            document = linked.get(descriptor['document_id']) if linked else reader.read_document(kind, descriptor['document_id'])
            envelope = {'documents': [document]}
            targets = select_targets(envelope, settings, report['counts'], identities=identities)
            if linked:
                from sttv.database_sets.descriptors import decorate_targets
                decorate_targets(kind, targets, descriptors)
            diagnostic_start = len(report['diagnostics'])
            attach(envelope, targets, settings, resolver, report)
            diagnostics(report, kind, descriptor['document_id'], diagnostic_start)
            document = prepare(document, kind)
            if source_hash(document) == descriptor['source_hash']:
                continue
            fragment = write_document(document, publication.directory / f'{position}.json', kind, performance())
            row = publication.accept(fragment, kind)
            manifest['datasets'][kind]['documents'][position] = row['descriptor']
        report['selected_sources'] = [index.selected[key] for key in sorted(index.selected)]
        if failed(report):
            return
        finalize(manifest)
        def verify():
            snapshot.verify()
            index.verify_files()
            reader.check_snapshot()
        report['database_written'] = publication.publish(manifest, verify)
        report['database_after'] = manifest['snapshot_revision']


@schema_operation
def enrich_localization(variables_path=None, config_path=None, *, kind='technologies'):
    variables_path = Path(variables_path or PRODUCT_ROOT / 'global_variables.json')
    config_path = Path(config_path or PRODUCT_ROOT / 'config/enrichment/localization.json')
    start, report, settings = perf_counter(), new_report(), None
    snapshot, stage = Snapshot(report), 'configuration'
    try:
        settings = load_settings(variables_path, config_path, snapshot, kind)
        report['paths'] = {'database': str(settings.database), 'report': str(settings.report)}
        report['settings'] = settings.options
        storage = load(variables_path, selected_path(settings.options['storage'], settings.work))
        stage = 'enrichment'
        refresh(settings, snapshot, report, storage, kind)
    except Exception as exc:
        failure(report, exc, stage)
    report['status'] = 'failed' if failed(report) else 'success'
    report['seconds'] = round(perf_counter() - start, 3)
    if settings is not None:
        try:
            save_json(settings.report, report, 'localization_report.schema.json')
        except Exception as exc:
            report['status'] = 'failed'
            failure(report, exc, 'report')
    return report
