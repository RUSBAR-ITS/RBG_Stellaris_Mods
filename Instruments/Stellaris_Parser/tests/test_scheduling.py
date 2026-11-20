"""Deterministic dispatch tests without timing assumptions."""

from concurrent.futures import Future
from pathlib import Path
import unittest

from stellaris_parser.scheduling import dispatch, run_jobs
from stellaris_parser.sources import SourceFile


class SchedulingTests(unittest.TestCase):
    def test_largest_first_with_root_relative_tie_break(self):
        jobs = [SourceFile(path, Path(path), size) for path, size in (
            ('events/a.txt', 1), ('common/t.txt', 1), ('events/b.txt', 10))]
        results = run_jobs(jobs, 1, lambda job: job.relative, lambda: None, ())
        self.assertEqual([name for _, name in results], ['events/b.txt', 'common/t.txt', 'events/a.txt'])

    def test_first_available_worker_receives_next_file(self):
        submitted = []

        class Executor:
            def submit(self, execute, job):
                future = Future()
                submitted.append(future)
                if job == 2:
                    future.set_result(job)
                if job == 3:
                    future.set_result(not submitted[0].done())
                    submitted[0].set_result(1)
                return future

        result = dict(dispatch([1, 2, 3], Executor(), None, 2))
        self.assertIs(result[3], True)
