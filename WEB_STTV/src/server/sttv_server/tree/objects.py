"""Resolve scoped DLC gates from the published game catalogs."""
from .ast import scalar


class References:
    def __init__(self, compiler, library):
        self.compiler, self.library = compiler, library
        self.graph, self.rules = compiler.graph, compiler.rules
        self.cache, self.active = {}, set()

    def reference(self, rule, identifier, context, depth):
        target = self.availability(rule, identifier, context, depth)
        return self.graph.add('presence', [target], rule=rule['id'], context=context)

    def availability(self, rule, identifier, context, depth):
        identity = rule['id'], identifier, context, rule['purpose'], 'base'
        if identity in self.cache:
            if identity in self.active:
                self.graph.diagnostics.append({'code': 'dlc_dependency_cycle', 'node_id': self.cache[identity]})
            return self.cache[identity]
        if len(self.active) >= self.graph.limits['max_depth']:
            return self.graph.unknown('dlc_depth_limit', target=identifier, rule=rule['id'])
        record = self.library.resolve(rule['database'], identifier)
        if record is None:
            return self.graph.unknown('missing_dlc_reference', database=rule['database'], target=identifier, rule=rule['id'])
        selector = rule.get('selector')
        if selector and scalar(record['body'], selector['field'], selector['default']) != selector['value']:
            return self.graph.unknown('dlc_reference_type', target=identifier, rule=rule['id'])
        node = self.graph.add('AND', object_ref=record['source'], object_id=identifier,
                              rule=rule['id'], context=context, purpose=rule['purpose'], variant='base',
                              source_basis=rule['source'], diagnostic_code=rule['diagnostic_code'])
        if node == 'node_limit':
            return node
        self.cache[identity] = node
        self.active.add(identity)
        try:
            children = self.gates(record, rule)
            if rule['handler'] in ('ship_category', 'tradition'):
                children.append(self.providers(rule, identifier, context, depth))
            if rule['handler'] == 'observe':
                children.append(self.graph.unknown('unconfirmed_object_availability', rule=rule['id'],
                                                   object_ref=record['source']))
                self.compiler.observe(record['body'], record['source']['pointer'] + '/value', context, node)
            self.graph.nodes[node]['children'] = children
        finally:
            self.active.remove(identity)
        return node

    def gates(self, record, rule):
        children, pointer = [], record['source']['pointer'] + '/value'
        gates = {gate['field']: gate for gate in rule['gates']}
        for i, item in enumerate(record['body'].get('items', [])):
            key = item.get('key', {}).get('text')
            if key not in gates:
                continue
            path, gate = f"{pointer}/items/{item.get('source_index', i)}/value", gates[key]
            value = item.get('value', {})
            if value.get('kind') == 'scalar' and value.get('text') in ('yes', 'no'):
                child = self.graph.add('constant', constant=value['text'] == 'yes', pointer=path)
            elif value.get('kind') == 'block':
                child = self.compiler.compile(value, path, gate['context'])
            else:
                child = self.graph.unknown('unsupported_availability_gate', pointer=path, rule=rule['id'])
            children.append(child)
        return children

    def providers(self, rule, identifier, context, depth):
        relation = rule['providers']
        provider_rule = next(r for r in self.rules['rules'] if r['id'] == relation['rule'])
        from .providers import index
        providers, complete = index(self.library, relation, provider_rule['database'])
        rows = providers.get(identifier, [])
        children = [self.availability(provider_rule, key, context, depth + 1) for key in sorted(rows)]
        if not rows or not complete:
            children.append(self.graph.unknown('incomplete_provider_domain', target=identifier, rule=rule['id']))
        return self.graph.add('OR', children, relation=relation, target=identifier, context=context)
