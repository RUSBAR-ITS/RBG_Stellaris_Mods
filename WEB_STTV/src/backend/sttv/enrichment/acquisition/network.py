"""Compile acquisition entry points, callers, and ordered crisis progression."""

from sttv.enrichment.technology_tree.ast import fields, scalar
from .effects import Effects


def located_fields(body, name, pointer):
    return [(node['value'], f'{pointer}/items/{i}/value') for i, node in enumerate(body.get('items', []))
            if node.get('kind') == 'assignment' and node.get('key', {}).get('text', '').casefold() == name]


class Network:
    def __init__(self, compiler, options, records, coverage):
        self.compiler, self.graph, self.options = compiler, compiler.graph, options
        self.records, self.coverage = records, coverage
        self.routes, self.activations, self.event_calls, self.gaps = [], {}, {}, []
        self.roots, self.levels = {}, {}

    def compile(self):
        for record in self.records:
            if self.graph.cancelled is not None and self.graph.cancelled():
                from sttv.common.errors import BuildError
                raise BuildError('cancelled', 'Acquisition graph preparation cancelled')
            self.roots[record['record_id']] = self.graph.add('AND', object_ref={
                'source': record['source'], 'pointer': record['pointer']}, entry=record['type'], entry_id=record['id'])
        walker = Effects(self)
        specs = {s['type']: s for s in self.options['entries']['definitions']}
        for record in self.records:
            root, body = self.roots[record['record_id']], record['node'].get('value', {})
            kind, path = record['type'], record['pointer'] + '/value'
            spec = specs.get(kind)
            if spec:
                for field in spec['effects']:
                    for block, field_path in located_fields(body, field, path):
                        guard = root
                        if field == 'option':
                            children = [root] + [self.compiler.compile(b, p) for b, p in located_fields(block, 'trigger', field_path)]
                            guard = self.graph.add('AND', children)
                        walker.walk(block, guard, record, field_path)
                if kind == 'on_action':
                    walker.walk(body, root, record, path, ignored=spec['effects'])
            else:
                walker.walk(body, root, record, path, scope='unknown')
        for record in self.records:
            root, body = self.roots[record['record_id']], record['node'].get('value', {})
            kind, path = record['type'], record['pointer'] + '/value'
            spec = specs.get(kind)
            gates = [self.compiler.compile(b, p) for field in (spec['gates'] if spec else [])
                     for b, p in located_fields(body, field, path)]
            if kind in ('perk', 'tradition'):
                gates.append(self.graph.unknown('acquisition_choice_state', entry_id=record['id']))
            elif kind == 'event':
                callers = [*self.event_calls.get(record['id'], []), *self.event_calls.get('*', [])]
                if scalar(body, self.options['entries']['event_triggered']) != 'yes':
                    callers.append(self.graph.unknown('acquisition_automatic_event_state', entry_id=record['id']))
                if not callers:
                    callers.append(self.graph.unknown('acquisition_event_entry_unresolved', entry_id=record['id']))
                gates.append(self.graph.add('OR', callers))
            elif kind == 'crisis_path':
                callers = [*self.activations.get(record['id'], []), *self.activations.get('*', [])]
                gates.append(self.graph.add('OR', callers) if callers else
                             self.graph.unknown('acquisition_crisis_entry_unresolved', entry_id=record['id']))
            elif kind == 'crisis_level':
                self.levels.setdefault(record['id'], []).append(root)
            else:
                gates.append(self.graph.unknown('acquisition_entry_unconfirmed', source=record['source'], entry_id=record['id']))
            self.graph.nodes[root]['children'] = gates
        ordered = {}
        for record in self.records:
            if record['type'] != 'crisis_path':
                continue
            previous = self.roots[record['record_id']]
            for block in fields(record['node'].get('value', {}), self.options['entries']['crisis_levels']):
                for item in block.get('items', []):
                    identifier = item.get('text')
                    for root in self.levels.get(identifier, []):
                        ordered.setdefault(root, []).append(previous)
                    # A missing level is an unknown predecessor, never a skipped requirement.
                    level = self.graph.add('OR', self.levels[identifier]) if identifier in self.levels else self.graph.unknown(
                        'acquisition_missing_crisis_level', target=identifier)
                    previous = self.graph.add('AND', [self.roots[record['record_id']], level])
        for roots in self.levels.values():
            for root in roots:
                predecessors = ordered.get(root)
                self.graph.nodes[root]['children'].append(self.graph.add('OR', predecessors) if predecessors else
                    self.graph.unknown('acquisition_level_path_unresolved', node_id=root))

    def add_route(self, record, pointer, command, arguments, guard, scope):
        rule = self.options['effects']['commands'][command]
        target = arguments.get('text') if arguments.get('kind') == 'scalar' else scalar(arguments, rule['target'])
        target = '*' if rule['handler'] in ('random', 'copy_random', 'copy_all') else Effects.target(target)
        self.routes.append({'target': target, 'command': command, 'handler': rule['handler'], 'arguments': arguments,
            'result_kind': ('research_option' if rule['handler'] in ('option', 'random') or
                            rule['handler'] == 'copy_random' and fields(arguments, 'progress') else
                            'progress_only' if rule['handler'] == 'progress' else 'researched_technology'),
            'guard': guard, 'recipient': scope, 'record_id': record['record_id'], 'source': record['source'],
            'pointer': pointer, 'basis': rule['basis']})
