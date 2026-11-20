"""Finite three-valued dependency graph; cycles start at unknown, never at false."""

from collections import defaultdict, deque
from decimal import Decimal
from operator import eq, ne, lt, le, gt, ge


def conjunction(values):
    return False if False in values else None if None in values else True


def disjunction(values):
    return True if True in values else None if None in values else False


def invert(value):
    return None if value is None else not value


def consensus(values):
    return values[0] if values and all(v is values[0] for v in values) else None


def calculate(node, values, enabled):
    op, children = node['op'], [values[k] for k in node['children']]
    if op == 'constant':
        return node['constant']
    if op == 'dlc':
        return None if enabled is None else node['dlc_id'] in enabled
    if op in ('AND', 'OR', 'NOT', 'NAND', 'NOR'):
        result = (disjunction if op in ('OR', 'NOR') else conjunction)(children)
        return invert(result) if op in ('NOT', 'NAND', 'NOR') else result
    if op == 'presence':
        return False if children[0] is False else None
    if op == 'branch':
        guard, yes, no = children
        return yes if guard is True else no if guard is False else consensus([yes, no])
    if op == 'count':
        low = sum(v is True for v in children)
        high = low + sum(v is None for v in children)
        compare = {'=': eq, '!=': ne, '<': lt, '<=': le, '>': gt, '>=': ge}[node['comparison']]
        return consensus([compare(n, Decimal(node['threshold'])) for n in range(low, high + 1)])
    return None


class Graph:
    def __init__(self, limits, cancelled=None):
        self.nodes, self.diagnostics = {}, []
        self.limits, self.cancelled = limits, cancelled
        self.baseline, self.last = None, None
        self.statistics = {}

    def add(self, op, children=(), **details):
        if len(self.nodes) >= self.limits['max_nodes']:
            key = 'node_limit'
            if key not in self.nodes:
                self.nodes[key] = {'op': 'unknown', 'children': [], 'unknown': 'dlc_node_limit'}
                self.diagnostics.append({'code': 'dlc_node_limit', 'limit': self.limits['max_nodes']})
            return key
        key = f'n{len(self.nodes)}'
        self.nodes[key] = {'op': op, 'children': list(children), **details}
        return key

    def unknown(self, code, **details):
        self.diagnostics.append({'code': code, **details})
        return self.add('unknown', unknown=code, **details)

    def solve(self, enabled):
        values = dict.fromkeys(self.nodes)
        parents = defaultdict(set)
        for key, node in self.nodes.items():
            for child in node['children']:
                parents[child].add(key)
        queue, pending = deque(self.nodes), set(self.nodes)
        steps = 0
        while queue and steps < self.limits['max_steps']:
            if self.cancelled is not None and self.cancelled():
                from sttv.common.errors import BuildError
                raise BuildError('cancelled', 'DLC evaluation cancelled')
            key = queue.popleft()
            pending.remove(key)
            steps += 1
            value = calculate(self.nodes[key], values, enabled)
            if value is not values[key]:
                values[key] = value
                for parent in sorted(parents[key]):
                    if parent not in pending:
                        pending.add(parent)
                        queue.append(parent)
        # An incomplete baseline cannot establish DLC causality; fail conservatively.
        self.statistics['steps'] = steps
        if queue:
            self.diagnostics.append({'code': 'dlc_refinement_limit', 'pending': len(queue)})
            return dict.fromkeys(self.nodes)
        return values

    def evaluate(self, enabled):
        profile = tuple(sorted(enabled))
        if self.last is not None and self.last[0] == profile:
            self.statistics['reused_profile'] = True
            return self.last[1]
        if self.baseline is None:
            self.baseline = self.solve(None)
        values = self.solve(set(profile))
        self.statistics.update(nodes=len(self.nodes), reused_profile=False)
        self.last = profile, values
        return values

    def trace(self, key, values, active=frozenset()):
        node = self.nodes[key]
        trace = {k: v for k, v in node.items() if k not in ('op', 'children')}
        trace.update(node_id=key, value=values[key], baseline=self.baseline[key])
        if key in active or node.get('object_ref'):
            return {**trace, 'reference': key}
        trace['operator'] = node['op']
        if node['children']:
            trace['children'] = [self.trace(c, values, active | {key}) for c in node['children']]
        return trace

    def evidence(self, values):
        return {key: {**node, 'value': values[key], 'baseline': self.baseline[key]}
                for key, node in self.nodes.items()}
