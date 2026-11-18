"""Optional operation-local preparation and application measurements."""

from contextvars import ContextVar
from functools import wraps
from time import perf_counter

ACTIVE = ContextVar('sttv_script_metrics', default=None)


class Metrics:
    def __init__(self, report):
        self.report, self.phase, self.depth = report, 'prepare', 0

    def count(self, name, amount=1):
        counts = self.report['counts']
        key = f'{self.phase}_{name}'
        counts[key] = counts.get(key, 0) + amount

    def seconds(self, name, elapsed):
        timings = self.report['timings']
        key = f'{self.phase}_{name}'
        timings[key] = timings.get(key, 0) + elapsed


def measured_application(function):
    @wraps(function)
    def execute(*args, **kwargs):
        metrics = ACTIVE.get()
        if metrics is None:
            return function(*args, **kwargs)
        start, outer = perf_counter(), metrics.depth == 0
        metrics.depth += 1
        try:
            return function(*args, **kwargs)
        finally:
            metrics.depth -= 1
            if outer:
                metrics.seconds('application', perf_counter() - start)
    return execute
