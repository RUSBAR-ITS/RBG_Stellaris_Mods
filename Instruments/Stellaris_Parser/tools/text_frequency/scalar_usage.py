"""Record structural uses of texts without inferring game semantics."""

from collections import Counter

from stellaris_parser.script.nodes import Assignment, Block, Conditional, Formula, LogicalOperation, Scalar, TaggedBlock
from stellaris_parser.script.nodes import InlineInvocation
from variable_filter import is_excluded_variable


def fresh_record(text):
    return {'text': text, 'count': 0, 'roles': Counter(), 'right_hand_types': Counter(),
            'assignment_operators': Counter(), 'scalar_forms': Counter(),
            'logical_name_occurrences': 0, 'examples': {}}


class UsageInventory:
    def __init__(self, vocabulary):
        self.records = {text: fresh_record(text) for text in vocabulary}
        self.file = None
        self.source = None

    def add(self, text, role, node, assignment=None):
        if is_excluded_variable(text):
            return
        record = self.records.get(text.casefold())
        if record is None:
            return
        record['count'] += 1
        record['roles'][role] += 1
        if isinstance(node, Scalar):
            form = ('quoted' if node.quoted else 'unquoted') + ('_parameterized' if node.parameters else '')
            record['scalar_forms'][form] += 1
        shape = type(assignment.value).__name__ if assignment else role
        if assignment:
            record['right_hand_types'][shape] += 1
            record['assignment_operators'][assignment.operator] += 1
        example_key = role + ':' + shape
        if example_key not in record['examples']:
            span = assignment.span if assignment else node.span
            raw = self.source.text[span.start:span.end]
            record['examples'][example_key] = {
                'file': self.file, 'line': span.line, 'column': span.column,
                'role': role, 'right_hand_type': shape if assignment else None,
                'snippet': raw[:240], 'truncated': len(raw) > 240,
            }

    def walk(self, node, role='list_value'):
        if isinstance(node, InlineInvocation):
            return
        if isinstance(node, Scalar):
            self.add(node.text, role, node)
        elif isinstance(node, Formula):
            self.add(node.raw, 'formula', node)
        elif isinstance(node, Assignment):
            self.add(node.key.text, 'assignment_key', node.key, node)
            self.walk(node.value, 'scalar_value')
        elif isinstance(node, LogicalOperation):
            record = self.records.get(node.name.text.casefold())
            if record is not None:
                record['logical_name_occurrences'] += 1
            self.walk(node.body)
        elif isinstance(node, TaggedBlock):
            self.add(node.tag.text, 'block_tag', node.tag)
            self.walk(node.block)
        elif isinstance(node, (Block, Conditional)):
            if isinstance(node, Conditional):
                self.add(node.parameter, 'conditional_parameter', node)
            for child in node.items:
                self.walk(child)
        else:
            raise TypeError(type(node).__name__)

    def consume(self, document, file):
        self.source, self.file = document.source, file
        for node in document.items:
            self.walk(node)

    def rows(self):
        result = []
        for record in self.records.values():
            row = {key: dict(value) if isinstance(value, Counter) else value
                   for key, value in record.items()}
            row['examples'] = list(record['examples'].values())
            result.append(row)
        return sorted(result, key=lambda row: (-row['count'], row['text']))


def scalar_assignment(row):
    return (row['roles'].get('assignment_key', 0) > 0
            and set(row['right_hand_types']) == {'Scalar'}
            and not row['roles'].get('block_tag', 0)
            and not row['logical_name_occurrences'])


def scalar_value_only(row):
    return (bool(row['roles']) and set(row['roles']) <= {'scalar_value', 'list_value'}
            and not row['logical_name_occurrences'])
