"""Named expansion settings and counters, independent of game commands."""

from .helpers import obj


def counts():
    count = {'type': 'integer', 'minimum': 0}
    return obj({kind: obj({key: count for key in
               ('files', 'definitions', 'local_definitions', 'encountered', 'expanded', 'failed', 'tests')})
               for kind in ('scripted_effect', 'scripted_trigger', 'script_value')})


def parameters():
    return obj({key: {'type': 'integer', 'minimum': 0} for key in
                ('defaults', 'retained_fragments', 'discarded_fragments')})
