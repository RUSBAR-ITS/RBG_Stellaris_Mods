"""Compile DLC gates once for each input revision."""
from .ast import number
from .graph import Graph
from .objects import References
from .conditions import Compiler


def entries(body, key, pointer):
    return [(node['value'], f"{pointer}/items/{node.get('source_index', i)}/value") for i, node in enumerate(body.get('items', []))
            if node.get('kind') == 'assignment' and node['key']['text'] == key and node['operator'] == '=']


def unsupported_weight(node, rules):
    if node.get('key', {}).get('text') in rules['unsupported_actions']:
        return True
    return any(unsupported_weight(value, rules) for value in node.values() if isinstance(value, dict)) or any(
        unsupported_weight(child, rules) for value in node.values() if isinstance(value, list)
        for child in value if isinstance(child, dict))


class Analysis:
    def __init__(self, technologies, names, rules, catalog):
        self.graph = Graph(rules['limits'])
        self.rules = rules
        self.compiler = Compiler(self.graph, names, rules)
        self.compiler.objects = References(self.compiler, catalog)
        self.roots = {key: self.technology(tech) for key, tech in technologies.items()}

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
