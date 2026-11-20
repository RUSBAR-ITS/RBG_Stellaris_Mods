"""Bounded file dispatch and ownership of one operation's temporary results."""

from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from multiprocessing import get_context
from pathlib import Path
from tempfile import mkdtemp
from types import SimpleNamespace
from time import perf_counter
import shutil

from sttv.common.errors import BuildError
from sttv.sources.files import selected_files
from sttv.storage.identity import SOURCE_ALGORITHM
from .results import aggregate
from .worker import initialize, execute
from .memory import Monitor
from .ordering import Ordering


class Pool:
    def __init__(self, settings, snapshot):
        self.settings, self.snapshot = settings, snapshot
        self.root, self.executor = None, None
        self.monitor = None
        self.requests, self.responses = None, []
        self.acquisition_options, self.acquisition_results = None, []

    def __enter__(self):
        options = self.settings.parallel
        options['directory'].mkdir(parents=True, exist_ok=True)
        self.root = Path(mkdtemp(prefix='operation-', dir=options['directory'])).resolve()
        self.monitor = Monitor(self.root)
        inventory = self.snapshot.inventory
        fixed = SimpleNamespace(rows=inventory.rows, fingerprint=inventory.fingerprint,
                                configuration_hash=inventory.configuration_hash)
        try:
            context = get_context('spawn')
            self.requests = context.Queue()
            self.responses = [context.Queue() for _ in range(options['workers'])]
            ranks = context.Value('i', 0)
            self.executor = ProcessPoolExecutor(max_workers=options['workers'], mp_context=context,
                initializer=initialize, initargs=(self.settings, fixed, self.snapshot.report['library_set_id'],
                                                  self.requests, self.responses, ranks))
        except BaseException:
            self.__exit__(None, None, None)
            raise
        return self

    def __exit__(self, *_):
        if self.executor is not None:
            self.executor.shutdown(wait=True, cancel_futures=True)
            self.executor = None
        if self.monitor is not None:
            self.monitor.close()
        for queue in [self.requests, *self.responses]:
            if queue is not None:
                queue.close()
                queue.join_thread()
        self.requests, self.responses = None, []
        if self.root is not None:
            parent = self.settings.parallel['directory'].resolve()
            if self.root.parent != parent or not self.root.name.startswith('operation-'):
                raise BuildError('unsafe_output', 'Refusing cleanup outside the owned operation directory')
            shutil.rmtree(self.root)
            self.root = None

    def build(self, kind, settings, report, local=None, local_report=None):
        files = selected_files(settings)
        report.data['counts']['selected_files'] = len(files)
        self.snapshot.variables(settings, report)
        directory = (self.root / kind).resolve()
        if directory.parent != self.root:
            raise BuildError('unsafe_output', 'Member staging must remain inside the operation directory')
        directory.mkdir()
        parallel = {'configured_workers': settings.parallel['workers'], 'used_workers': 0,
                    'identity_algorithm': SOURCE_ALGORITHM, 'jobs': [], 'workers': [], 'memory': self.monitor.data}
        report.data['performance']['parallel'] = parallel
        jobs = []
        for index, (path, encoding) in enumerate(files):
            source = path.relative_to(settings.game).as_posix()
            jobs.append({'kind': kind, 'index': index, 'source': source, 'path': str(path), 'encoding': encoding,
                         'settings': settings, 'local': local, 'acquisition': self.acquisition_options,
                         'output': str(directory / f'{index:06d}.json')})
            parallel['jobs'].append({'index': index, 'source': source, 'status': 'not_started', 'pid': None,
                                    'seconds': 0.0, 'bytes': 0, 'content_hash': None, 'shard_hash': None})
        results, pending, cursor, failed = {}, {}, 0, False
        error = None
        started = perf_counter()
        ordering = Ordering(kind, len(jobs), self.requests, self.responses)
        try:
            while cursor < len(jobs) or pending:
                while not failed and cursor < len(jobs) and len(pending) < settings.parallel['workers']:
                    job = jobs[cursor]
                    pending[self.executor.submit(execute, job)] = job
                    cursor += 1
                if not pending:
                    break
                ordering.receive()
                done, _ = wait(pending, timeout=0.05, return_when=FIRST_COMPLETED)
                for future in done:
                    job = pending.pop(future)
                    if future.cancelled():
                        parallel['jobs'][job['index']]['status'] = 'cancelled'
                        continue
                    try:
                        result = future.result()
                        if (result['index'] != job['index'] or result['source'] != job['source']
                                or result['index'] in results):
                            raise BuildError('parallel_result', 'Repeated or mismatched job result')
                        fragment = result['fragment']
                        if fragment is not None and Path(fragment['path']).resolve() != Path(job['output']).resolve():
                            raise BuildError('parallel_result', 'Unexpected intermediate file')
                        results[result['index']] = result
                        if result.get('acquisition'):
                            self.acquisition_results.append(result['acquisition'])
                        summary = parallel['jobs'][job['index']]
                        summary.update(status=result['status'], pid=result['pid'], seconds=result['seconds'])
                        if fragment:
                            summary.update({key: fragment[key] for key in ('bytes', 'content_hash', 'shard_hash')})
                        failed |= result['status'] != 'success'
                    except Exception as exc:
                        parallel['jobs'][job['index']]['status'] = 'failed'
                        failed, error = True, exc
                if failed:
                    ordering.abort()
                    for future in pending:
                        future.cancel()
        except BaseException as exc:
            ordering.abort()
            for future, job in pending.items():
                future.cancel()
                parallel['jobs'][job['index']]['status'] = 'cancelled'
            while pending:
                ordering.receive()
                done, _ = wait(pending, timeout=0.05, return_when=FIRST_COMPLETED)
                for future in done:
                    pending.pop(future)
            if isinstance(exc, KeyboardInterrupt):
                raise BuildError('build_cancelled', 'Build cancelled by user') from exc
            raise
        finally:
            report.data['performance']['timings']['parallel_wall'] = perf_counter() - started
            parallel['used_workers'] = len({row['pid'] for row in parallel['jobs'] if row['pid'] is not None})
        ordered = [results[index] for index in sorted(results)]
        aggregate(ordered, report, local_report, self.snapshot.report, parallel)
        if error is not None:
            raise BuildError('worker_failure', str(error)) from error
        if failed or report.failed:
            raise BuildError('parallel_document_failed', 'Document processing failed; see document diagnostics')
        if len(results) != len(jobs):
            raise BuildError('parallel_incomplete', 'Not every source produced exactly one result')
        return ordered
