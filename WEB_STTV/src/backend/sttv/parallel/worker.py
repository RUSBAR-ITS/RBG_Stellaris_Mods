"""Spawn-safe worker initialization and independent document jobs."""

from copy import deepcopy
import os
from pathlib import Path
from time import perf_counter

from sttv.common.report import Report
from sttv.common.schema import SchemaSession, _session
from sttv.common.timing import measure
from sttv.common.errors import BuildError
from sttv.common.datasets import definition
from sttv.database.collection import read_document
from sttv.storage.writing import write_document
from sttv.database.validation import database_rules
from sttv.libraries.operation import ACTIVE
from sttv.libraries.storage import load
from sttv.script.metrics import ACTIVE as METRICS, Metrics
from sttv.script.serialization import encode
from sttv.sources.expansion import expansion_context
from sttv.enrichment.localization.report import new_report
from .localization import Localizations
from .ordering import offsets

STATE = None


def initialize(settings, inventory, library_id, requests, responses, ranks):
    global STATE
    start = perf_counter()
    _session.set(SchemaSession())
    report = {'bytes': 0, 'counts': {}, 'timings': {}}
    STATE = {'snapshot': None, 'error': None, 'localizations': Localizations(), 'initialization': None}
    with ranks.get_lock():
        rank = ranks.value
        ranks.value += 1
    STATE['transport'] = requests, responses[rank], rank
    rules_seconds = 0.0
    try:
        with measure(report['timings'], 'load'):
            snapshot = load(settings, inventory, report)
        if report['library_set_id'] != library_id:
            raise BuildError('library_inputs_changed', 'Worker loaded a different library snapshot')
        ACTIVE.set(snapshot)
        STATE['snapshot'] = snapshot
        rules_seconds = database_rules().seconds
    except Exception as exc:
        STATE['error'] = (getattr(exc, 'code', 'worker_initialization'), str(exc))
    STATE['initialization'] = {'pid': os.getpid(), 'seconds': perf_counter() - start,
        'rule_seconds': rules_seconds, 'bytes': report['bytes'],
        'counts': report['counts'], 'timings': report['timings']}


def execute(job):
    start = perf_counter()
    report, local = Report(), new_report()
    result = {'index': job['index'], 'source': job['source'], 'pid': os.getpid(),
              'status': 'failed', 'fragment': None, 'identities': {}, 'localization': local,
              'localization_files': [], 'report': report.data, 'seed': None,
              'library': {'counts': {}, 'timings': {}}, 'initialization': STATE['initialization']}
    STATE['initialization'] = None
    metrics = Metrics(result['library'])
    metrics.phase = 'apply'
    token = METRICS.set(metrics)
    stage = 'initialization'
    assigned, requested = {}, False
    try:
        if STATE['error']:
            raise BuildError(*STATE['error'])
        settings = job['settings']
        snapshot = STATE['snapshot']
        snapshot.report = result['library']
        variables = snapshot.variables(settings, report)
        result['seed'] = deepcopy(report.data)
        expansion = expansion_context(settings, report, variables)
        def assign_identifiers():
            nonlocal requested
            requested = True
            assigned.update(offsets(job, expansion, result['seed'], STATE['transport'],
                                    report.data['performance']['timings']))
            return assigned
        stage = 'parsing'
        document = read_document(settings, report, variables, expansion,
            Path(job['path']), job['encoding'], before_serialization=assign_identifiers)
        if document is None:
            if not requested:
                assign_identifiers()
            return result
        if job['local'] is not None:
            stage = 'localization'
            with measure(report.data['performance']['timings'], 'localization'):
                result['localization_files'] = STATE['localizations'].apply(
                    document, job['local'], job['index'], local, result['identities'],
                    report.data['performance']['timings'])
        if job.get('acquisition'):
            from sttv.enrichment.acquisition.extraction import extract
            from sttv.enrichment.acquisition.preparation import store
            result['acquisition'] = store(extract(document, job['acquisition']), job['output'] + '.acquisition.json')
        stage = 'validation_storage'
        result['fragment'] = write_document(document, Path(job['output']), job['kind'], report.data['performance'],
            validate='descriptorLink' not in definition(job['kind']))
        report.data['counts']['nodes'] += result['fragment']['nodes']
        result['status'] = 'success'
    except Exception as exc:
        if getattr(exc, 'code', None) == 'parallel_cancelled':
            result['status'] = 'failed' if report.failed else 'cancelled'
        else:
            report.failure(exc, stage, source='STELLARIS_ROOT', file=job['source'])
    finally:
        result['report'] = encode(report.data, assigned)
        result['seconds'] = perf_counter() - start
        METRICS.reset(token)
    return result
