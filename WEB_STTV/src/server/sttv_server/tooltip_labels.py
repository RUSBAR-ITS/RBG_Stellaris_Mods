"""Resolve the names and phrases used by one tooltip in a batch."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass

from .tooltip_expressions import numeric_text
from .localization import determine_key, lookup
from .tree.ast import fields, scalar
from .tree.inputs import records


@dataclass
class Label:
    keys: tuple
    fallback: str | Label | None
    arguments: dict | None = None
    color: str | None = None
    missing: dict | None = None
    russian_key: str | None = None
    disabled_dlc: str | None = None
    wrapper: str | None = None


class Labels:
    def __init__(self, language, rules, db):
        self.language = language
        self.rules = rules
        self.db = db
        self.keys = set()
        self.diagnostics = []
        self._dlcs = None
        self._policies = None
        self._bypasses = None
        self.saved_targets = {}

    def label(self, *keys, fallback=None, arguments=None, color=None, wrapper=None):
        keys = tuple(k for k in keys if k)
        self.keys.update(keys)
        if wrapper:
            self.keys.add(wrapper)
        return Label(keys, fallback, arguments, color, wrapper=wrapper)

    def phrase(self, term, **arguments):
        key = determine_key(self.rules, 'tooltip_condition', term)
        return self.label(key, fallback=term, arguments=arguments)

    def flag(self, check, identifier, section):
        specific = determine_key(self.rules, 'tooltip_condition', check + '_' + identifier)
        neutral = determine_key(self.rules, 'tooltip_condition', check)
        label = self.label(specific, neutral, fallback='…')
        label.missing = {'reason': 'missing_flag_label', 'check': check, 'flag': identifier, 'section': section}
        return label

    def numeric(self, value, *, signed=False, prefix='', suffix=''):
        if self.language is None:
            return {'number_format': [value, signed, prefix, suffix]}
        return prefix + numeric_text(value, self.language, signed=signed) + suffix

    def resolve(self, result, reader, enabled=None):
        display_keys = {f'sttv_tooltip_{key}' for key in ('dynamic_value', 'dynamic_ruler', 'dynamic_planet',
                        'dynamic_name', 'country_pre_ftl', 'missing_game_string')}
        items = lookup(self.language, sorted(self.keys | display_keys), reader)['items']
        texts = {item['key']: item['text'] for item in items if item['text']}

        localized = {}
        diagnostic_keys = {repr(issue) for issue in self.diagnostics}

        def report(issue):
            marker = repr(issue)
            if marker not in diagnostic_keys:
                self.diagnostics.append(issue)
                diagnostic_keys.add(marker)

        def display(text, source_key):
            def dynamic(match):
                token = match[1]
                label = 'dynamic_value'
                name = token.casefold()
                if 'getrulername' in name:
                    label = 'dynamic_ruler'
                elif 'pre_ftl_planet.getname' in name:
                    label = 'dynamic_planet'
                elif 'getpreftl' in name or 'primitive_civ.getname' in name:
                    label = 'country_pre_ftl'
                elif 'getname' in name or 'getrealname' in name or 'getfirstname' in name:
                    label = 'dynamic_name'
                issue = {'reason': 'campaign_localization', 'key': source_key, 'expression': token,
                         'language': self.language}
                report(issue)
                return texts.get('sttv_tooltip_' + label, match[0])
            text = re.sub(r"\[([^\[\]]+)\]", dynamic, text).replace(r'\n', '\n')
            if '|||' in text:
                forms = text.split('|||')
                base = re.sub(r'&![a-z]+$', '', forms[0])
                nominative = next((f[5:] for f in forms[1:] if f.startswith('masc:')), None)
                text = nominative or base
            def unresolved(match):
                issue = {'reason': 'unresolved_localization_reference', 'key': source_key,
                         'expression': match[0], 'language': self.language}
                report(issue)
                return texts.get('sttv_tooltip_missing_game_string', match[0])
            return re.sub(r'\$[^$\n]+\$', unresolved, text)

        def missing_name(phrase):
            candidates = phrase.keys if isinstance(phrase.fallback, Label) else phrase.keys[:-1]
            return phrase.missing and not any(key in texts for key in candidates)

        def visit(value):
            if isinstance(value, Label):
                if missing_name(value):
                    issue = {**value.missing, 'technology': result.get('technology_id'), 'language': self.language}
                    report(issue)
                if id(value) in localized:
                    return localized[id(value)]
                keys = list(value.keys)
                if self.language == 'ru' and value.russian_key:
                    keys.insert(0, value.russian_key)
                if value.disabled_dlc and enabled is not None and value.disabled_dlc not in enabled:
                    keys.insert(0, determine_key(self.rules, 'tooltip_condition', 'progress_dlc_disabled'))
                source_key = next((k for k in keys if k in texts), None)
                text = texts.get(source_key)
                if text is None:
                    if value.keys:
                        issue = {'reason': 'missing_localization', 'keys': list(value.keys)}
                        report(issue)
                    return visit(value.fallback)
                text = display(text, source_key)
                if value.wrapper:
                    text = texts.get(value.wrapper, '{name}').replace('{name}', text)
                if value.arguments:
                    for slot, argument in visit(value.arguments).items():
                        text = text.replace('{' + slot + '}', str(argument))
                localized[id(value)] = f'§{value.color}{text}§!' if value.color else text
                return localized[id(value)]
            if isinstance(value, list):
                return [visit(entry) for entry in value]
            if isinstance(value, dict):
                if 'localized_list' in value:
                    return ', '.join(dict.fromkeys(visit(value['localized_list'])))
                if 'math' in value:
                    op, *args = visit(value['math'])
                    first = str(args[0]).strip()
                    if op == 'floor':
                        return f'⌊{first}⌋'
                    second = str(args[1]).strip()
                    if op in ('min', 'max'):
                        return f'{op}({first}; {second})'
                    return f'({first} {op} {second})'
                if 'scope_path' in value:
                    return ' → '.join(visit(part) for part in value['scope_path'])
                if 'number_format' in value:
                    number, signed, prefix, suffix = value['number_format']
                    return self.numeric(number, signed=signed, prefix=prefix, suffix=suffix)
                if value.get('kind') == 'unrecognized':
                    return value
                if '_negative_text' in value:
                    phrase = value['_negative_text']
                    if any(key in texts for key in phrase.keys):
                        child, = value['children']
                        return {**child, 'text': visit(phrase), 'negated': True}
                    visit(phrase)  # Report the missing translation and render the original NOT group.
                    return {k: visit(v) for k, v in value.items() if k != '_negative_text'}
                output = {k: visit(v) for k, v in value.items()}
                phrase = value.get('text')
                if isinstance(phrase, Label) and missing_name(phrase):
                    output['evidence'] = phrase.missing
                return output
            return value

        return {**visit(result), 'diagnostics': self.diagnostics}

    def technology(self, identifier, *, reference=False):
        return self.label(determine_key(self.rules, 'technology_name', identifier), fallback=identifier,
                          color='Y' if reference else None)

    def dlc(self, name):
        if self._dlcs is None:
            self._dlcs = {}
            for r in records(self.db, 'dlcs', ['name', 'localizable_name']):
                keys = [scalar(r['body'], 'localizable_name')]
                self._dlcs[scalar(r['body'], 'name')] = (keys, r['id'])
        keys, identifier = self._dlcs.get(name, ((name,), None))
        label = self.label(*keys, fallback=name)
        if identifier:
            label.russian_key = determine_key(self.rules, 'dlc_project_name', identifier)
            if label.russian_key:
                self.keys.add(label.russian_key)
        return label

    def policy(self, flag):
        if self._policies is None:
            self._policies = defaultdict(list)
            for r in records(self.db, 'policies', ['option']):
                for option in fields(r['body'], 'option'):
                    name = scalar(option, 'name')
                    for group in fields(option, 'policy_flags'):
                        for item in group.get('items', []):
                            if name and item.get('kind') == 'scalar':
                                pair = (r['id'], name)
                                if pair not in self._policies[item['text']]:
                                    self._policies[item['text']].append(pair)
        matches = self._policies[flag]
        if len(matches) != 1:
            self.diagnostics.append({'reason': 'policy_flag_resolution', 'flag': flag, 'matches': matches})
            return self.phrase('has_policy_flag_unresolved', flag=flag)
        policy, option = matches[0]
        return self.phrase('has_policy_flag', policy=self.label('policy_' + policy, fallback=policy),
                           option=self.label(option, fallback=option))

    def name(self, role, value):
        if role == 'technology':
            return self.technology(value)
        if role == 'dlc':
            return self.dlc(value)
        if role == 'bypass':
            if self._bypasses is None:
                self._bypasses = {r['id']: scalar(r['body'], 'name') for r in records(self.db, 'bypass', ['name'])}
            key = self._bypasses.get(value)
            if not key:
                self.diagnostics.append({'reason': 'missing_bypass_name', 'id': value})
            return self.label(key, fallback=value)
        if role in ('target', 'country', 'other') and value.lower() in ('owner', 'this', 'prev', 'species'):
            return self.phrase(value.lower())
        if role in ('target', 'country', 'other') and value.lower() in ('root', 'from'):
            return self.label('TRIGGER_' + value.upper(), fallback=value)
        if role == 'personality':
            return self.label('personality_' + value, value, fallback=value)
        if role == 'pop_category':
            return self.label('pop_cat_' + value, value, fallback=value)
        if role == 'trait' and (match := re.fullmatch(r'(leader_trait_\w+)_([2-9]\d*)', value)):
            return self.label(value, fallback=self.phrase('trait_rank', name=self.label(match[1],
                              'sttv_tooltip_name_unavailable'), value=match[2]))
        if value == 'observation_outpost_owner' and role in ('target', 'country', 'other'):
            return self.phrase(value)
        if role in ('target', 'country', 'other') and (':' in value or '.' in value):
            from .condition_text import scope_name
            return scope_name(self, value)
        if role in ('target', 'country', 'other') and (value.casefold() in ('leader', 'solar_system', 'prevprev', 'prevprevprev')
                or 'scope' in self.rules.get('condition_rules', {}).get(value.casefold(), {})):
            from .condition_text import scope_name
            return scope_name(self, value)
        keys = [value]
        if role in ('country_type', 'district_set', 'target', 'type'):
            keys.insert(0, 'sttv_tooltip_' + role + '_' + value)
        label = self.label(*keys, 'sttv_tooltip_name_unavailable', fallback=value)
        label.missing = {'reason': 'missing_object_name', 'type': role, 'id': value}
        return label
