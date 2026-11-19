"""Real spawn workers, varied scheduling, isolation and failure publication."""

import json
import os
from pathlib import Path
from time import sleep
from unittest.mock import patch

from libraries.fixture import LibraryFixture
from sttv.builder import build
from sttv.parallel.worker import execute
from sttv.common.errors import BuildError
from sttv.sources.settings import load_settings
from sttv.parallel.worker import initialize


def reverse_completion(job):
    sleep((12 - min(job['index'], 12)) * 0.03)
    return execute(job)


def crash(job):
    os._exit(7)


def wrong_result(job):
    result = execute(job)
    result['index'] += 1
    return result


def failed_initialization(*args):
    initialize(*args)
    from sttv.parallel import worker
    worker.STATE['error'] = ('worker_initialization', 'Simulated initialization failure')


class ParallelTests(LibraryFixture):
    def configure_workers(self, workers, directory='staging/parallel'):
        work = Path(self.variables['WORK_DIR'])
        work.mkdir(parents=True, exist_ok=True)
        path = work / 'parallel.json'
        path.write_text(json.dumps({'format_version': 1, 'workers': workers,
                                   'staging_directory': directory}), encoding='utf-8')
        self.options['parallel'] = {'base': 'work', 'path': path.name}
        self.persist()

    def assert_clean(self):
        root = Path(self.variables['WORK_DIR']) / 'staging/parallel'
        self.assertFalse(list(root.glob('operation-*')))
        self.assertFalse(list(Path(self.variables['WORK_DIR']).rglob('.sttv-libraries.lock')))

    def test_one_and_ten_workers_match_with_different_completion_order(self):
        for number in range(12):
            self.write_script(f'extra_{number:02d}.txt',
                              '@local=%d tech_%d={n=@local effect_a={N=%d}}' % (number, number, number + 1))
        self.configure_workers(1)
        first = self.run_build()
        self.assertEqual(first['status'], 'success', first['diagnostics'])
        expected = self.database_path().read_bytes()
        self.configure_workers(10)
        with patch('sttv.parallel.pool.execute', reverse_completion):
            second = build(self.variable_file, self.config_file, library_mode='reuse')
        self.assertEqual(second['status'], 'success', second['diagnostics'])
        self.assertEqual(expected, self.database_path().read_bytes())
        self.assertEqual(first['counts'], second['counts'])
        rows = second['performance']['parallel']['jobs']
        self.assertEqual([row['index'] for row in rows], list(range(len(rows))))
        self.assertGreater(second['performance']['parallel']['used_workers'], 1)
        self.assertEqual([r['content_hash'] for r in first['performance']['parallel']['jobs']],
                         [r['content_hash'] for r in rows])
        self.assert_clean()

    def test_worker_crash_fails_without_replacing_existing_database(self):
        self.configure_workers(2)
        self.assertEqual(self.run_build()['status'], 'success')
        expected = self.database_path().read_bytes()
        with patch('sttv.parallel.pool.execute', crash):
            result = build(self.variable_file, self.config_file, library_mode='reuse')
        self.assertEqual(result['status'], 'failed')
        self.assertIn('worker_failure', self.errors(result))
        self.assertEqual(expected, self.database_path().read_bytes())
        self.assert_clean()

    def test_foreign_result_fails_and_cleans_fragments(self):
        self.configure_workers(2)
        with patch('sttv.parallel.pool.execute', wrong_result):
            result = self.run_build()
        self.assertEqual(result['status'], 'failed')
        self.assertFalse(self.database_path().exists())
        self.assert_clean()

    def test_invalid_concurrency_and_overlapping_paths(self):
        for workers in (0, -1, True, 1.5):
            with self.subTest(workers=workers):
                self.configure_workers(workers)
                with self.assertRaises(BuildError):
                    load_settings(self.variable_file, self.config_file)
        for directory in ('libraries', '.', '../outside', 'database_set/manifest.json'):
            with self.subTest(directory=directory):
                self.configure_workers(10, directory)
                with self.assertRaises(BuildError):
                    load_settings(self.variable_file, self.config_file)

    def test_single_file_and_more_workers_than_files(self):
        self.configure_workers(10)
        self.options['sources'][0].update(pattern='base.txt', recursive=False)
        result = self.run_build()
        self.assertEqual(result['status'], 'success', result['diagnostics'])
        self.assertEqual(result['counts']['parsed_files'], 1)
        self.assertEqual(len(result['performance']['parallel']['jobs']), 1)
        self.assert_clean()

    def test_cancelled_operation_releases_waiting_workers(self):
        self.configure_workers(2)
        from sttv.parallel import pool
        wait = pool.wait
        calls = []
        def interrupt_once(*args, **kwargs):
            if not calls:
                calls.append(True)
                raise KeyboardInterrupt()
            return wait(*args, **kwargs)
        with patch.object(pool, 'wait', interrupt_once):
            result = self.run_build()
        self.assertEqual(result['status'], 'failed')
        self.assertIn('build_cancelled', self.errors(result))
        self.assert_clean()

    def test_initializer_failure_is_reported_and_does_not_publish(self):
        self.configure_workers(2)
        with patch('sttv.parallel.pool.initialize', failed_initialization):
            result = self.run_build()
        self.assertEqual(result['status'], 'failed')
        self.assertIn('worker_initialization', self.errors(result))
        self.assertFalse(self.database_path().exists())
        self.assert_clean()
