"""One calculation writer, explicit cancellation and pinned result snapshots."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from contextlib import contextmanager
import secrets
from threading import Event, RLock

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.persistence import save_json
from sttv.storage.manifest import check
from sttv.enrichment.technology_tree.operation import execute


class Operations:
    def __init__(self, options, variables, config, settings):
        self.options, self.variables, self.config, self.settings = options, variables, config, settings
        self.lock, self.executor = RLock(), ThreadPoolExecutor(max_workers=1)
        self.sessions, self.jobs, self.snapshots = {}, {}, {}
        from sttv.enrichment.dlc.cache import AnalysisCache
        self.analysis_cache = AnalysisCache()

    def manifest(self):
        return check(read_json(self.settings.storage.manifest))

    def connect(self, payload):
        with self.lock:
            manifest = self.manifest()
            if (payload.get('setId'), payload.get('snapshotRevision')) != (manifest['set_id'], manifest['snapshot_revision']):
                raise BuildError('set_mismatch', 'Selected directory does not match the registered set snapshot')
            token = secrets.token_urlsafe(32)
            self.sessions[token] = manifest['set_id']
            self.snapshots[manifest['snapshot_revision']] = manifest
            self.trim(self.sessions)
            return {'token': token, 'setId': manifest['set_id'], 'snapshotRevision': manifest['snapshot_revision']}

    def trim(self, entries):
        while len(entries) > self.options['history_limit']:
            entries.pop(next(iter(entries)))

    def authorize(self, token):
        if token not in self.sessions:
            raise BuildError('invalid_session', 'Connect the selected database set first')

    def start(self, token, payload):
        with self.lock:
            self.authorize(token)
            request = payload.get('requestId')
            enabled = payload.get('enabled')
            if not isinstance(request, str) or not request or len(request) > 100:
                raise BuildError('invalid_request', 'A bounded request ID is required')
            if enabled is not None and (not isinstance(enabled, list) or any(not isinstance(v, str) for v in enabled)):
                raise BuildError('invalid_request', 'Enabled DLC must be an array of catalog IDs or null for all')
            for job in self.jobs.values():
                if job['status'] == 'running':
                    raise BuildError('service_busy', 'Another calculation is running')
            manifest = self.manifest()
            if payload.get('snapshotRevision') != manifest['snapshot_revision'] or self.sessions[token] != manifest['set_id']:
                raise BuildError('stale_snapshot', 'The registered snapshot changed; reopen the set')
            base = manifest.get('technology_tree', {}).get('combinations', {}).get(payload.get('baseCombinationId'))
            if not base or base['parameters']['profile'] != self.settings.facts:
                raise BuildError('invalid_combination', 'Select a prepared combination with the configured reference profile')
            identifier = secrets.token_hex(16)
            job = {'id': identifier, 'requestId': request, 'owner': token, 'status': 'running',
                   'before': manifest['snapshot_revision'], 'cancel': Event(), 'result': None, 'error': None}
            self.jobs[identifier] = job
            self.trim(self.jobs)
            self.executor.submit(self.calculate, job, enabled, base['parameters']['variants'])
            return self.public(job)

    def calculate(self, job, enabled, variants):
        @contextmanager
        def commit():
            with self.lock:
                yield
                job['committed'] = True
        try:
            report = execute(self.variables, self.config, dlc_enabled=enabled,
                             expected_revision=job['before'], cancelled=job['cancel'].is_set,
                             variants=variants, commit_guard=commit, analysis_cache=self.analysis_cache)
            try:
                save_json(self.settings.work / 'reports/dlc' / (job['id'] + '.json'), report, 'technology_tree_report.schema.json')
            except (BuildError, OSError, ValueError) as exc:
                report['diagnostics'].append({'code': 'service_report_write_error', 'message': str(exc)})
            with self.lock:
                published_report_error = report.get('database_written') and (report.get('error') or {}).get('code') == 'report_write_error'
                if report['status'] == 'failed' and not published_report_error:
                    job['error'] = report['error']
                    job['status'] = 'cancelled' if report['error']['code'] == 'cancelled' else 'failed'
                else:
                    manifest = self.manifest()
                    self.snapshots[manifest['snapshot_revision']] = manifest
                    self.trim(self.snapshots)
                    job['status'] = 'completed'
                    job['result'] = {'setId': manifest['set_id'], 'snapshotRevision': manifest['snapshot_revision'],
                        'combinationId': report['combination']['id'], 'profile': report['combination']['dlc'],
                        'action': report['action'], 'counts': report['counts'], 'diagnostics': report['diagnostics'],
                        'timings': report['timings'], 'coverage': report['coverage']}
        except Exception as exc:
            with self.lock:
                job.update(status='failed', error={'code': getattr(exc, 'code', 'service_failed'), 'message': str(exc)})

    def get(self, token, identifier, cancel=False):
        with self.lock:
            self.authorize(token)
            job = self.jobs.get(identifier)
            if job is None or job['owner'] != token:
                raise BuildError('unknown_operation', 'Unknown operation for this session')
            if cancel and job['status'] == 'running' and not job.get('committed'):
                job['cancel'].set()
            return self.public(job)

    def snapshot(self, token, revision):
        with self.lock:
            self.authorize(token)
            manifest = self.snapshots.get(revision)
            if manifest is None or manifest['set_id'] != self.sessions[token]:
                raise BuildError('unknown_snapshot', 'Snapshot is no longer available; reopen the set')
            return manifest

    @staticmethod
    def public(job):
        return deepcopy({k: v for k, v in job.items() if k not in ('owner', 'cancel', 'committed')})

    def close(self):
        for job in self.jobs.values():
            job['cancel'].set()
        self.executor.shutdown(wait=True)
        self.analysis_cache.clear()
