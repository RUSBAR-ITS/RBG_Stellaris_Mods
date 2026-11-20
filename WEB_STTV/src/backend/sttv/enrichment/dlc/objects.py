"""Resolve references from the manifest; project each necessary document once."""

from sttv.common.errors import BuildError
from sttv.enrichment.technology_tree.ast import scalar
from sttv.enrichment.technology_tree.inputs import record_for


class Library:
    def __init__(self, reader=None, records=None):
        self.reader, self.records = reader, {}
        self.loaded, self.complete, self.providers = set(), set(), {}
        for kind, rows in (records or {}).items():
            for row in rows:
                self.insert(kind, row)
            self.complete.add(kind)

    def insert(self, kind, record):
        key = kind, record['id']
        if key in self.records and self.records[key]['source'] != record['source']:
            raise BuildError('ambiguous_object', f'Duplicate DLC dependency: {kind}/{record["id"]}')
        self.records[key] = record

    def document(self, kind, identifier):
        if (kind, identifier) in self.loaded:
            return
        rows = self.reader.project(kind, identifier, lambda p, n: record_for(kind, identifier, p, n),
                                   cache_key='dlc_compact')
        for row in rows:
            self.insert(kind, row)
        self.loaded.add((kind, identifier))

    def get(self, kind, identifier):
        if self.reader is not None:
            refs = self.reader.resolve_object(kind, identifier)
            if len(refs) > 1:
                raise BuildError('ambiguous_object', f'Duplicate DLC dependency: {kind}/{identifier}')
            if (kind, identifier) not in self.records:
                for ref in refs:
                    self.document(kind, ref['document_id'])
        return self.records.get((kind, identifier))

    def all(self, kind):
        if self.reader is not None and kind not in self.complete:
            for identifier in self.reader.document_ids(kind):
                self.document(kind, identifier)
            self.complete.add(kind)
        return [row for (database, _), row in sorted(self.records.items()) if database == kind]


class References:
    def __init__(self, compiler, library):
        self.compiler, self.library = compiler, library
        self.graph, self.rules = compiler.graph, compiler.rules
        self.cache, self.active = {}, set()

    def reference(self, rule, identifier, context, depth):
        if rule['handler'] == 'technology':
            if self.compiler.acquisition is None:
                return self.graph.unknown('acquisition_not_prepared', target=identifier)
            return self.compiler.acquisition.reference(identifier)
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
        record = self.library.get(rule['database'], identifier)
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
            path, gate = f'{pointer}/items/{i}/value', gates[key]
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
