"""Compile only declared condition semantics, retaining the scope of every node."""

from .controls import compile_block, compile_count


class Compiler:
    def __init__(self, graph, names, rules, objects=None):
        self.graph, self.rules, self.objects = graph, rules, objects
        self.compiled = {}
        self.names = {name: identifier for identifier, name in names.items()}
        self.routes = {p: r for r in rules.get('rules', []) if r['enabled'] for p in r['predicates']}

    def unknown(self, node, pointer, context, code='unknown_dlc_condition', **details):
        key = self.graph.unknown(code, pointer=pointer, context=context,
                                 predicate=node.get('key', {}).get('text', node.get('kind')), **details)
        self.observe(node, pointer, context, key)
        return key

    def observe(self, node, pointer, context, owner):
        """Inventory unsupported subtrees without lifting their conditions into proofs."""
        stack = [(node, pointer)]
        observations = []
        while stack:
            item, path = stack.pop()
            predicate, value = item.get('key', {}).get('text'), item.get('value', {})
            if predicate in self.rules['predicates']:
                observations.append({'pointer': path, 'dlc_id': self.names.get(value.get('text')),
                                     'name': value.get('text'), 'reason': 'unsupported_context'})
            if predicate in self.routes:
                observations.append({'pointer': path, 'predicate': predicate, 'target': value.get('text'),
                                     'reason': 'unsupported_context'})
            for field in ('value', 'body', 'block'):
                child = item.get(field)
                if isinstance(child, dict):
                    stack.append((child, path + '/' + field))
            stack.extend((child, f'{path}/items/{i}') for i, child in enumerate(item.get('items', [])))
        if observations:
            self.graph.nodes[owner]['observations'] = observations

    def compile(self, node, pointer, context='country', depth=0):
        result = self._compile(node, pointer, context, depth)
        self.compiled[id(node), context] = result
        return result

    def _compile(self, node, pointer, context, depth):
        if len(self.graph.nodes) >= self.graph.limits['max_nodes']:
            return self.graph.add('unknown')
        if depth > self.graph.limits['max_depth']:
            return self.unknown(node, pointer, context, 'dlc_depth_limit')
        meta = {'pointer': pointer, 'context': context}
        kind = node.get('kind')
        if kind == 'block':
            return compile_block(self, node, pointer, context, depth)
        if kind == 'logical_operation' and node.get('body', {}).get('kind') == 'block':
            operator, items = node['operator'], node['body']['items']
            if operator not in ('AND', 'OR', 'NAND', 'NOR') and not (operator == 'NOT' and len(items) == 1):
                return self.unknown(node, pointer, context, 'unsupported_dlc_logic')
            children = [self.compile(n, f'{pointer}/body/items/{i}', context, depth + 1)
                        for i, n in enumerate(items)]
            return self.graph.add(operator, children, **meta)
        if kind == 'scripted_trigger_test' and node.get('operator') == '=':
            text = node.get('value', {}).get('text')
            if text in ('yes', 'no'):
                child = self.compile(node['body'], pointer + '/body', context, depth + 1)
                return self.graph.add('AND' if text == 'yes' else 'NOT', [child], **meta)
        if kind != 'assignment' or node.get('operator') != '=':
            return self.unknown(node, pointer, context, 'unsupported_dlc_node')
        key, value = node['key']['text'], node['value']
        text = value.get('text')
        meta['predicate'] = key
        if key in self.rules['predicates'] and value.get('kind') == 'scalar':
            identifier = self.names.get(text)
            if identifier is None:
                return self.unknown(node, pointer, context, 'unknown_dlc_name', name=text)
            return self.graph.add('dlc', dlc_id=identifier, name=text, **meta)
        if key in self.rules['constants'] and text in self.rules['constants'][key]:
            return self.graph.add('constant', constant=self.rules['constants'][key][text], **meta)
        if key in self.rules['acquisition_predicates'] and context == 'country' and text:
            return self.unknown(node, pointer, context, 'acquisition_incomplete_sources', target=text)
        if key in self.rules['wrappers'] and value.get('kind') == 'block':
            return compile_block(self, value, pointer + '/value', context, depth + 1,
                                 ignored=self.rules['ignored_wrapper_fields'])
        if key == 'calc_true_if' and context != 'government' and value.get('kind') == 'block':
            return compile_count(self, value, pointer + '/value', context, depth + 1)
        if context == 'government':
            target = self.rules.get('government_requirements', {}).get(key)
            if target and value.get('kind') == 'block':
                return self.government(value, pointer + '/value', target, depth + 1)
        route = self.routes.get(key)
        if route and self.objects:
            if context not in route['contexts'] or value.get('kind') != 'scalar':
                return self.unknown(node, pointer, context, 'unsupported_reference_context')
            if route['handler'] == 'technology':
                return self.unknown(node, pointer, context, 'acquisition_incomplete_sources', target=text)
            child = self.objects.reference(route, text, context, depth + 1)
            return self.graph.add('AND', [child], rule=route['id'], **meta)
        scope = self.rules.get('scopes', {}).get(key)
        if scope and context in scope['from'] and value.get('kind') == 'block':
            child = self.compile(value, pointer + '/value', scope['to'], depth + 1)
            # A possible scoped object is not proof of its actual existence.
            return self.graph.add('presence', [child], **meta)
        return self.unknown(node, pointer, context)

    def government(self, node, pointer, predicate, depth):
        if depth > self.graph.limits['max_depth']:
            return self.unknown(node, pointer, 'government', 'dlc_depth_limit')
        kind = node.get('kind')
        if kind == 'block':
            children = [self.government(n, f'{pointer}/items/{i}', predicate, depth + 1)
                        for i, n in enumerate(node['items']) if n.get('key', {}).get('text') != 'text']
            return self.graph.add('AND', children, pointer=pointer, context='government')
        if kind == 'logical_operation':
            items, op = node['body']['items'], node['operator']
            items = [(i, n) for i, n in enumerate(items) if n.get('key', {}).get('text') != 'text']
            if op in ('AND', 'OR', 'NOR', 'NAND') or op == 'NOT' and len(items) == 1:
                children = [self.government(n, f'{pointer}/body/items/{i}', predicate, depth + 1) for i, n in items]
                return self.graph.add(op, children, pointer=pointer, context='government')
        if kind == 'assignment' and node['key']['text'] == 'value' and node['operator'] == '=':
            translated = {**node, 'key': {'kind': 'scalar', 'text': predicate}}
            return self.compile(translated, pointer, 'government', depth + 1)
        return self.unknown(node, pointer, 'government', 'unsupported_requirement')
