"""Closed configuration and reporting for approved in-memory corrections."""

from .helpers import NULL, RELATIVE, STRING, TEXT, array, obj, union
from . import inline


def configuration():
    root = {'root_files': array(RELATIVE, minItems=1, uniqueItems=True)}
    scalar = obj({'id': TEXT, 'kind': {'const': 'script_value_reference'}, 'reason': TEXT,
                  'match': obj(dict(root, file=RELATIVE, scalar=TEXT)),
                  'action': obj({'replace_scalar': TEXT})})
    matching = dict(root, call_kind={'enum': ['inline_script', 'scripted_effect', 'scripted_trigger', 'script_value']},
                    definition_file=RELATIVE, call_name=TEXT, reference=TEXT, missing_parameter=TEXT,
                    required_parameters=array(TEXT, uniqueItems=True))
    parameter = obj({'id': TEXT, 'kind': {'const': 'missing_parameter'}, 'reason': TEXT,
                     'match': obj(matching, [key for key in matching if key != 'call_name']),
                     'action': union(obj({'parameter_from': TEXT}), obj({'parameter_literal': STRING}),
                         obj({'parameter_from_object': obj({'field': TEXT,
                             'allowed_values': array(TEXT, minItems=1, uniqueItems=True),
                             'multiple_literal': TEXT})}))})
    separator = obj({'id': TEXT, 'kind': {'const': 'missing_assignment_separator'}, 'reason': TEXT,
        'match': obj(dict(root, containers=array(TEXT, minItems=1), field=TEXT, value={'const': '""'})),
        'action': obj({'insert': {'const': ' ='}})})
    return obj({'format_version': {'const': 1}, 'rules': array(union(scalar, parameter, separator))})


def application():
    return obj({'rule_id': TEXT, 'root_source': {'$ref': '#/$defs/origin'},
                'provenance': {'$ref': '#/$defs/origin'}, 'call_chain': inline.chain(),
                'before': union(STRING, NULL), 'after': STRING, 'value_source': TEXT})
