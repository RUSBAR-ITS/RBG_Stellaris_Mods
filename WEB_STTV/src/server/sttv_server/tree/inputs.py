"""Project analytical fields in MongoDB before transferring BSON to Python."""

import json

from . import evidence, groups
from .ast import compact, fields, number, numeric_items, prerequisite, references, requirements, scalar
from .catalog import Catalog
from .errors import BuildError


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from strings(item)


def records(db, kind, keys, match=None):
    items = {'$filter': {'input': '$tree.value.items', 'as': 'entry',
                         'cond': {'$in': ['$$entry.key.text', keys]}}}
    pipeline = [{'$match': match}] if match else []
    pipeline.append({'$project': {'source.file': 1, 'pointer': 1, 'type': '$tree.key.text', 'items': items,
                                  'keys': {'$map': {'input': '$tree.value.items', 'as': 'item',
                                                    'in': {'$ifNull': ['$$item.key.text', None]}}}}})
    selected = set(keys)
    for row in db[kind].aggregate(pipeline, batchSize=20):
        key = row['_id']
        if not isinstance(key, str):
            key = row['type'] if kind == 'on_actions' else json.dumps(key, sort_keys=True)
        body = compact({'kind': 'block', 'items': row['items'] or []})
        for entry, index in zip(body['items'], (i for i, v in enumerate(row['keys'] or []) if v in selected), strict=True):
            entry['source_index'] = index
        yield {'id': key, 'type': row['type'], 'body': body,
               'source': {'database': kind, 'document_id': row['source']['file'], 'pointer': row['pointer']}}


def technology(row):
    body = row['body']
    req = prerequisite(body)
    parents, mandatory, _ = requirements(req)
    bonuses, conflict = {}, False
    for block in fields(body, 'modifier'):
        for key, value in numeric_items(block):
            conflict |= key in bonuses and bonuses[key] != value
            bonuses[key] = value
    return {**row, 'tier': int(scalar(body, 'tier')), 'area': scalar(body, 'area'),
            'levels': number(scalar(body, 'levels')), 'starting': scalar(body, 'start_tech') == 'yes',
            'variant': 'base', 'potential': fields(body, 'potential'), 'prerequisites': req,
            'parents': sorted(parents), 'mandatory': mandatory, 'bonuses': bonuses,
            'effects_unknown': 'conflicting_effects' if conflict else None,
            'category': sorted(set().union(*(references(n) for n in fields(body, 'category'))))}


def load_inputs(db, config):
    kinds = config['catalogs']
    keys = sorted(set(strings(config['parent_rules'])) | set(strings(config['dlc']['rules'])) |
                  {'tier', 'area', 'category', 'levels', 'start_tech', 'potential', 'weight_modifier',
                   'modifier', 'prerequisites', 'allow', 'possible', 'produces', 'resources', 'name'})
    data = {kind: list(records(db, kind, keys)) for kind in kinds if kind not in ('localization', 'events')}
    techs = {row['id']: technology(row) for row in data['technologies']}
    for tech in techs.values():
        missing = set(tech['parents']) - techs.keys()
        if missing:
            raise BuildError('missing_prerequisite', f"{tech['id']}: {sorted(missing)}")
    names = {row['id']: scalar(row['body'], 'name') for row in data['dlcs']}
    if None in names.values() or len(set(names.values())) != len(names):
        raise BuildError('invalid_dlc_catalog', 'Missing or duplicate game name')
    catalog = Catalog(data)
    functional = next((r for r in config['parent_rules'] if r['id'] == 'functional_groups' and r['enabled']), None)
    routes = groups.routes(catalog, techs, functional['parameters']['weapon']) if functional else []
    wanted = sorted({key for route in routes for key in route['events']})
    data['events'] = list(records(db, 'events', keys, {'_id': {'$in': wanted}}))
    catalog = Catalog(data)
    proofs = evidence.prepare(catalog, techs, {'rules': config['parent_rules']}, routes)
    return names, techs, catalog, proofs
