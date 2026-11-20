"""Prepare reusable condition roots once and evaluate explicit DLC profiles."""

from time import perf_counter
from sttv.common.errors import BuildError
from sttv.enrichment.technology_tree.ast import number
from .conditions import Compiler
from .graph import Graph
from .objects import Library, References


def entries(body, key, pointer):
    return [(node['value'], f'{pointer}/items/{i}/value') for i, node in enumerate(body.get('items', []))
            if node.get('kind') == 'assignment' and node['key']['text'] == key and node['operator'] == '=']


def unsupported_weight(node, rules):
    if node.get('key', {}).get('text') in rules['unsupported_actions']:
        return True
    return any(unsupported_weight(value, rules) for value in node.values() if isinstance(value, dict)) or any(
        unsupported_weight(child, rules) for value in node.values() if isinstance(value, list)
        for child in value if isinstance(child, dict))


class Analysis:
    def __init__(self, technologies, names, rules, *, reader=None, records=None, cancelled=None):
        start = perf_counter()
        if reader is not None:
            missing = set(rules['required_datasets']) - reader.manifest['datasets'].keys()
            if missing:
                raise BuildError('missing_dlc_catalogs', f'Prepare a new database set: missing {sorted(missing)}')
        self.technologies, self.names, self.rules = technologies, names, rules
        self.graph = Graph(rules['limits'], cancelled)
        self.library = Library(reader, {'technologies': list(technologies.values()), **(records or {})})
        compiler = Compiler(self.graph, names, rules)
        compiler.objects = References(compiler, self.library)
        if rules.get('acquisition', {}).get('revision'):
            from sttv.enrichment.acquisition.analysis import Acquisition
            compiler.acquisition = Acquisition(compiler, self.library, rules['acquisition'], reader=reader)
        self.compiler, self.roots = compiler, {}
        for key, tech in sorted(technologies.items()):
            if cancelled is not None and cancelled():
                raise BuildError('cancelled', 'DLC graph preparation cancelled')
            self.roots[key] = self.technology(tech)
        if compiler.acquisition:
            compiler.acquisition.prepare()
        self.build_seconds = perf_counter() - start
        self.result, self.values = None, None

    def technology(self, tech):
        compiler, rules = self.compiler, self.rules
        path = tech['source']['pointer'] + '/value'
        sections = []
        potentials = [compiler.compile(block, pointer) for block, pointer in entries(tech['body'], rules['potential_field'], path)]
        potential = self.graph.add('AND', potentials, pointer=path)
        sections.extend(('potential', node) for node in potentials)
        weights = []
        for body, pointer in entries(tech['body'], rules['weight_field'], path):
            if unsupported_weight(body, rules):
                sections.append(('unsupported_weight', compiler.unknown(body, pointer, 'country', 'unsupported_weight_action')))
                continue
            for modifier, target in entries(body, rules['modifier_field'], pointer):
                factors = entries(modifier, rules['factor_field'], target)
                if len(factors) != 1 or number(factors[0][0].get('text')) != 0:
                    continue
                from .controls import compile_block
                node = compile_block(compiler, modifier, target, 'country', 0, ignored=(rules['factor_field'],))
                sections.append(('zero_weight_modifier', node))
                weights.append(node)
        return {'potential': potential, 'weights': weights, 'sections': sections,
                'source': tech['source'], 'variant': tech.get('variant', 'base')}

    def evaluate(self, enabled):
        start = perf_counter()
        unknown = set(enabled) - self.names.keys()
        if unknown:
            raise BuildError('unknown_dlc', f'Unknown DLC identifiers: {sorted(unknown)}')
        values = self.graph.evaluate(enabled)
        baseline, outcomes = self.graph.baseline, {}
        for key, roots in self.roots.items():
            reasons, p = [], roots['potential']
            if values[p] is False and baseline[p] is not False:
                from .coverage import indirect
                code = 'dlc_indirect_potential' if indirect(self.graph.nodes, p) else 'dlc_potential'
                reasons.append({'code': code, 'pointer': self.graph.nodes[p]['pointer']})
            for node in roots['weights']:
                if values[node] is True and baseline[node] is not True:
                    reasons.append({'code': 'dlc_zero_weight', 'pointer': self.graph.nodes[node]['pointer']})
            traces = [{'section': section, **self.graph.trace(node, values)} for section, node in roots['sections']]
            outcomes[key] = {'visible': not reasons, 'reasons': reasons, 'evidence': traces}
        self.result, self.values = outcomes, values
        self.graph.statistics['evaluation_seconds'] = perf_counter() - start
        return outcomes, list(self.graph.diagnostics)

    def report(self):
        from .coverage import coverage
        return {'context': self.rules['context'], 'acquisition': self.compiler.acquisition.report() if self.compiler.acquisition else None,
                'statistics': {**self.graph.statistics,
                    'build_seconds': self.build_seconds, 'read_documents': len(self.library.loaded)},
                'roots': self.roots, 'nodes': self.graph.evidence(self.values),
                'coverage': coverage(self), 'diagnostics': self.graph.diagnostics}
