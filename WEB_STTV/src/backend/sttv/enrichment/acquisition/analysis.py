"""Prove only unattainability; attainable technologies never imply present ownership."""

from sttv.enrichment.technology_tree.ast import fields, scalar, number
from .network import Network


class Acquisition:
    def __init__(self, compiler, library, options, *, reader=None, records=None, coverage=None):
        self.compiler, self.graph, self.library, self.options = compiler, compiler.graph, library, options
        self.cache, self.level_cache, self.active = {}, {}, set()
        self.index = None
        if reader is not None:
            from .storage import Index
            self.index = Index(reader, options)
            records, coverage = self.index.relevant(compiler.graph.cancelled), self.index.manifest['coverage']
        self.network = Network(compiler, options, records or [], coverage or {'parsed': False})
        self.ready = False

    def prepare(self):
        from .closure import select
        self.network.records, self.prepared_targets = select(self.network.records, self.cache, self.level_cache,
                                                            self.library, self.options)
        self.network.compile()
        self.ready = True
        # Entry conditions may have allocated forward references while compiling the network.
        for target in list(self.cache):
            self.fill(target)
        for target, node in self.level_cache.items():
            self.graph.nodes[node]['children'] = self.level_children(target)

    def level_children(self, target):
        children = list(self.network.levels.get(target, []))
        if not children:
            children.append(self.graph.unknown('acquisition_missing_crisis_level', target=target))
        if not self.network.coverage.get('parsed'):
            children.append(self.graph.unknown('acquisition_incomplete_sources', target=target, coverage_ref='acquisition.coverage'))
        return children

    def crisis(self, target):
        if target not in self.level_cache:
            self.level_cache[target] = self.graph.add('OR', object_id=target, purpose='crisis_acquisition')
            if self.ready:
                self.graph.nodes[self.level_cache[target]]['children'] = self.level_children(target)
        return self.graph.add('presence', [self.level_cache[target]])

    def reference(self, target):
        if target not in self.cache:
            self.cache[target] = self.graph.add('OR', object_id=target, purpose='technology_acquisition')
            if self.ready:
                self.fill(target)
        return self.graph.add('presence', [self.cache[target]])

    def prerequisite(self, node):
        kind = node.get('kind')
        if kind == 'scalar':
            return self.reference(node['text'])
        if kind == 'block':
            return self.graph.add('AND', [self.prerequisite(n) for n in node['items']])
        if kind == 'logical_operation' and node['operator'] in ('AND', 'OR'):
            return self.graph.add(node['operator'], [self.prerequisite(n) for n in node['body']['items']])
        return self.graph.unknown('acquisition_prerequisite_unsupported')

    def ordinary(self, tech, starting=False):
        body, path = tech['body'], tech['source']['pointer'] + '/value'
        constraints = [self.compiler.compile(b, path + '/potential') for b in fields(body, 'potential')]
        if starting:
            constraints.extend(self.compiler.compile(b, path + '/starting_potential') for b in fields(body, 'starting_potential'))
            constraints.append(self.graph.unknown('acquisition_starting_state', target=tech['id']))
        else:
            constraints.extend(self.prerequisite(b) for b in fields(body, 'prerequisites'))
            weight = number(scalar(body, 'weight'))
            modifiers = fields(body, 'weight_modifier')
            # An additive or unknown modifier may turn an initial zero into a positive weight.
            from sttv.enrichment.dlc.analysis import unsupported_weight
            uncertain = any(unsupported_weight(b, self.compiler.rules) for b in modifiers)
            constraints.append(self.graph.unknown('acquisition_weight_unknown', target=tech['id']) if uncertain or weight is None
                               else self.graph.add('constant', constant=weight > 0))
            if not uncertain:
                from sttv.enrichment.dlc.controls import compile_block
                for block in modifiers:
                    for modifier in fields(block, 'modifier'):
                        if number(scalar(modifier, 'factor')) == 0:
                            guard = compile_block(self.compiler, modifier, path + '/weight_modifier', 'country', 0, ignored=('factor',))
                            constraints.append(self.graph.add('NOT', [guard]))
        return self.graph.add('AND', constraints, route='starting' if starting else 'ordinary', target=tech['id'])

    def fill(self, target):
        if target in self.active:
            return
        self.active.add(target)
        root = self.cache[target]
        tech = self.library.get('technologies', target)
        if tech is None:
            self.graph.nodes[root]['children'] = [self.graph.unknown('acquisition_missing_technology', target=target)]
            return
        self.graph.nodes[root]['object_ref'] = tech['source']
        children = [self.ordinary(tech)]
        if target not in self.prepared_targets:
            children.append(self.graph.unknown('acquisition_target_outside_closure', target=target))
        if scalar(tech['body'], 'start_tech') == 'yes':
            children.append(self.ordinary(tech, starting=True))
        for route in self.network.routes:
            if route['target'] not in (target, '*') or not self.compatible(route, tech):
                continue
            constraints = [route['guard']]
            handler = route['handler']
            if handler in ('copy_random', 'copy_all'):
                # Copy filters are necessary, not sufficient; donor ownership is unknown.
                constraints.append(self.copy_gate(tech, handler))
            if handler not in ('grant', 'option') or route['target'] == '*' or route['recipient'] != 'recipient':
                constraints.append(self.graph.unknown('acquisition_route_uncertain', target=target,
                    mechanism=handler, recipient=route['recipient'], source=route['source'], pointer=route['pointer']))
            children.append(self.graph.add('AND', constraints, **{k: v for k, v in route.items() if k not in ('guard', 'arguments')}))
        if not self.network.coverage.get('parsed'):
            children.append(self.graph.unknown('acquisition_incomplete_sources', target=target,
                                              coverage_ref='acquisition.coverage'))
        children.extend(self.network.gaps)
        self.graph.nodes[root]['children'] = children

    def copy_gate(self, tech, handler):
        # Do not inherit ordinary prerequisite ownership into a direct copy.
        body = dict(tech['body'])
        body['items'] = [n for n in body['items'] if n.get('key', {}).get('text') != 'prerequisites']
        if handler == 'copy_all':
            body['items'] = [n for n in body['items'] if n.get('key', {}).get('text') != 'potential']
        return self.ordinary({**tech, 'body': body})

    def compatible(self, route, tech):
        if route['target'] != '*':
            return True
        if route['handler'] == 'copy_all':
            excluded = {n.get('text') for block in fields(route['arguments'], 'except') for n in block.get('items', [])}
            if tech['id'] in excluded:
                return False
        if route['handler'] == 'random':
            # Documented defaults of add_random_research_option, not a guessed weight filter.
            rare = scalar(tech['body'], 'is_rare', 'no') == 'yes'
            if rare and scalar(route['arguments'], 'ignore_rare', 'yes') == 'yes':
                return False
            if not rare and scalar(route['arguments'], 'only_rare', 'no') == 'yes':
                return False
            if scalar(tech['body'], 'is_insight', 'no') == 'yes' and scalar(route['arguments'], 'ignore_insight', 'yes') == 'yes':
                return False
        for field in self.options['effects']['domain_fields']:
            value = scalar(route['arguments'], field)
            if value is None or '$' in value or '@' in value:
                continue
            if field == 'category':
                categories = [n.get('text') for b in fields(tech['body'], field) for n in b.get('items', [])]
                if categories and value not in categories:
                    return False
            elif field == 'area' and scalar(tech['body'], field) not in (value, None):
                return False
            # Tier selection semantics are not inferred from an equality-looking field.
        return True

    def report(self):
        values, baseline = (self.graph.last[1], self.graph.baseline) if self.graph.last else ({}, {})
        return {'technology_roots': self.cache, 'crisis_roots': self.level_cache,
                'states': {target: {'possible_acquisition': values.get(root),
                    'current_ownership': False if values.get(root) is False else None,
                    'dlc_exclusion_proven': values.get(root) is False and baseline.get(root) is not False}
                    for target, root in self.cache.items()},
                'routes': self.network.routes, 'coverage': self.network.coverage,
                'read_documents': len(self.index.loaded) if self.index else 0}
