"""Coordinate existing-database enrichment, freshness and safe publication."""

from time import perf_counter

from sttv.common.errors import BuildError
from sttv.common.persistence import save_json
from sttv.common.schema import schema_operation
from sttv.common.timing import measure
from . import attachment, evidence, integrity, report as reporting, representations, revisions
from .inputs import technology_input
from sttv.storage import open_set
from sttv.storage.publication import Publication
from .publication import publish
from .selection import calculate
from .settings import load


def run(settings, report, recalculate, publication):
    times = report['timings']
    report['paths'] = {'manifest': str(settings.storage.manifest), 'report': str(settings.report),
                       'staging': str(settings.staging)}
    report['rules'] = settings.rules
    with measure(times, 'reading'):
        reader = open_set(settings.storage.manifest)
        documents, records, targets = technology_input(settings, reader)
        technologies = representations.prepare(records, settings.combination['variants'])
    report['combination'] = {'id': settings.combination['id'], **revisions.parameters(settings, technologies)}
    with measure(times, 'hashing'):
        inventory = [{'kind': kind, 'algorithm': 'sttv.dataset_sources.v1', 'hash': dataset['source_revision']}
                     for kind, dataset in reader.manifest['datasets'].items()]
        meta = revisions.metadata(settings, technologies, reader.manifest['set_id'], inventory)
    report['bytes']['technology_read'] = reader.bytes
    report['file_hashes'] = {'before': reader.manifest['snapshot_revision'], 'after': reader.manifest['snapshot_revision']}
    combo = settings.combination['id']
    try:
        old_meta, old_results = attachment.stored(reader.manifest, documents, targets, technologies, combo)
    except BuildError as exc:
        old_meta, old_results = None, {}
        report['diagnostics'].append({'code': 'stored_result_invalid', 'message': str(exc)})
    reusable = False
    if old_meta and old_meta.get('calculation_revision') == meta['calculation_revision']:
        try:
            with measure(times, 'validation'):
                integrity.check_results(old_results, technologies)
                integrity.check_metadata(old_meta, old_results)
            reusable = True
        except (BuildError, KeyError, TypeError) as exc:
            report['diagnostics'].append({'code': 'stored_result_invalid', 'message': str(exc)})
    if reusable and not recalculate:
        results, meta = old_results, old_meta
        report['decisions'] = reporting.reused_decisions(technologies, results)
        report['action'] = 'reused'
    else:
        with measure(times, 'indexes'):
            prepared = evidence.load(settings, technologies, reader)
        report['bytes']['index_read'] = reader.bytes - report['bytes']['technology_read']
        with measure(times, 'criteria'):
            results, decisions, diagnostics = calculate(technologies, prepared, settings.rules, settings.facts)
        report['decisions'] = decisions
        report['diagnostics'].extend(diagnostics)
        report['action'] = 'computed'
        meta['result_revision'] = revisions.result_revision(meta, results)
    with measure(times, 'validation'):
        integrity.check_results(results, technologies)
        integrity.check_metadata(meta, results)
        settings.check_snapshot()
        reader.check_snapshot()
    report['revisions'] = meta
    if not reusable or meta != old_meta or results != old_results:
        with measure(times, 'attachment'):
            changed = attachment.attach(documents, targets, technologies, combo, results)
        with measure(times, 'writing'):
            manifest = publish(reader, documents, changed, combo, meta, settings, publication)
        report['database_written'] = publication.published
        report['bytes']['written'] = publication.written_bytes
        report['counts']['written_documents'] = len(changed)
        report['file_hashes']['after'] = manifest['snapshot_revision']
    else:
        report['bytes']['written'] = 0
        report['counts']['written_documents'] = 0
    report['counts']['unchanged_documents'] = len(documents) - report['counts']['written_documents']
    report['coverage'] = reader.coverage()
    report['bytes']['read_and_hashed'] = reader.bytes
    report['bytes']['hashing_extra_read'] = 0
    report['bytes']['events_read'] = sum(reader.descriptors[key]['byte_size']
        for key in reader.verified if key[0] == 'events')
    reporting.summarize(report, results, technologies)


@schema_operation
def execute(variables_path=None, config_path=None, combination_path=None, *, recalculate=False):
    report, settings, start = reporting.initial(), None, perf_counter()
    try:
        with measure(report['timings'], 'configuration'):
            settings = load(variables_path, config_path, combination_path)
        with Publication(settings.storage) as publication:
            from sttv.parallel.memory import Monitor
            memory = Monitor(publication.directory)
            try:
                run(settings, report, recalculate, publication)
            finally:
                memory.close()
                report['memory'] = memory.data
    except (BuildError, OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        report['status'] = 'failed'
        report['error'] = {'code': getattr(exc, 'code', 'operation_error'), 'message': str(exc),
                           'details': getattr(exc, 'context', {})}
    report['timings']['total'] = perf_counter() - start
    if settings is not None:
        try:
            save_json(settings.report, report, 'technology_tree_report.schema.json')
        except (BuildError, OSError, ValueError) as exc:
            report['status'] = 'failed'
            report['diagnostics'].append({'code': 'report_write_error', 'message': str(exc)})
            if report['error'] is None:
                report['error'] = {'code': 'report_write_error', 'message': str(exc)}
    return report
