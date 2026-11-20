"""Complete reverse indexes for explicit ship providers and tradition membership."""

from collections import defaultdict


def index(library, relation, database):
    key = database, tuple(relation['fields'])
    if key in library.providers:
        return library.providers[key]
    providers, valid = defaultdict(set), True
    for record in library.all(database):
        for item in record['body'].get('items', []):
            if item.get('key', {}).get('text') not in relation['fields']:
                continue
            value = item.get('value', {})
            if item.get('operator') != '=':
                valid = False
            elif value.get('kind') == 'scalar':
                providers[value['text']].add(record['id'])
            elif value.get('kind') == 'block' and all(n.get('kind') == 'scalar' for n in value['items']):
                for n in value['items']:
                    providers[n['text']].add(record['id'])
            else:
                valid = False
    result = {k: sorted(v) for k, v in providers.items()}, valid and database in library.complete
    library.providers[key] = result
    return result
