"""Coordinate parallel document preparation and standalone publication."""

from contextlib import ExitStack

from sttv.common.report import Report
from sttv.common.schema import schema_operation
from sttv.common.timing import measure
from sttv.sources.settings import check_sources, load_settings
from sttv.sources.verification import verify_inputs
from sttv.database.storage import publish, write_report
from sttv.libraries.operation import library_operation, require_mode
from sttv.parallel.pool import Pool


@schema_operation
def build(variables_path, config_path, *, library_mode=None):
    report, settings, stage, temporary = Report(), None, 'configuration', None
    metrics = report.data['performance']
    lifetime = ExitStack()
    try:
        require_mode(library_mode)
        with measure(metrics['timings'], 'prepare_sources'):
            settings = load_settings(variables_path, config_path)
            check_sources(settings)
            snapshot = lifetime.enter_context(library_operation(settings, library_mode))
            pool = lifetime.enter_context(Pool(settings, snapshot))
        stage = 'parsing'
        temporary, _, _ = pool.build('standalone', settings, report)
        pool.__exit__(None, None, None)
        stage = 'source_verification'
        with measure(metrics['timings'], 'verify_inputs'):
            verify_inputs(settings, report)
            snapshot.inventory.verify()
        lifetime.close()
        stage = 'storage'
        publish(settings, temporary, report)
    except Exception as exc:
        report.data['status'] = 'failed'
        report.failure(exc, stage)
    finally:
        try:
            lifetime.close()
        except Exception as exc:
            report.failure(exc, 'library_report')
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    if report.failed and settings is not None:
        try:
            write_report(settings, report)
        except Exception as exc:
            report.failure(exc, 'report')
    return report.data
