"""Non-overlapping operation measurements kept outside persisted game data."""

from contextlib import contextmanager
from time import perf_counter


def performance():
    return {'timings': {}, 'rule_preparations': 0, 'validated_documents': 0, 'documents': []}


@contextmanager
def measure(target, name):
    start = perf_counter()
    try:
        yield
    finally:
        target[name] = target.get(name, 0.0) + perf_counter() - start
