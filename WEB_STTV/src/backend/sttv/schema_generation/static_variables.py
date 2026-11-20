"""Static-variable configuration and aggregate report counters."""

from .helpers import obj


def counts():
    return obj({key: {'type': 'integer', 'minimum': 0} for key in
                ('files', 'global_definitions', 'local_definitions', 'references', 'substituted')})
