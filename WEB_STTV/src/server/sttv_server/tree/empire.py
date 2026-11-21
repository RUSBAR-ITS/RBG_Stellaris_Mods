"""Compare candidate conditions with all viable interpretations of the child's potential."""

from .graph import conjunction, disjunction, invert


def expression(node, scope, config, dlc_value, atoms):
    """Build a boolean expression while keeping unsupported game state unknown."""
    proven = dlc_value(node, scope)
    if proven is not None:
        return ('constant', proven)
    kind = node.get('kind')
    if kind in ('block', 'logical_operation'):
        op = node.get('operator', 'AND')
        items = node.get('body', node).get('items', [])
        if op in ('AND', 'OR', 'NOR', 'NAND') or op == 'NOT' and len(items) == 1:
            return op, [expression(n, scope, config, dlc_value, atoms) for n in items]
    if kind == 'scripted_trigger_test' and node.get('operator') == '=':
        test = node.get('value', {}).get('text')
        if test in ('yes', 'no'):
            return ('AND' if test == 'yes' else 'NOT'), [expression(node['body'], scope, config, dlc_value, atoms)]
    if kind == 'assignment' and node.get('operator') == '=':
        key, value = node['key']['text'], node['value']
        if value['kind'] == 'block':
            if key in config['dlc']['wrappers']:
                inner = [n for n in value['items'] if n.get('key', {}).get('text') not in config['dlc']['ignored_wrapper_fields']]
                return 'AND', [expression(n, scope, config, dlc_value, atoms) for n in inner]
            if scope == 'country' and key in ('founder_species', 'federation'):
                return expression(value, key, config, dlc_value, atoms)
        text = value.get('text')
        if text is not None and (key in config['empire_predicates'] or key in config['reference_facts'].get(scope, {})):
            atom = scope, key, 'yes' if text == 'no' else text
            atoms.add(atom)
            return ('NOT', [('atom', atom)]) if text == 'no' else ('atom', atom)
    return 'constant', None


def evaluate(expr, values):
    op, arg = expr
    if op == 'constant':
        return arg
    if op == 'atom':
        return values.get(arg)
    outcomes = [evaluate(n, values) for n in arg]
    value = disjunction(outcomes) if op in ('OR', 'NOR') else conjunction(outcomes)
    return invert(value) if op in ('NOT', 'NOR', 'NAND') else value


def compatible(child, current, technologies, context):
    config, dlc_value = context
    def condition(tech, atoms):
        return 'AND', [expression(n, 'country', config, dlc_value, atoms) for n in tech['potential']]
    atoms = set()
    child_expr = condition(child, atoms)
    variables = sorted(atoms)
    parents = {key: condition(technologies[key], set()) for key in current}
    defaults = {(scope, key, text): value for scope, checks in config['reference_facts'].items()
                for key, entries in checks.items() for text, value in entries.items() if text != 'no'}
    exclusive = set(config['exclusive_predicates'])
    found, branches = set(), []
    pending = [{}]
    while pending:
        assigned = pending.pop()
        if evaluate(child_expr, assigned) is False:
            continue
        positives = [a[:2] for a, value in assigned.items() if value and a[1] in exclusive]
        if len(positives) != len(set(positives)):
            continue
        if len(assigned) < len(variables):
            atom = variables[len(assigned)]
            pending.extend(({**assigned, atom: True}, {**assigned, atom: False}))
            continue
        facts = {**defaults, **assigned}
        # A selected value of a single-valued characteristic excludes its siblings.
        for scope, key in positives:
            for parent in current:
                for atom in context_atoms(parents[parent]):
                    if atom[:2] == (scope, key) and atom not in assigned:
                        facts[atom] = False
        if evaluate(child_expr, facts) is False:
            continue
        matches = [key for key, expr in parents.items() if evaluate(expr, facts) is not False]
        found.update(matches)
        branches.append({'facts': [(*a, v) for a, v in facts.items()], 'matches': matches})
        if len(found) == len(current):
            break
    return [key for key in current if key in found], branches


def context_atoms(expr):
    op, arg = expr
    if op == 'atom':
        yield arg
    elif op != 'constant':
        for term in arg:
            yield from context_atoms(term)
