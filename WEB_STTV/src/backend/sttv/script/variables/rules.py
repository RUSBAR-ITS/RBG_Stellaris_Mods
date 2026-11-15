"""Recognize configured static names and report errors at their use sites."""

import re

from sttv.common.errors import BuildError
from sttv.common.schema import validate_schema
from ..nodes import Assignment, Scalar


def fail(code, message, node):
    origin = node.origin
    span = origin['span'] if origin else vars(node.span)
    file = origin['file'] if origin else '<text>'
    error = BuildError(code, f"{file}:{span['line']}:{span['column']}: {message}", line=span['line'])
    error.column, error.provenance = span['column'], origin
    raise error


class Rules:
    def __init__(self, options, syntax):
        validate_schema(options, 'parser_static_variables.schema.json')
        self.options = options
        self.prefix = options['prefix']
        try:
            self.pattern = re.compile(options['name_pattern'])
        except re.error as exc:
            raise BuildError('static_variable_configuration', f'Invalid name pattern: {exc}') from exc
        markers = [syntax.lexical['line_comment'], syntax.lexical['string']['quote'],
                   syntax.lexical['string']['escape'], *syntax.lexical['block'].values(),
                   *syntax.lexical['operators'], syntax.constructs['parameters']['open'],
                   syntax.constructs['conditional']['open'],
                   *(item['open'] for item in syntax.constructs['formulas'])]
        if (self.pattern.fullmatch('') or any(char.isspace() for char in self.prefix)
                or any(marker in self.prefix for marker in markers)):
            raise BuildError('static_variable_configuration', 'Empty names or conflicting variable prefix')

    def normalize(self, name):
        return name if self.options['case_sensitive'] else name.casefold()

    def reference(self, node):
        if (not isinstance(node, Scalar) or node.quoted or node.parameters
                or not node.text.startswith(self.prefix)):
            return None
        if self.pattern.fullmatch(node.text[len(self.prefix):]):
            return self.normalize(node.text)
        return None

    def declaration(self, node):
        return (isinstance(node, Assignment) and not node.key.quoted
                and node.key.text.startswith(self.prefix))
