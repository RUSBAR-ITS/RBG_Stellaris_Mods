"""Follow effect execution guards without evaluating runtime state or probabilities."""

from sttv.enrichment.technology_tree.ast import fields, scalar
from .extraction import key, reference_target


class Effects:
    def __init__(self, network):
        self.network = network
        self.graph, self.compiler = network.graph, network.compiler
        self.rules, self.entries = network.options['effects'], network.options['entries']
        self.relevant = set()
        for record in network.records:
            self.mark(record['node'].get('value', {}))

    def mark(self, node):
        name = key(node)
        if name in self.entries['condition_fields']:
            return False
        found = name in self.rules['commands'] or name in self.rules['event_calls'] or name in self.entries['event_lists'] or name == self.rules['activation']
        for field in ('value', 'body', 'block'):
            if isinstance(node.get(field), dict):
                found = self.mark(node[field]) or found
        for child in node.get('items', []):
            found = self.mark(child) or found
        if found:
            self.relevant.add(id(node))
        return found

    def condition(self, body, pointer, scope, dirty):
        context = 'country' if scope == 'recipient' and not dirty else 'acquisition_runtime'
        return self.compiler.compile(body, pointer, context)

    def branch_indices(self, items):
        enabled, chain = set(), []
        def flush():
            if any(id(items[i]) in self.relevant for i in chain):
                enabled.update(chain)
            chain.clear()
        for i, node in enumerate(items):
            name = key(node)
            if name == 'if':
                flush()
                chain.append(i)
            elif name in ('else_if', 'else'):
                chain.append(i)
            else:
                flush()
        flush()
        return enabled

    def walk(self, body, guard, record, pointer, scope='recipient', dirty=False, depth=0, ignored=()):
        from .network import located_fields
        if depth > self.rules['limits']['max_depth']:
            self.network.gaps.append(self.graph.unknown('acquisition_depth_limit', source=record['source'], pointer=pointer))
            return
        excluded = []
        items = body.get('items', [])
        branches = self.branch_indices(items)
        for i, node in enumerate(items):
            path = f'{pointer}/items/{i}'
            name, value = key(node), node.get('value', {})
            if name in self.entries['condition_fields'] or name in ignored:
                continue
            if id(node) not in self.relevant and name not in self.rules['branches']:
                dirty |= name not in self.rules['safe_actions']
                continue
            if node.get('kind') != 'assignment':
                uncertain = self.graph.unknown('acquisition_unknown_effect_node', source=record['source'], pointer=path)
                nested_guard = self.graph.add('AND', [guard, uncertain])
                for field in ('value', 'body', 'block'):
                    if isinstance(node.get(field), dict):
                        self.walk(node[field], nested_guard, record, path + '/' + field, scope, True, depth + 1)
                if 'items' in node:
                    self.walk(node, nested_guard, record, path, scope, True, depth + 1)
                dirty = True
                continue
            if name in self.rules['branches']:
                if i not in branches:
                    dirty = True
                    excluded = []
                    continue
                if name == 'if':
                    excluded = []
                limits = located_fields(value, 'limit', path + '/value')
                valid = name == 'else' or len(limits) == 1
                test = (self.condition(limits[0][0], limits[0][1], scope, dirty) if limits
                        else self.graph.add('constant', constant=True) if name == 'else'
                        else self.graph.unknown('acquisition_missing_limit', pointer=path))
                branch = self.graph.add('AND', [guard, test, *[self.graph.add('NOT', [n]) for n in excluded]],
                                        pointer=path, source=record['source'])
                if not valid:
                    branch = self.graph.add('AND', [guard, self.graph.unknown('acquisition_invalid_branch', pointer=path)])
                self.walk(value, branch, record, path + '/value', scope, dirty, depth + 1)
                excluded.append(test)
                dirty = True
                continue
            excluded = []
            if name in self.rules['commands']:
                self.network.add_route(record, path, name, value, guard, scope)
                for failure, failure_path in located_fields(value, self.rules['failure_field'], path + '/value'):
                    failed = self.graph.unknown('acquisition_selection_failure_unknown', pointer=path)
                    self.walk(failure, self.graph.add('AND', [guard, failed]), record,
                              failure_path, scope, dirty, depth + 1)
                dirty = True
            elif name == self.rules['activation']:
                target = value.get('text')
                self.network.activations.setdefault(self.target(target), []).append(guard)
            elif name in self.rules['event_calls']:
                target = value.get('text') if value.get('kind') == 'scalar' else scalar(value, self.entries['event_id'])
                self.network.event_calls.setdefault(self.target(target), []).append(guard)
            elif name in self.entries['event_lists']:
                for event in value.get('items', []):
                    target = event.get('text') if event.get('kind') == 'scalar' else event.get('value', {}).get('text')
                    if target:
                        self.network.event_calls.setdefault(self.target(target), []).append(guard)
            elif name in self.rules['transparent']:
                self.walk(value, guard, record, path + '/value', scope, dirty, depth + 1)
                dirty = True
            elif name in self.rules['scopes']:
                self.walk(value, guard, record, path + '/value', scope + '/' + name, dirty, depth + 1)
                dirty = True
            elif name == 'random_list':
                for j, choice in enumerate(value.get('items', [])):
                    self.walk(choice.get('value', {}), guard, record, f'{path}/value/items/{j}/value', scope, dirty, depth + 1)
                dirty = True
            elif name == 'random':
                self.walk(value, guard, record, path + '/value', scope, dirty, depth + 1)
                dirty = True
            else:
                # Unknown blocks may contain an effect; retain that possible route.
                if value.get('kind') == 'block':
                    uncertain = self.graph.unknown('acquisition_unknown_effect_container', predicate=name,
                                                    source=record['source'], pointer=path)
                    self.walk(value, self.graph.add('AND', [guard, uncertain]), record,
                              path + '/value', scope + '/' + name, True, depth + 1)
                dirty |= name not in self.rules['safe_actions']

    @staticmethod
    def target(text):
        return reference_target(text)
