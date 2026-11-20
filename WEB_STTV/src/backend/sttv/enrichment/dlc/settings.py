"""Load explicit rule groups and reject ambiguous or dangling configuration."""

from copy import deepcopy
from sttv.common.errors import BuildError
from sttv.common.paths import selected_path


def resolve(options, read, work):
    result = deepcopy(options)
    rows = [row for group in options['groups']
            for row in read(selected_path(group, work), 'dlc_group.schema.json')['rules']]
    identifiers, predicates = set(), set()
    for row in rows:
        if row['id'] in identifiers or predicates.intersection(row['predicates']):
            raise BuildError('invalid_dlc_rules', f'Duplicate DLC rule or predicate: {row["id"]}')
        identifiers.add(row['id'])
        predicates.update(row['predicates'])
    for row in rows:
        if row['database'] not in result['required_datasets']:
            raise BuildError('invalid_dlc_rules', f'Undeclared required catalog: {row["database"]}')
        if row['handler'] == 'observe' and row['gates']:
            raise BuildError('invalid_dlc_rules', 'Observation rules cannot declare proof gates')
        if row['handler'] in ('ship_category', 'tradition') and 'providers' not in row:
            raise BuildError('invalid_dlc_rules', f'Missing provider relation: {row["id"]}')
        if 'providers' in row and not any(r['id'] == row['providers']['rule'] and r['enabled'] for r in rows):
            raise BuildError('invalid_dlc_rules', f'Missing enabled provider rule: {row["id"]}')
    if any(p not in predicates for p in result['government_requirements'].values()):
        raise BuildError('invalid_dlc_rules', 'Government requirement refers to an unknown predicate')
    result['rules'] = rows
    if options.get('acquisition'):
        from sttv.enrichment.acquisition.configuration import load
        result['acquisition'], _ = load(options['acquisition'], work, read)
    return result
