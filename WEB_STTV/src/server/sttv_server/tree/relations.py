"""Confirmed object upgrades, positive object relations and component effects."""

from collections import defaultdict

from .ast import fields, checks, references, prerequisite, requirements, unlocks, numeric_items, access


def upgrades(catalog, techs, config):
    result = defaultdict(list)
    for mapping in config['mappings']:
        kind = mapping['kind']
        for source in catalog.rows(kind):
            for key in set().union(*(references(n) for n in fields(source['body'], mapping['field']))):
                target = catalog.resolve(kind, key)
                if target is None:
                    continue
                catalog.resolve(kind, source['id'])
                before, after = (source, target) if mapping['direction'] == 'forward' else (target, source)
                ra, _, simple_a = requirements(prerequisite(before['body']), strict=False)
                rb, _, simple_b = requirements(prerequisite(after['body']), strict=False)
                removed, added = ra - rb, rb - ra
                if not simple_a or not simple_b or len(removed) != 1 or len(added) != 1:
                    continue
                parent, child = next(iter(removed)), next(iter(added))
                if child in techs and parent in techs[child]['parents']:
                    result[child].append({'parent': parent, 'from': before['source'], 'to': after['source'],
                        'shared': sorted(ra & rb), 'requirements': [prerequisite(before['body']), prerequisite(after['body'])]})
    return result


def direct(catalog, techs, config):
    result = defaultdict(list)
    for kind in config['kinds']:
        for obj in catalog.rows(kind):
            affected = unlocks(obj) & techs.keys()
            if not affected:
                continue
            for section in config['sections']:
                for block in fields(obj['body'], section):
                    for key, value, operator, path in checks(block, (section,)):
                        linked = []
                        if key in config['relations'] and operator in config['operators'] and value['kind'] == 'scalar':
                            linked.append((config['relations'][key], value['text']))
                        queue = config['queue']
                        if key == queue['command'] and operator == '=':
                            linked.extend((k, v.get('text')) for v in fields(value, queue['field']) for k in queue['kinds'])
                        for other_kind, other_key in linked:
                            other = catalog.resolve(other_kind, other_key)
                            if not other:
                                continue
                            for tech in sorted(affected):
                                for parent in sorted(unlocks(other) & set(techs[tech]['parents'])):
                                    catalog.resolve(kind, obj['id'])
                                    result[tech].append({'parent': parent, 'source': obj['source'],
                                        'target': other['source'], 'command': key, 'operator': operator,
                                        'path': list(path), 'condition': block, 'access': access(obj),
                                        'target_access': access(other), 'conditional': True})
    return result


def indirect(catalog, techs, config):
    effects, result = defaultdict(list), defaultdict(list)
    for obj in catalog.rows(config['kind']):
        owners = references(prerequisite(obj['body'])) & techs.keys()
        for block in fields(obj['body'], config['modifier_block']):
            for modifier, value in numeric_items(block):
                if value:
                    for owner in owners:
                        effects[owner].append({'source': obj['source'], 'modifier': modifier,
                            'sign': 1 if value > 0 else -1, 'value': str(value), 'access': access(obj)})
    for child, tech in techs.items():
        if len(tech['parents']) < 2:
            continue
        for parent in tech['parents']:
            queue = [(parent, [parent])]
            while queue:
                current, path = queue.pop()
                if len(path) > config['depth']:
                    continue
                for ancestor in techs[current]['parents']:
                    if ancestor in path:
                        continue
                    route = [*path, ancestor]
                    queue.append((ancestor, route))
                    for target in effects[child]:
                        for prior in effects[ancestor]:
                            if (target['modifier'], target['sign']) == (prior['modifier'], prior['sign']):
                                result[child].append({'parent': parent, 'ancestor': ancestor, 'path': route,
                                    'context': config['modifier_block'], 'target_effect': target, 'ancestor_effect': prior,
                                    'requirements': [techs[k]['prerequisites'] for k in path], 'conditional': True})
    return result
