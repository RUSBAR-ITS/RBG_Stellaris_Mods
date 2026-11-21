"""Ordered candidate elimination with immediate reciprocal child attachment."""

import re

from .empire import compatible
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
        found, witnesses = compatible(technology, current, technologies, facts)
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
