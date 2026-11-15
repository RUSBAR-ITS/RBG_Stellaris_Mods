"""Read-only AST statistics for the optional corpus acceptance run."""

import re
import json
from collections import Counter

from sttv.script.nodes import Assignment, Block, Conditional, Formula, LogicalOperation, Scalar, TaggedBlock

VARIABLE = re.compile(r'@(?:[A-Za-z0-9_]+|\$[^$\r\n]+\$)+')
PARAMETER = re.compile(r'\$[^$|\s]+(?:\|[^$]*)?\$')


class Statistics:
    def __init__(self):
        self.rows = {}
        self.logical = Counter()
        self.excluded = Counter()
        self.node_count = 0

    def add(self, text, role, node, shape=None):
        key = text.casefold()
        if VARIABLE.fullmatch(text) or PARAMETER.search(text):
            self.excluded['variables'] += 1
            return
        if key in ('yes', 'no'):
            self.excluded[key] += 1
            return
        row = self.rows.setdefault(key, {'text': key, 'count': 0, 'roles': Counter(),
                                         'right_hand_types': Counter(), 'examples': {}})
        row['count'] += 1
        row['roles'][role] += 1
        if shape:
            row['right_hand_types'][shape] += 1
        sample = role + ':' + str(shape)
        if sample not in row['examples']:
            origin = node.origin
            row['examples'][sample] = {key: origin[key] for key in ('root', 'file', 'inline_call_id')}
            row['examples'][sample].update(line=origin['span']['line'], column=origin['span']['column'])

    def walk(self, node, role='list_value'):
        self.node_count += 1
        if isinstance(node, Scalar):
            self.add(node.text, role, node)
        elif isinstance(node, Formula):
            self.add(node.raw, 'formula', node)
        elif isinstance(node, Assignment):
            self.node_count += 1
            self.add(node.key.text, 'assignment_key', node.key, type(node.value).__name__)
            self.walk(node.value, 'scalar_value')
        elif isinstance(node, LogicalOperation):
            self.node_count += 1
            self.logical[node.operator.casefold()] += 1
            self.walk(node.body)
        elif isinstance(node, TaggedBlock):
            self.node_count += 1
            self.add(node.tag.text, 'block_tag', node.tag)
            self.walk(node.block)
        elif isinstance(node, (Block, Conditional)):
            if isinstance(node, Conditional):
                self.add(node.parameter, 'conditional_parameter', node)
            for child in node.items:
                self.walk(child)
        else:
            raise TypeError(type(node).__name__)

    def consume(self, document):
        for node in document.items:
            self.walk(node)

    def lists(self):
        rows = sorted((row for row in self.rows.values() if row['count'] >= 2),
                      key=lambda row: (-row['count'], row['text']))
        values = [row for row in rows if set(row['roles']) <= {'scalar_value', 'list_value'}
                  and row['text'] not in self.logical]
        assignments = [row for row in rows if set(row['right_hand_types']) == {'Scalar'}
                       and not row['roles'].get('block_tag') and row['text'] not in self.logical]
        return {'frequencies': rows, 'scalar_values': values, 'scalar_assignments': assignments}

    def write(self, directory):
        directory.mkdir(parents=True, exist_ok=True)
        result = {}
        for name, rows in self.lists().items():
            destination = directory if name == 'frequencies' else directory / 'scalar_analysis'
            destination.mkdir(exist_ok=True)
            (destination / (name + '.txt')).write_text(
                ''.join(f"{json.dumps(row['text'], ensure_ascii=False)[1:-1]}:{row['count']}\n" for row in rows),
                encoding='utf-8')
            data = [{'text': row['text'], 'count': row['count']} for row in rows] if name == 'frequencies' else rows
            (destination / (name + '.json')).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            result[name] = len(rows)
        return result
