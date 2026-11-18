"""Static-variable configuration and aggregate report counters."""

from .helpers import BOOL, TEXT, obj


def configuration():
    return obj({'format_version': {'const': 1}, 'prefix': TEXT, 'name_pattern': TEXT,
                'case_sensitive': BOOL,
                'max_reference_depth': {'type': 'integer', 'minimum': 1}})


def counts():
    return obj({key: {'type': 'integer', 'minimum': 0} for key in
                ('files', 'global_definitions', 'local_definitions', 'references', 'substituted')})
