"""Size-ordered, bounded dispatch shared by the two parser phases."""

from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from multiprocessing import get_context
import sys


def dispatch(jobs, executor, execute, limit):
    queue = iter(jobs)
    pending = {}

    def submit_next():
        job = next(queue, None)
        if job is not None:
            pending[executor.submit(execute, job)] = job

    for _ in range(limit):
        submit_next()
    while pending:
        completed, _ = wait(pending, return_when=FIRST_COMPLETED)
        for future in completed:
            job = pending.pop(future)
            result = future.result()
            submit_next()
            yield job, result


def run_jobs(jobs, workers, execute, initializer, initargs):
    ordered = sorted(jobs, key=lambda job: (-job.size, job.relative))
    if not ordered:
        return
    limit = min(workers, len(ordered))
    if sys.platform == 'win32':
        # ProcessPoolExecutor supports at most 61 workers on Windows.
        limit = min(limit, 61)
    if limit == 1:
        initializer(*initargs)
        for job in ordered:
            yield job, execute(job)
        return
    with ProcessPoolExecutor(max_workers=limit, mp_context=get_context('spawn'),
                             initializer=initializer, initargs=initargs) as pool:
        yield from dispatch(ordered, pool, execute, limit)
