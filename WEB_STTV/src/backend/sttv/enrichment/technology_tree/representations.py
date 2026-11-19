"""Effective analytical representations, without changing original technology nodes."""

from sttv.common.errors import BuildError
from .ast import fields, scalar, references, prerequisite, requirements, numeric_items


def prepare(records, selected):
    technologies = {}
    for record in records:
        body, key = record['body'], record['id']
        if not fields(body, 'tier'):
            continue
        if key in technologies:
            raise BuildError('duplicate_technology', f'Duplicate technology: {key}')
        choice = selected.get(key, 'base')
        swaps = fields(body, 'technology_swap')
        try:
            variant = None if choice == 'base' else swaps[int(choice.split(':')[1]) - 1]
            if choice != 'base' and (not choice.startswith('swap:') or int(choice.split(':')[1]) < 1):
                raise ValueError(choice)
        except (ValueError, IndexError, AttributeError):
            raise BuildError('invalid_variant', f'{key}: unknown representation {choice}') from None
        req = prerequisite(body)
        parents, mandatory, _ = requirements(req)
        try:
            tier = int(scalar(body, 'tier'))
        except (ValueError, TypeError):
            raise BuildError('invalid_tier', f'{key}: expected integer tier') from None
        area = scalar(variant, 'area', scalar(body, 'area')) if variant else scalar(body, 'area')
        category_nodes = fields(variant, 'category') if variant else []
        category = sorted(set().union(*(references(n) for n in (category_nodes or fields(body, 'category')))))
        inheritance = scalar(variant, 'inherit_effects') if variant else 'yes'
        if inheritance not in ('yes', 'no', None):
            raise BuildError('invalid_inheritance', f'{key}: invalid inherit_effects')
        effects = fields(body, 'modifier') if variant is None or inheritance == 'yes' else []
        if variant:
            effects = [*effects, *fields(variant, 'modifier')]
        numbers, conflict = {}, False
        for block in effects:
            for modifier, value in numeric_items(block):
                conflict |= modifier in numbers and numbers[modifier] != value
                numbers[modifier] = value
        technologies[key] = {**record, 'tier': tier, 'area': area, 'category': category,
            'variant': choice, 'variant_condition': fields(variant, 'trigger') if variant else [],
            'potential': fields(body, 'potential'), 'prerequisites': req,
            'parents': sorted(parents), 'mandatory': sorted(mandatory),
            'effects': effects, 'bonuses': numbers,
            'effects_unknown': 'variant_effects_unknown' if inheritance is None else
                               'conflicting_effects' if conflict else None}
    unknown = set(selected) - technologies.keys()
    if unknown:
        raise BuildError('invalid_variant', f'Unknown technology selections: {sorted(unknown)}')
    for key, tech in technologies.items():
        missing = set(tech['parents']) - technologies.keys()
        if missing:
            raise BuildError('missing_prerequisite', f'{key}: missing prerequisites {sorted(missing)}')
    return technologies
