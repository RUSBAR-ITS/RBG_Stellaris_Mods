"""Build named definition indexes without binding unused bodies."""

from dataclasses import dataclass

from sttv.common.errors import BuildError
from ..inlining.text import slice_source
from ..nodes import Assignment, Block, Scalar


@dataclass
class Definition:
    name: str
    kind: str
    source: object
    node: object


class Index:
    def __init__(self, options):
        self.options, self.entries, self.file_fields = options, {}, {}
        self.values, self.value_options = {}, None
        self.counts = {kind: dict(files=0, definitions=0, local_definitions=0, encountered=0,
                                 expanded=0, failed=0, tests=0)
                       for kind in ('scripted_effect', 'scripted_trigger', 'script_value')}

    def key(self, name):
        return name if self.options['name_case_sensitive'] else name.casefold()

    def find(self, node):
        if not isinstance(node, Assignment) or node.key.quoted or node.key.parameters:
            return None
        return self.entries.get(self.key(node.key.text))

    def add(self, document, kind, syntax, variables):
        counts = self.counts[kind]
        entries = self.values if kind == 'script_value' else self.entries
        counts['files'] += 1
        width = len(syntax.lexical['block']['open'])
        for node in document.items:
            if variables.rules.declaration(node):
                counts['local_definitions'] += 1
                continue
            if (isinstance(node, Assignment) and node.operator == '=' and not node.key.quoted
                    and node.key.text in self.options['file_fields'] and isinstance(node.value, Scalar)):
                self.file_fields.setdefault(document.source.file, {})[node.key.text] = node.value.raw
                continue
            if (not isinstance(node, Assignment) or node.operator != '=' or node.key.quoted
                    or node.key.parameters or not isinstance(node.value, Block)):
                document.source.fail('invalid_scripted_definition', 'Expected a named block definition', node.span.start)
            name, key = node.key.text, self.key(node.key.text)
            if kind != 'script_value' and (syntax.is_inline(name) or syntax.logical_name(name) is not None):
                document.source.fail('scripted_name_conflict', f'Reserved construct: {name}', node.span.start)
            if key in entries:
                previous = entries[key]
                raise BuildError('duplicate_scripted_definition',
                                 f'{name}: {previous.source.file}:{previous.node.span.line} and '
                                 f'{document.source.file}:{node.span.line}')
            source = getattr(document, 'node_sources', {}).get(id(node), document.source)
            body = slice_source(source, node.value.span.start + width, node.value.span.end - width)
            body.environment = document.source.environment
            entries[key] = Definition(name, kind, body, node)
            counts['definitions'] += 1
