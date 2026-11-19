"""Three-valued evaluation limited to explicitly supplied empire facts."""


def conjunction(values):
    return False if False in values else None if None in values else True


def disjunction(values):
    return True if True in values else None if None in values else False


def negate(value):
    return None if value is None else not value


def evaluate(node, facts, scope='country', evidence=None):
    evidence = [] if evidence is None else evidence
    kind = node['kind']
    if kind == 'block':
        return conjunction([evaluate(n, facts, scope, evidence) for n in node['items']])
    if kind == 'logical_operation':
        values = [evaluate(n, facts, scope, evidence) for n in node['body']['items']]
        operator = node['operator']
        if operator in ('AND', 'NAND'):
            result = conjunction(values)
            return negate(result) if operator == 'NAND' else result
        if operator in ('OR', 'NOR'):
            result = disjunction(values)
            return negate(result) if operator == 'NOR' else result
        if operator == 'NOT' and values and None not in values and len(set(values)) == 1:
            return not values[0]
        return None
    if kind != 'assignment' or node['operator'] != '=':
        return None
    key, value = node['key']['text'], node['value']
    if value['kind'] == 'block':
        if scope == 'country' and key == 'founder_species':
            return evaluate(value, facts, 'founder_species', evidence)
        return None
    if value['kind'] != 'scalar':
        return None
    result = facts.get(scope, {}).get(key, {}).get(value['text'])
    if result is not None:
        evidence.append({'scope': scope, 'predicate': key, 'value': value['text'], 'result': result})
    return result


def availability(technology, facts):
    evidence = []
    result = conjunction([evaluate(n, facts, evidence=evidence) for n in technology['potential']])
    return {'value': result, 'known_predicates': evidence, 'source': technology['source']}
