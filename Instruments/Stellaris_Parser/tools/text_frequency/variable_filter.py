"""Recognize script variables and parameterized text in research lists."""

import re


SCRIPT_VARIABLE = re.compile(r'@(?:[A-Za-z0-9_]+|\$[^$\r\n]+\$)+')
PARAMETER = re.compile(r'\$[^$|\s]+(?:\|[^$]*)?\$')
VARIABLE_FILTER = {
    'kind': 'whole_script_variable_or_text_containing_template_parameter',
    'script_variable_pattern': SCRIPT_VARIABLE.pattern,
    'parameter_pattern': PARAMETER.pattern,
    'includes_parameterized_names': True,
    'removes_definition_names_and_references': True,
    'removes_definition_values': False,
    'standalone_template_parameters_excluded': True,
    'parameterized_text_excluded_whole': True,
    'formulas_excluded': 'only_when_containing_template_parameters',
    'embedded_at_references_excluded': False,
    'runtime_variable_semantics_inferred': False,
}


def exclusion_reason(text):
    if SCRIPT_VARIABLE.fullmatch(text):
        return 'script_variable'
    if PARAMETER.search(text):
        return 'template_parameter'
    return None


def is_excluded_variable(text):
    return exclusion_reason(text) is not None
