"""Ordered candidate elimination with immediate reciprocal child attachment."""

import re

from .conditions import availability
from .economy import matches as bonus_matches


def criterion(rule, technology, current, technologies, evidence, facts):
    key, witnesses, reason = rule['id'], [], None
    if key == 'normalized_id':
        normalized = re.sub('[0-9]', '', technology['id'])
        found = [p for p in current if re.sub('[0-9]', '', p) == normalized]
    elif key == 'same_area':
        if any(t['area'] is None for t in [technology, *(technologies[p] for p in current)]):
            return [], [], 'unknown_area'
        found = [p for p in current if technology['area'] is not None and technologies[p]['area'] == technology['area']]
    elif key == 'same_category':
        found = [p for p in current if set(technologies[p]['category']) & set(technology['category'])]
    elif key == 'mandatory':
        found = [p for p in current if p in technology['mandatory']]
    elif key == 'same_potential':
        nonempty = any(n.get('items') for n in technology['potential'])
        found = [p for p in current if nonempty and technologies[p]['potential'] == technology['potential']]
    elif key == 'standard_empire':
        values = {p: availability(technologies[p], facts) for p in current}
        witnesses = [{'candidate': p, **value} for p, value in values.items()]
        found = [p for p in current if values[p]['value'] is not False]
    elif key == 'highest_tier':
        tier = max(technologies[p]['tier'] for p in current)
        found = [p for p in current if technologies[p]['tier'] == tier]
    elif key == 'functional_groups':
        own = evidence.groups.get(technology['id'], [])
        own_groups = {w['group'] for w in own}
        for parent in current:
            shared = own_groups & {w['group'] for w in evidence.groups.get(parent, [])}
            if shared:
                witnesses.append({'parent': parent, 'groups': sorted(shared),
                    'child': [w for w in own if w['group'] in shared],
                    'candidate': [w for w in evidence.groups[parent] if w['group'] in shared]})
        found = [w['parent'] for w in witnesses]
    else:
        if key in ('production_affinity', 'capacity_affinity'):
            reason = technology['effects_unknown']
            index = evidence.production if key == 'production_affinity' else evidence.capacity
            witnesses = [] if reason else bonus_matches(technology, current, index)
        else:
            witnesses = [w for w in evidence.witnesses.get(key, {}).get(technology['id'], []) if w['parent'] in current]
        found = sorted({w['parent'] for w in witnesses})
    return found, witnesses, reason


def calculate(technologies, evidence, rules, facts, *, order=None):
    results = {key: {'parent_tech': None, 'children': [], 'status': 'root'} for key in technologies}
    decisions, diagnostics = [], []
    for key in sorted(technologies) if order is None else order:
        tech = technologies[key]
        current, trace = tech['parents'].copy(), []
        for rule in rules['rules']:
            if len(current) <= 1:
                break
            if not rule['enabled']:
                continue
            found, witnesses, reason = criterion(rule, tech, current, technologies, evidence, facts)
            after = found if found and reason is None else current.copy()
            trace.append({'rule': rule['id'], 'before': current, 'matches': found, 'after': after,
                          'skip_reason': reason or ('empty_matches' if not found else None), 'evidence': witnesses})
            if reason:
                diagnostics.append({'code': reason, 'technology': key, 'variant': tech['variant'], 'rule': rule['id']})
            current = after
        status = 'root' if not current else 'resolved' if len(current) == 1 else 'ambiguous'
        parent = current[0] if status == 'resolved' else None
        results[key].update(parent_tech=parent, status=status)
        if parent is not None and key not in results[parent]['children']:
            results[parent]['children'].append(key)
        decisions.append({'id': key, 'variant': tech['variant'], 'area': tech['area'], 'tier': tech['tier'],
            'category': tech['category'], 'source': tech['source'], 'candidates': tech['parents'],
            'mandatory': tech['mandatory'], 'prerequisites': tech['prerequisites'], 'remaining': current,
            'variant_condition': tech['variant_condition'], 'status': status, 'parent_tech': parent, 'trace': trace})
        if status == 'ambiguous':
            diagnostics.append({'code': 'ambiguous_parent', 'technology': key, 'candidates': current})
    for result in results.values():
        result['children'].sort()
    return results, sorted(decisions, key=lambda r: r['id']), diagnostics
