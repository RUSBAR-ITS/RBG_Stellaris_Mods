"""Functional group evidence from explicit object and action/event routes."""

from collections import defaultdict

from .ast import fields, scalar, references, prerequisite, checks, number, unlocks, access


def routes(catalog, techs, config):
    result = []
    for kind in config['kinds']:
        for obj in catalog.rows(kind):
            owners = sorted(unlocks(obj) & techs.keys())
            if not owners:
                continue
            for action_id in sorted(set().union(*(references(v) for v in fields(obj['body'], config['action_field'])))):
                action = catalog.resolve(config['action_kind'], action_id, required=True)
                hook_id = scalar(action['body'], config['completion_field'])
                hooks = catalog.resolve(config['hook_kind'], hook_id, fragments=True, required=True)
                events = sorted(set().union(*(references(v) for hook in hooks
                                             for v in fields(hook['body'], config['events_field']))))
                if not events:
                    continue
                catalog.resolve(kind, obj['id'])
                result.append({'owners': owners, 'object': obj['source'], 'access': access(obj),
                    'action': action['source'], 'action_body': action['body'],
                    'hooks': [{'source': h['source'], 'body': h['body']} for h in hooks], 'events': events})
    return result


def damage(node, config, path=()):
    if node.get('kind') == 'assignment':
        key = node['key']['text']
        if key in config['excluded_effect_sections']:
            return
        if key == config['damage_command']:
            yield {'path': list(path), 'value': node['value']}
        yield from damage(node['value'], config, path + (key,))
    elif node.get('kind') == 'logical_operation':
        yield from damage(node['body'], config, path + (node['operator'],))
    else:
        for i, child in enumerate(node.get('items', [])):
            yield from damage(child, config, path + (i,))


def collect(catalog, techs, config, weapon_routes):
    result = defaultdict(list)
    ship = config['ship']
    for obj in catalog.rows(ship['kind']):
        speed = number(scalar(obj['body'], ship['speed_field']))
        roles = set().union(*(references(n) for n in fields(obj['body'], ship['roles_field'])))
        if speed is None or speed <= 0 or not roles.intersection(ship['roles']):
            continue
        for owner in sorted(references(prerequisite(obj['body'])) & techs.keys()):
            catalog.resolve(ship['kind'], obj['id'])
            result[owner].append({'group': ship['group'], 'object': obj['source'],
                                 'speed': str(speed), 'roles': sorted(roles), 'access': access(obj)})
    terra = config['terraform']
    for obj in catalog.rows(terra['kind']):
        start, end = (scalar(obj['body'], terra[key]) for key in ('from_field', 'to_field'))
        if obj['type'] != terra['type'] or not start or not end or start == end:
            continue
        for block in fields(obj['body'], terra['condition_field']):
            for key, value, operator, path in checks(block):
                if key == terra['predicate'] and operator == '=' and value.get('text') in techs:
                    result[value['text']].append({'group': terra['group'], 'object': obj['source'],
                        'from': start, 'to': end, 'condition': block, 'path': list(path), 'conditional': True})
    weapon = config['weapon']
    for obj in catalog.rows(weapon['component_kind']):
        if obj['type'] == weapon['component_type']:
            for owner in sorted(unlocks(obj) & techs.keys()):
                catalog.resolve(weapon['component_kind'], obj['id'])
                result[owner].append({'group': weapon['group'], 'object': obj['source'], 'access': access(obj)})
    for route in weapon_routes:
        for event_id in route['events']:
            event = catalog.resolve(weapon['event_kind'], event_id, required=True)
            effects = fields(event['body'], weapon['effect_field'])
            hits = [hit for i, effect in enumerate(effects) for hit in damage(effect, weapon, (weapon['effect_field'], i))]
            if hits:
                for owner in route['owners']:
                    result[owner].append({'group': weapon['group'], 'route': route, 'event': event['source'],
                                         'effects': effects, 'damage': hits, 'conditional': True})
    return result
