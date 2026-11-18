"""Explicit snapshot modes, operation ownership and one shared in-memory library."""

from contextlib import contextmanager
from contextvars import ContextVar

from sttv.common.errors import BuildError
from sttv.common.paths import output_path
from sttv.common.persistence import save_json
from sttv.common.timing import measure
from .inventory import Inventory, configuration, digest
from .snapshot import prepare_snapshot
from .storage import publish, load
from .ownership import ownership
from sttv.script.metrics import ACTIVE as METRICS, Metrics

ACTIVE = ContextVar('sttv_libraries', default=None)


def current(settings):
    snapshot = ACTIVE.get()
    if snapshot is None:
        raise BuildError('library_mode_required', 'Choose --rebuild-libraries or --reuse-libraries')
    if snapshot.inventory.configuration_hash != digest(configuration(settings)):
        raise BuildError('library_context', 'Prepared libraries belong to different settings')
    return snapshot


def require_mode(mode):
    if mode not in ('rebuild', 'reuse'):
        raise BuildError('library_mode_required', 'Choose --rebuild-libraries or --reuse-libraries')


@contextmanager
def library_operation(settings, mode):
    require_mode(mode)
    if ACTIVE.get() is not None:
        raise BuildError('library_context', 'Nested library operations are not supported')
    with ownership(settings):
        with prepared_operation(settings, mode) as snapshot:
            yield snapshot


@contextmanager
def prepared_operation(settings, mode):
    report = {'format': 'sttv.library_report', 'format_version': 1, 'mode': mode,
              'status': 'running', 'library_set_id': None, 'bytes': 0, 'diagnostics': [],
              'counts': {'prepared_plans': 0, 'loaded_artifacts': 0, 'contexts': 0}, 'timings': {}}
    token = None
    metrics = Metrics(report)
    metrics_token = METRICS.set(metrics)
    try:
        with measure(report['timings'], 'verify_inputs'):
            inventory = Inventory(settings, retain=mode == 'rebuild')
        report['counts']['source_reads'] = inventory.reads
        inventory.report = report
        if mode == 'rebuild':
            with measure(report['timings'], 'prepare'):
                snapshot = prepare_snapshot(settings, inventory, report)
            with measure(report['timings'], 'save'):
                publish(settings, snapshot)
        else:
            with measure(report['timings'], 'load'):
                snapshot = load(settings, inventory, report)
            inventory.verify()
        token = ACTIVE.set(snapshot)
        metrics.phase = 'apply'
        yield snapshot
        report['status'] = 'success'
    except BaseException as exc:
        report['status'] = 'failed'
        report['diagnostics'].append({'code': getattr(exc, 'code', 'library_error'), 'message': str(exc)})
        raise
    finally:
        if token is not None:
            ACTIVE.reset(token)
        METRICS.reset(metrics_token)
        save_json(output_path(settings.work, settings.libraries['report'], settings.protected),
                  report, 'library_report.schema.json')


def add_mode_arguments(parser):
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--rebuild-libraries', dest='library_mode', action='store_const', const='rebuild')
    group.add_argument('--reuse-libraries', dest='library_mode', action='store_const', const='reuse')
