"""Presentation fields for visible base technologies, separate from stored tree nodes."""

from ..localization import determine_key
from .ast import fields, number, references, scalar
from .inputs import records


def catalog(db, rules):
    result = {}
    keys = ['area', 'tier', 'category', 'cost', 'weight', 'levels', 'start_tech', 'is_rare', 'is_dangerous', 'icon']
    for row in records(db, 'technologies', keys):
        body, key = row['body'], row['id']
        def numeric(name):
            values = fields(body, name)
            if len(values) != 1:
                return None
            value = values[0]
            text = scalar(value, 'factor') if name == 'cost' and value['kind'] == 'block' else value.get('text')
            parsed = number(text)
            return float(parsed) if parsed is not None else None
        result[key] = {'tier': int(scalar(body, 'tier')), 'cost': numeric('cost'), 'weight': numeric('weight'),
                       'levels': numeric('levels'), 'rare': scalar(body, 'is_rare') == 'yes',
                       'dangerous': scalar(body, 'is_dangerous') == 'yes', 'starting': scalar(body, 'start_tech') == 'yes',
                       'categories': sorted({determine_key(rules, 'research_category', k)
                                             for block in fields(body, 'category') for k in references(block)}),
                       'icon': scalar(body, 'icon', key), 'source': row['source'],
                       'name': determine_key(rules, 'technology_name', key),
                       'description': determine_key(rules, 'technology_description', key)}
    return result
