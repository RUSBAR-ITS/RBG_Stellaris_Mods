"""Interpret condition forms shared by technology sections and acquisition paths."""

from functools import cache
import json
from pathlib import Path
import re

from .localization import determine_key
from .tree.ast import number

@cache
def default_rules():
    return json.loads((Path(__file__).resolve().parents[1] / 'config/condition_rules.json').read_text(encoding='utf8'))

FLAGS = set('has_archaeology_flag has_astral_rift_flag has_carrier_flag has_first_contact_flag has_fleet_flag has_leader_flag has_planet_flag has_ship_flag has_situation_flag has_species_flag has_star_flag has_storm_flag'.split())
SIGNS = {'=': '=', '!=': '≠', '<': '<', '>': '>', '<=': '≤', '>=': '≥'}


def typed_name(labels, role, value):
    if role == 'literal':
        return value
    if role == 'target':
        return scope_name(labels, value)
    keys = {'mission': ['mission_' + value], 'event_chain': [value + '_title', value],
            'scope_type': ['sttv_tooltip_role_' + value, value.upper(), value],
            'graphical_culture': [value, value.upper(), value.upper() + '_SHIP'],
            'crisis_type': ['CRISIS_TYPE_' + value.upper(), value.upper(), value],
            'climate': ['climate_' + value, value], 'leader_class': ['leader_class_' + value, value],
            'variable': ['sttv_tooltip_variable_' + value, value], 'portrait': ['por_' + value, value]}
    fallback = 'module_unavailable' if role == 'starbase_module' else 'name_unavailable'
    name_keys = keys.get(role, [determine_key(labels.rules, role, value) or value])
    if role in ('graphical_culture', 'portrait', 'contact', 'type'):
        name_keys = ['sttv_tooltip_' + role + '_' + value, *name_keys]
    label = labels.label(*name_keys, 'sttv_tooltip_' + fallback, color='Y')
    label.missing = {'reason': 'missing_object_name', 'type': role, 'id': value}
    return label


def scope_parts(labels, value):
    # A saved name can itself contain a dotted substitution such as @root.controller.
    if '.' not in value or not (value.lower().startswith('event_target:') and '@' in value):
        return value.split('.')
    target = value.split(':', 1)[1].removesuffix('?')
    if target not in labels.saved_targets:
        for saved in sorted(labels.saved_targets, key=len, reverse=True):
            if target.startswith(saved + '.'):
                first = value[:len('event_target:') + len(saved)]
                return [first, *value[len(first)+1:].split('.')]
    return [value]


def scope_name(labels, value):
    parts = scope_parts(labels, value)
    if labels.scope is not None:
        with labels.scope.nested(parts) as names:
            # Each role is resolved relative to the preceding participant.
            last = names[-1]
            if len(parts) > 1 and parts[-1].lower() not in ('owner', 'controller', 'leader', 'this', 'root', 'prev'):
                last = {'scope_path': names}
            return labels.phrase('optional_scope', scope=last) if value.endswith('?') else last
    if len(parts) > 1:
        return {'scope_path': [scope_name(labels, p) for p in parts]}
    return literal_scope(labels, value)


def literal_scope(labels, value):
    name = value.removesuffix('?')
    part = name.casefold()
    if part.startswith('event_target:'):
        target = name.split(':', 1)[1]
        locale = 'sttv_tooltip_target_' + target
        label = labels.label(locale, 'sttv_tooltip_saved_target')
        label.missing = {'reason': 'unknown_scope_role', 'id': target}
        sites = labels.saved_targets.get(target, ())
        if sites:
            roles = set()
            for site in sites:
                scope = site['scope'].casefold()
                if scope in ('owner', 'controller', 'overlord', 'create_rebels'):
                    roles.add('country')
                elif m := re.search(r'(?:^|_)(country|fleet|planet|ship|leader|system|species)(?:_event)?$', scope):
                    roles.add(m[1])
                else:
                    break
            else:
                if len(roles) == 1:
                    role, = roles
                    label.keys = label.keys[:1]
                    label.fallback = labels.phrase('saved_role', role=labels.phrase('role_' + role))
                    label.missing = None
            if label.missing:
                examples = {s['scope']: s for s in sites}
                label.missing = {**label.missing, 'reason': 'ambiguous_saved_target',
                                 'assignment_count': len(sites), 'examples': list(examples.values())}
    elif re.fullmatch(r'(?:prev){2,}', part):
        label = {'scope_path': [labels.phrase(part[:4]) for _ in range(len(part) // 4)]}
    else:
        rules = labels.rules.get('condition_rules') or default_rules()
        label = labels.label(rules.get(part, {}).get('scope_locale'), 'sttv_tooltip_' + part,
                             'sttv_tooltip_progress_scope_' + part,
                             'sttv_tooltip_saved_target')
        label.missing = {'reason': 'unknown_scope_role', 'id': value}
    return labels.phrase('optional_scope', scope=label) if value.endswith('?') else label


def calculated_factor(labels, value):
    """Read a numeric script value in execution order, preserving bounds and rounding."""
    if value.get('kind') != 'script_value' or value.get('scope') is not None:
        return None
    expression = None
    operations = {'add': '+', 'mult': '×', 'divide': '/', 'min': 'max', 'max': 'min'}
    for step in value['body']['items']:
        if step.get('kind') != 'assignment' or step['operator'] != '=':
            return None
        key, operand = step['key']['text'].casefold(), step['value']
        literal = operand.get('text')
        if key == 'base' and expression is None and number(literal) is not None:
            expression = labels.numeric(literal)
        elif expression is None:
            return None
        elif key == 'complex_trigger_modifier' and operand.get('kind') == 'block':
            fields = operand['items']
            if len(fields) != 2 or any(f.get('kind') != 'assignment' or f['operator'] != '=' for f in fields):
                return None
            args = {f['key']['text'].casefold(): f['value'].get('text') for f in fields}
            if args != {'trigger': 'years_passed', 'mode': 'add'}:
                return None
            years = labels.phrase('years_passed', comparison='', value='')
            expression = {'math': ['+', expression, years]}
        elif key == 'floor' and literal == 'yes':
            expression = {'math': ['floor', expression]}
        elif key in operations and number(literal) is not None:
            expression = {'math': [operations[key], expression, labels.numeric(literal)]}
        else:
            return None
    return expression


def stockpile(content, items, path):
    labels = content.labels
    args = {item['key']['text'].casefold(): item for item in items}
    if len(args) != len(items) or set(args) not in ({'resource', 'value'}, {'resource', 'value', 'mult'}):
        return None
    resource = args['resource']['value'].get('text')
    sign = args['value']['operator']
    if not resource or args['resource']['operator'] != '=' or sign not in SIGNS:
        return None
    formula = []
    def operand(field):
        value = args[field]['value']
        literal = value.get('text')
        if number(literal) is not None:
            return labels.numeric(literal)
        if field == 'mult' and literal == 'root.trigger:empire_size':
            return labels.phrase('empire_size')
        if value.get('kind') == 'script_value' and value.get('scope') is None:
            arithmetic = calculated_factor(labels, value)
            if arithmetic is not None:
                return arithmetic
            steps = [result for step in value['body']['items']
                     if (result := content.node(step, (*path, 'resource_stockpile_compare', field, 'script_value'))) is not None]
            formula.append({**content.term('operation', 'script_value'), 'children': steps, 'expression': value})
        else:
            formula.append(content.partial(args[field], path))
        return labels.phrase('script_value')
    threshold = operand('value')
    if 'mult' in args:
        if args['mult']['operator'] != '=':
            return None
        threshold = labels.phrase('stockpile_scaled', value=threshold, factor=operand('mult'))
    result = content.term('condition', 'resource_stockpile_compare', resource=typed_name(labels, 'resource', resource),
                          comparison=SIGNS[sign], value=threshold)
    if formula:
        result['formula'] = formula
    return result


def apply(content, node, path, scopes):
    labels = content.labels
    raw, op, value = node['key']['text'], node['operator'], node['value']
    key, arg = raw.casefold(), value.get('text')
    rules = labels.rules.get('condition_rules') or default_rules()
    rule = rules.get(key, {})
    if 'percent' in rule and op in SIGNS and number(arg) is not None:
        percentage = format((number(arg) * 100).normalize(), 'f')
        return content.term('condition', key, comparison=SIGNS[op], value=labels.numeric(percentage, suffix='%'))
    if key == 'current_awareness_level' and op in SIGNS and arg:
        return content.term('condition', key, comparison=SIGNS[op],
                            name=labels.label('awareness_' + arg, 'sttv_tooltip_name_unavailable'))
    if key == 'species_portrait' and op == '=' and arg:
        name = (labels.phrase('portrait_mol4') if arg == 'mol4' else typed_name(labels, 'portrait', arg))
        return {**content.term('condition', key, name=name),
                'reference': {'type': 'portrait', 'id': arg}}
    if op in SIGNS and 'number' in rule and number(arg) is not None:
        return content.comparison(key, op, arg)
    if op != '=':
        return
    if arg in ('yes', 'no') and arg in rule.get('boolean_locale', {}):
        return {'kind': 'condition', 'key': key, 'text': labels.label(rule['boolean_locale'][arg])}
    if arg in ('yes', 'no') and 'boolean' in rule:
        term = rule['boolean']
        child = content.term('condition', term)
        if arg == 'no':
            if key == 'has_deposit':
                return content.term('condition', term + '_no')
            child['text'] = labels.phrase('predicate_false', predicate=child['text'])
        return child
    if arg and arg in rule.get('event_titles', {}):
        event = labels.label(rule['event_titles'][arg], 'sttv_tooltip_source_unnamed', color='Y')
        return {**content.term('condition', 'observation_event_marked', event=event),
                'reference': {'type': key, 'id': arg}}
    if arg and key in FLAGS:
        label = labels.label('sttv_tooltip_' + key + '_' + arg, 'sttv_tooltip_unresolved_flag')
        label.missing = {'reason': 'missing_flag_label', 'check': key, 'flag': arg, 'section': path[0]}
        return content.flag_condition(key, arg, label)
    if key == 'is_country_type' and arg == 'primitive':
        return content.term('condition', key, country_type=labels.phrase('country_pre_ftl'))
    if arg and 'reference' in rule:
        role = rule['reference']
        return {**content.term('condition', key, name=typed_name(labels, role, arg)),
                'reference': {'type': role, 'id': arg}}
    if value.get('kind') != 'block':
        return
    items = value['items']
    if key in ('switch', 'inverted_switch'):
        triggers = [n for n in items if n.get('key', {}).get('text') == 'trigger']
        if len(triggers) != 1 or not (test := triggers[0]['value'].get('text')):
            return content.partial(node, path)
        branches = []
        for case in items:
            if case is triggers[0]:
                continue
            name = case.get('key', {}).get('text')
            if not name or case.get('operator') != '=' or case['value'].get('kind') != 'block':
                return content.partial(node, path)
            body = content.conditions(case['value']['items'], (*path, key))
            if name == 'default':
                branch = content.term('condition', 'switch_else')
                checks = []
            else:
                predicate = {'kind': 'assignment', 'operator': '=', 'key': {'kind': 'scalar', 'text': test},
                             'value': case['key']}
                check = content.node(predicate, (*path, key))
                if check is None:
                    return content.partial(node, path)
                checks = [content.group('NOT', [check]) if key == 'inverted_switch' else check]
                branch = content.term('condition', 'switch_case')
            if body:
                checks.append(content.with_children(content.term('condition', 'switch_result'), [body]))
            branches.append(content.with_children(branch, checks))
        return content.with_children(content.term('condition', 'switch_order'), branches)
    if key == 'has_active_event' and items and all(n['kind'] == 'scalar' for n in items):
        events = []
        for item in items:
            ident = item['text']
            keys = content.index.event_keys(ident) if content.index else (ident + '.name',)
            events.append({**content.term('condition', key, event=labels.label(*keys, 'sttv_tooltip_source_unnamed')),
                           'reference': {'type': 'events', 'id': ident}})
        return events[0] if len(events) == 1 else content.group('OR', events)
    parts = scope_parts(labels, raw)
    if all(p.lower().rstrip('?') in scopes or 'scope' in rules.get(p.lower().rstrip('?'), {})
           or p.lower().startswith('event_target:') for p in parts):
        if labels.scope is None:
            names = [scope_name(labels, part) for part in parts]
            child = content.conditions(items, (*path, raw)) if items else None
        else:
            with labels.scope.nested(parts) as names:
                child = content.conditions(items, (*path, raw)) if items else None
            names = [labels.phrase('optional_scope', scope=name) if part.endswith('?') else name
                     for part, name in zip(parts, names)]
        if items and child is None:
            return None
        for part, label in reversed(list(zip(parts, names))):
            if (part.casefold() == 'any_relation' and child and child.get('key') == 'is_same_value'
                    and child['kind'] == 'condition' and child.get('reference')):
                child = {**content.term('condition', 'has_relation_with', target=child['text'].arguments['target']),
                         'reference': child['reference']}
                continue
            child = {'kind': 'scope', 'key': part.casefold(), 'text': label,
                     'children': [child] if child is not None else []}
        return child
    if key == 'else_if' or key == 'limit' and path[-1] not in ('if', 'count_owned_pop_amount', 'count_archaeological_site'):
        return content.with_children(content.term('scope', 'branch_else_if' if key == 'else_if' else 'branch_limit'),
                                     [content.conditions(items, (*path, key))])
    if not items or any(n.get('kind') != 'assignment' for n in items):
        return
    if rule.get('count') or key in ('count_controlled_ship', 'count_system_within_storm', 'count_owned_planet'):
        by_key = {n['key']['text']: n for n in items}
        if len(items) == len(by_key) and 'count' in by_key and by_key.keys() <= {'count', 'limit'}:
            limit, count = by_key.get('limit'), by_key['count']
            sign, amount = count['operator'], count['value'].get('text')
            if sign in SIGNS and (number(amount) is not None or sign == '=' and amount == 'all'):
                label = labels.phrase('all_members') if amount == 'all' else labels.numeric(amount)
                result = content.term('condition', key, comparison=SIGNS[sign], value=label)
                if limit is None:
                    return result
                if limit['operator'] == '=' and limit['value'].get('kind') == 'block':
                    if labels.scope:
                        with labels.scope.nested([key]):
                            child = content.conditions(limit['value']['items'], (*path, key))
                    else:
                        child = content.conditions(limit['value']['items'], (*path, key))
                    return content.with_children(result, [child])
    if key == 'resource_stockpile_compare':
        return stockpile(content, items, path)
    fields = {n['key']['text'].casefold(): (n['operator'], n['value'].get('text')) for n in items}
    if len(fields) != len(items):
        return
    if any(text is None for _, text in fields.values()):
        return
    if key == 'relative_power' and {'who', 'value'} <= fields.keys() <= {'who', 'category', 'value'}:
        who, (sign, rank) = fields['who'], fields['value']
        category = fields.get('category', ('=', 'all'))
        ranks = ('pathetic', 'inferior', 'equivalent', 'superior', 'overwhelming')
        if (who[0] == '=' and sign in SIGNS and rank in ranks and category[0] == '='
                and category[1] in ('all', 'fleet', 'economy', 'technology')):
            return content.term('condition', key, target=scope_name(labels, who[1]),
                                category=labels.phrase('power_' + category[1]), comparison=SIGNS[sign],
                                rank=labels.label('RELATIVE_POWER_' + str(ranks.index(rank) + 1)))
    if key == 'distance' and 'source' in fields and fields['source'][0] == '=':
        if fields.keys() <= {'source', 'min_distance', 'max_distance', 'min_jumps', 'max_jumps', 'use_bypasses'}:
            result = content.term('condition', key, target=scope_name(labels, fields['source'][1]))
            return content.with_children(result, [content.node(item, (*path, key)) for item in items
                                                   if item['key']['text'].casefold() != 'source'])
    if key == 'can_copy_random_tech_from' and 'who' in fields and fields.keys() <= {'who', 'area', 'category'} and all(
        sign == '=' for sign, _ in fields.values()
    ):
        result = content.term('condition', key, donor=scope_name(labels, fields['who'][1]))
        result['children'] = [content.term('condition', 'pool_' + k, value=typed_name(labels, 'research_' + k, v))
                              for k, (_, v) in fields.items() if k != 'who']
        return result
    if key == 'intel_level' and set(fields) == {'system', 'level'} and fields['system'][0] == '=' and fields['level'][0] in SIGNS:
        return content.term('condition', key, system=scope_name(labels, fields['system'][1]),
            comparison=SIGNS[fields['level'][0]], level=labels.label('INTEL_LEVEL_' + fields['level'][1].upper(),
            'sttv_tooltip_name_unavailable'))
    if key == 'is_point_of_interest' and 'owner' in fields and fields.keys() <= {'owner', 'id', 'event_chain'} and all(
        sign == '=' for sign, _ in fields.values()
    ):
        poi = content.term('condition', key, owner=scope_name(labels, fields['owner'][1]))
        details = []
        if 'event_chain' in fields:
            details.append(content.term('condition', 'poi_chain', name=typed_name(labels, 'event_chain', fields['event_chain'][1])))
        if 'id' in fields:
            identifier = fields['id'][1]
            details.append(content.term('condition', 'poi_name', name=labels.label(identifier + '.name', identifier,
                                       'sttv_tooltip_poi_' + identifier,
                                       'sttv_tooltip_name_unavailable')))
        return {**poi, 'children': details, 'expression': node}
    if key == 'starbase_buildable_is_in_queue_before' and set(fields) == {'first', 'second'} and all(
            sign == '=' for sign, _ in fields.values()):
        return {**content.term('condition', 'queued_module', name=typed_name(labels, 'starbase_buildable', fields['first'][1]),
                               second=typed_name(labels, 'starbase_buildable', fields['second'][1])),
                'references': [v for _, v in fields.values()]}
    if key == 'has_relation_flag' and set(fields) == {'who', 'flag'} and all(sign == '=' for sign, _ in fields.values()):
        label = labels.label('sttv_tooltip_has_relation_flag_' + fields['flag'][1], 'sttv_tooltip_flag_relation',
                             arguments={'target': scope_name(labels, fields['who'][1])})
        label.missing = {'reason': 'missing_flag_label', 'check': key, 'flag': fields['flag'][1], 'section': path[0]}
        return {'kind': 'condition', 'key': key, 'text': label, 'expression': node}
    roles = {'has_completed_event_chain_counter': ('event_chain_counter', {'event_chain': ('chain', 'event_chain'), 'counter': ('counter', 'counter')}),
             'has_patron_relation': ('patron_test', {'patron': ('patron', 'patron'), 'contact': ('contact', 'contact')})}
    if key in roles:
        term, required = roles[key]
        if set(fields) == required.keys() and all(sign == '=' for sign, _ in fields.values()):
            args = {slot: typed_name(labels, role, fields[k][1]) for k,(slot,role) in required.items()}
            return content.term('condition', term, **args)
    pairs = {'has_country_resource': ('type', 'amount', 'resource', 'resource', 'resource_stockpile_compare'),
             'distance': ('source', 'max_distance', 'source', 'target', 'distance_to'),
             'num_researched_techs_of_tier': ('tier', 'value', 'tier', 'literal', 'tier_count'),
             'check_variable': ('which', 'value', 'variable', 'variable', 'check_variable'),
             'trust': ('who', 'value', 'target', 'target', 'trust_test')}
    if key in pairs:
        name, field, slot, role, phrase = pairs[key]
        if set(fields) == {name, field} and fields[name][0] == '=':
            sign, amount = fields[field]
            if sign in SIGNS and number(amount) is not None:
                return content.term('condition', phrase, comparison=SIGNS[sign], value=labels.numeric(amount),
                                    **{slot: typed_name(labels, role, fields[name][1])})
