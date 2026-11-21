"""Build localized tooltip content from a base technology, independently of tree layout."""

from .localization import determine_key
from .tooltip_expressions import ARGUMENTS, LOGIC, councilor_position, numeric_text, operation_term
from .tooltip_labels import Labels
from .tree.ast import number
from .tree.inputs import records


SECTIONS = ('prerequisites', 'potential', 'allow', 'weight_modifier')
FLAG_CHECKS = {'has_country_flag', 'has_global_flag'}
IGNORED_FLAGS = {('has_country_flag', 'crystal_armor_1_weight')}
SYMBOLS = {'=': '=', '!=': '≠', '<': '<', '>': '>', '<=': '≤', '>=': '≥'}
INVERSE = {'=': '!=', '!=': '=', '<': '>=', '>': '<=', '<=': '>', '>=': '<'}
NUMERIC = {'years_passed', 'mid_game_years_passed', 'days_passed', 'num_cosmic_storms_encountered',
           'num_owned_planets', 'num_communications', 'num_ascension_perk_slots', 'has_base_skill',
           'perc_communications_with_playable'}
BOOLEAN = {'always', 'is_ai', 'is_nomadic', 'is_sapient', 'is_councilor', 'is_ruler', 'has_federation',
           'is_galactic_community_member', 'is_subject', 'is_astral_scar', 'is_inside_nebula', 'is_site_completed'}
SCOPES = {
    'any_agreement', 'any_country', 'any_member', 'any_neighbor_country', 'any_owned_leader',
    'any_owned_nonprimary_starbase', 'any_owned_planet', 'any_owned_pop_group', 'any_owned_species',
    'any_planet_within_border', 'any_relation', 'any_system_megastructure', 'any_system_planet',
    'any_system_within_border', 'federation', 'founder_species', 'owner', 'owner_species', 'prev',
    'solar_system', 'space_owner?', 'species', 'this',
}
NAMES = {
    'has_technology': 'technology', 'can_research_technology': 'technology', 'has_tradition': 'tradition',
    'has_ascension_perk': 'perk', 'has_crisis_level': 'level', 'has_menace_perk': 'perk', 'host_has_dlc': 'dlc',
    'has_origin': 'origin', 'has_authority': 'authority', 'has_civic': 'civic', 'has_valid_civic': 'civic',
    'has_ethic': 'ethic', 'has_ai_personality': 'personality', 'is_country_type': 'country_type',
    'uses_ship_category': 'category', 'has_trait': 'trait', 'is_archetype': 'archetype', 'is_same_species': 'other',
    'is_pop_category': 'category', 'is_councilor_type': 'position', 'has_communications': 'country',
    'has_federation_law': 'law', 'has_federation_perk': 'perk', 'is_active_resolution': 'resolution',
    'has_active_specialization': 'specialization', 'is_planet_class': 'planet_class', 'has_deposit': 'deposit',
    'has_deposit_for': 'station_class', 'has_district': 'district', 'uses_district_set': 'district_set',
    'has_megastructure': 'megastructure', 'has_relic': 'relic', 'has_seen_any_bypass': 'bypass',
    'owns_any_bypass': 'bypass', 'has_modifier': 'modifier',
    'exists': 'target', 'is_same_value': 'target',
}


class Content:
    def __init__(self, labels):
        self.labels = labels

    def unknown(self, node):
        return {'kind': 'unrecognized', 'expression': node}

    def term(self, kind, key, **arguments):
        return {'kind': kind, 'key': key, 'text': self.labels.phrase(key, **arguments)}

    def comparison(self, key, operator, value):
        if key == 'perc_communications_with_playable':
            percent = format(number(value) * 100, 'f')
            return self.term('condition', key, comparison=SYMBOLS[operator],
                             percentage=numeric_text(percent, self.labels.language) + '%')
        return self.term('condition', key, comparison=SYMBOLS[operator],
                         value=numeric_text(value, self.labels.language))

    def group(self, operator, children):
        if None in children:
            children = [child for child in children if child is not None]
            if not children:
                return None
        if len(children) == 1:
            child = children[0]
            if operator in ('AND', 'OR') and child['kind'] in ('condition', 'technology', 'group', 'scope'):
                return child
            if operator == 'NOT' and child.get('key') in ('has_origin', 'has_authority') and child['kind'] == 'condition':
                # Keep the original group until the batch lookup confirms the negative translation.
                return {'kind': 'group', 'operator': operator, 'text': self.labels.phrase('not'), 'children': children,
                        '_negative_text': self.labels.phrase('not_' + child['key'], **child['text'].arguments)}
        term = operator.lower()
        if (children and (operator != 'NOT' or len(children) == 1)
                and all(child['kind'] == 'technology' or child.get('key') == 'has_technology' for child in children)):
            term = 'technologies_' + term
            children = [{**child, 'text': self.labels.technology(child['id'], reference=True)} for child in children]
        return {'kind': 'group', 'operator': operator, 'text': self.labels.phrase(term),
                'children': children}

    def weight_rule(self, node):
        if node.get('kind') != 'assignment' or node['key'].get('text') != 'modifier' or node['operator'] != '=':
            return self.node(node, ('weight_modifier',))
        if node['value']['kind'] != 'block':
            return self.unknown(node)
        operations, checks = [], []
        for item in node['value']['items']:
            child = self.node(item, ('weight_modifier', 'modifier'))
            if item.get('key', {}).get('text') in ('factor', 'add'):
                if child is None:
                    return None
                if child['kind'] != 'operation':
                    return self.unknown(node)
                operations.append(child)
            else:
                checks.append(child)
        if not operations:
            return self.unknown(node)
        rule = {'kind': 'modifier', 'operations': operations}
        if checks:
            condition = checks[0] if len(checks) == 1 else self.group('AND', checks)
            if condition is None:
                return None
            rule['condition'] = condition
        return rule

    def conditions(self, items, path):
        children = [self.node(item, path) for item in items]
        return children[0] if len(children) == 1 else self.group('AND', children)

    @staticmethod
    def with_children(parent, children, field='children'):
        visible = [child for child in children if child is not None]
        if children and not visible:
            return None
        return {**parent, field: visible}

    def node(self, node, path):
        kind = node['kind']
        if kind == 'scalar' and path[0] == 'prerequisites':
            identifier = node['text']
            return {'kind': 'technology', 'id': identifier,
                    'text': self.labels.phrase('has_technology', technology=self.labels.technology(identifier))}
        if kind == 'block':
            return self.conditions(node['items'], path)
        if kind == 'logical_operation' and node['operator'] in LOGIC:
            op, body = node['operator'], node['body']
            if body['kind'] != 'block':
                return self.group(op, [self.node(body, path)])
            items = body['items']
            if op == 'NOT' and len(items) == 1 and items[0]['kind'] == 'assignment':
                item = items[0]
                key, sign, val = item['key']['text'], item['operator'], item['value'].get('text')
                if key in NUMERIC and sign in INVERSE and number(val) is not None:
                    return self.comparison(key, INVERSE[sign], val)
            return self.group(op, [self.node(item, path) for item in items])
        if kind == 'scripted_trigger_test':
            value, sign = node['value'].get('text'), node['operator']
            if sign not in SYMBOLS or number(value) is None:
                return self.unknown(node)
            items = node['body'].get('items', [])
            if len(items) == 1 and items[0].get('operator') == '=':
                item = items[0]
                key = item.get('key', {}).get('text')
                if key in ('count_owned_pop_amount', 'count_archaeological_site') and item['value'] == {'kind': 'block', 'items': []}:
                    return self.comparison(key, sign, value)
            return self.with_children(self.comparison('scripted_trigger_test', sign, value),
                                      [self.node(node['body'], path)])
        if kind != 'assignment':
            return self.unknown(node)
        key, sign, value = node['key']['text'], node['operator'], node['value']
        text = value.get('text')
        term = operation_term(path, key)
        if term and sign == '=':
            return self.operation(node, term, path)
        if key == 'complex_trigger_modifier' and sign == '=' and path[-1] == 'script_value':
            position = councilor_position(value)
            if position:
                return self.term('operation', 'add_councilor_level', position=self.labels.name('position', position))
        if key in NUMERIC and sign in SYMBOLS and number(text) is not None:
            return self.comparison(key, sign, text)
        if key == 'has_starbase_size' and sign in SYMBOLS and text:
            return self.term('condition', key, comparison=SYMBOLS[sign], starbase_size=self.labels.name('starbase_size', text))
        if sign != '=':
            return self.unknown(node)
        if key in FLAG_CHECKS and text:
            if (key, text) in IGNORED_FLAGS:
                return None
            return {'kind': 'condition', 'key': key, 'text': self.labels.flag(key, text, path[0])}
        if key == 'has_policy_flag' and text:
            return {'kind': 'condition', 'key': key, 'text': self.labels.policy(text)}
        if key in BOOLEAN and text in ('yes', 'no'):
            return self.term('condition', key + ('_no' if text == 'no' else ''))
        if key in NAMES and text is not None:
            slot = NAMES[key]
            label = key
            if key == 'has_trait':
                if text.startswith('leader_trait_'):
                    label += '_leader'
                elif text.startswith('trait_'):
                    label += '_species'
            role = 'pop_category' if key == 'is_pop_category' else slot
            condition = self.term('condition', label, **{slot: self.labels.name(role, text)})
            if key == 'has_technology':
                condition['id'] = text
            return condition
        if value['kind'] == 'block':
            if key in ARGUMENTS:
                return self.arguments(node, path)
            if key in SCOPES:
                return self.with_children(self.term('scope', key), [self.conditions(value['items'], (*path, key))])
            if key == 'custom_tooltip':
                return self.with_children({'kind': key}, [self.node(item, (*path, key)) for item in value['items']])
        if text and (key == 'custom_tooltip' or (path[-1] == 'custom_tooltip' and key in ('text', 'fail_text', 'success_text'))):
            return {'kind': 'caption', 'key': key, 'text': self.labels.label(text, fallback=text)}
        return self.unknown(node)

    def arguments(self, node, path):
        key = node['key']['text']
        slots = ARGUMENTS[key]
        args, children = {}, []
        for item in node['value']['items']:
            field = item.get('key', {}).get('text')
            slot = slots.get(field)
            if slot is None:
                children.append(self.node(item, (*path, key)))
                continue
            text, sign = item['value'].get('text'), item['operator']
            if text is None or slot in args or sign not in SYMBOLS or (slot != 'value' and sign != '='):
                return self.unknown(node)
            if slot == 'value':
                if number(text) is None:
                    return self.unknown(node)
                args.update(comparison=SYMBOLS[sign], value=numeric_text(text, self.labels.language))
            elif slot in ('disabled', 'in_construction'):
                args[slot] = text
            else:
                args[slot] = self.labels.name(slot, text)
        required = set(slots.values()) - {'disabled', 'in_construction'}
        if not required.issubset(args):
            return self.unknown(node)
        label = key
        if 'disabled' in args or 'in_construction' in args:
            if (args.pop('disabled', None), args.pop('in_construction', None)) != ('no', 'no'):
                return self.unknown(node)
            label += '_completed_enabled'
        result = self.term('condition', label, **args)
        return self.with_children(result, children) if children else result

    def operation(self, node, term, path):
        value, key = node['value'], node['key']['text']
        if key in ('modifier', 'if', 'else', 'limit', 'hidden_trigger'):
            if value['kind'] != 'block':
                return self.unknown(node)
            return self.with_children(self.term(key, term), [self.node(n, (*path, key)) for n in value['items']])
        operand = value.get('text')
        if key == 'factor' and operand == 'trigger:acquired_specimen_count':
            return {**self.term('operation', term, value=self.labels.phrase('acquired_specimen_count')),
                    'trigger': 'acquired_specimen_count'}
        if value['kind'] == 'script_value' and value.get('scope') is None:
            items = value['body']['items']
            if len(items) == 1 and items[0].get('key', {}).get('text') == 'base' and items[0].get('operator') == '=':
                operand = items[0]['value'].get('text')
            else:
                slot = 'signed_value' if key == 'add' else 'value'
                return self.with_children(self.term('operation', term, **{slot: self.labels.phrase('script_value')}),
                                          [self.node(n, (*path, key, 'script_value')) for n in items], 'formula')
        if number(operand) is None:
            return self.unknown(node)
        signed = key == 'add'
        text = numeric_text(operand, self.labels.language, signed=signed)
        return {**self.term('operation', term, **{'signed_value' if signed else 'value': text}), 'value': operand}


def technology_tooltip(db, rules, reader, technology_id, language):
    row = next(records(db, 'technologies', list(SECTIONS), {'_id': technology_id}), None)
    if row is None:
        return None
    labels = Labels(language, rules, db)
    content = Content(labels)
    sections = {}
    for item in row['body']['items']:
        key, block = item['key']['text'], item['value']
        if item['operator'] != '=' or block['kind'] != 'block':
            sections.setdefault(key, []).append(content.unknown(item))
        elif block['items']:
            entries = sections.setdefault(key, [])
            if key == 'weight_modifier':
                entries.extend(row for child in block['items'] if (row := content.weight_rule(child)) is not None)
            else:
                condition = content.conditions(block['items'], (key,))
                if condition is not None:
                    entries.append(condition)
            if not entries:
                del sections[key]
    return labels.resolve({'technology_id': technology_id, 'language': language,
                           'name': labels.technology(technology_id),
                           'description': labels.label(determine_key(rules, 'technology_description', technology_id)),
                           'sections': sections}, reader)
