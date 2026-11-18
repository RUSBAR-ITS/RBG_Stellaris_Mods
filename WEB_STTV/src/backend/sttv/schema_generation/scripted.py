"""Named expansion settings and counters, independent of game commands."""

from .helpers import BOOL, TEXT, array, obj


def configuration():
    positive = {'type': 'integer', 'minimum': 1}
    return obj(dict(format_version={'const': 1},
                    name_case_sensitive=BOOL, parameter_case_sensitive=BOOL,
                    max_call_depth=positive, max_expanded_nodes=positive,
                    root_definition_files=array(TEXT, uniqueItems=True),
                    file_fields=array(TEXT, uniqueItems=True), definition_directives=array(TEXT, uniqueItems=True)))


def counts():
    count = {'type': 'integer', 'minimum': 0}
    return obj({kind: obj({key: count for key in
               ('files', 'definitions', 'local_definitions', 'encountered', 'expanded', 'failed', 'tests')})
               for kind in ('scripted_effect', 'scripted_trigger', 'script_value')})


def parameters():
    return obj({key: {'type': 'integer', 'minimum': 0} for key in
                ('defaults', 'retained_fragments', 'discarded_fragments')})
