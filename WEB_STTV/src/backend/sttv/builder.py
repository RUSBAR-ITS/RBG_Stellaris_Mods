"""Coordinate parallel document preparation and standalone publication."""

from contextlib import ExitStack

from sttv.common.report import Report
from sttv.common.schema import schema_operation
from sttv.common.timing import measure
from sttv.sources.settings import check_sources, load_settings
from sttv.sources.verification import verify_inputs
from sttv.common.persistence import save_json
from sttv.common.paths import selected_path
from sttv.storage.settings import load as load_storage
from sttv.storage.publication import Publication
from sttv.storage.manifest import create
from sttv.common.datasets import KINDS
from sttv.libraries.operation import library_operation, require_mode
from sttv.parallel.pool import Pool


@schema_operation
def build(variables_path, config_path, *, library_mode=None):
    report, settings, stage = Report(), None, 'configuration'
    metrics = report.data['performance']
    lifetime = ExitStack()
    try:
        require_mode(library_mode)
        with measure(metrics['timings'], 'prepare_sources'):
            settings = load_settings(variables_path, config_path)
            check_sources(settings)
            storage = load_storage(variables_path, selected_path(settings.options['storage'], settings.work))
            publication = lifetime.enter_context(Publication(storage))
            snapshot = lifetime.enter_context(library_operation(settings, library_mode))
            pool = lifetime.enter_context(Pool(settings, snapshot))
        stage = 'parsing'
        results = pool.build('technologies', settings, report)
        members = {kind: [] for kind in KINDS}
        members['technologies'] = [publication.accept(r['fragment'], 'technologies') for r in results]
        pool.__exit__(None, None, None)
        stage = 'source_verification'
        def verify():
            with measure(metrics['timings'], 'verify_inputs'):
                verify_inputs(settings, report)
                snapshot.inventory.verify()
        stage = 'storage'
        publication.publish(create(members), verify)
        report.data.update(status='success', database_written=True)
    except Exception as exc:
        report.data['status'] = 'failed'
        report.failure(exc, stage)
    finally:
        try:
            lifetime.close()
        except Exception as exc:
            report.data['status'] = 'failed'
            report.failure(exc, 'library_report')
    if settings is not None:
        try:
            save_json(settings.report, report.data, 'report.schema.json')
        except Exception as exc:
            report.data['status'] = 'failed'
            report.failure(exc, 'report')
    return report.data
