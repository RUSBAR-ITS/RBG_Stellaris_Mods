"""Resolve the names and phrases used by one tooltip in a batch."""

from collections import defaultdict
from dataclasses import dataclass

from .localization import determine_key, lookup
from .tree.ast import fields, scalar
from .tree.inputs import records


@dataclass
class Label:
    keys: tuple
    fallback: str | None
    arguments: dict | None = None
    color: str | None = None
    missing: dict | None = None


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

    def label(self, *keys, fallback=None, arguments=None, color=None):
        keys = tuple(k for k in keys if k)
        self.keys.update(keys)
        return Label(keys, fallback, arguments, color)

    def phrase(self, term, **arguments):
        key = determine_key(self.rules, 'tooltip_condition', term)
        return self.label(key, fallback=term, arguments=arguments)

    def flag(self, check, identifier, section):
        specific = determine_key(self.rules, 'tooltip_condition', check + '_' + identifier)
        neutral = determine_key(self.rules, 'tooltip_condition', check)
        label = self.label(specific, neutral, fallback='…')
        label.missing = {'reason': 'missing_flag_label', 'check': check, 'flag': identifier, 'section': section}
        return label

    def resolve(self, result, reader):
        items = lookup(self.language, sorted(self.keys), reader)['items']
        texts = {item['key']: item['text'] for item in items if item['text']}

        def visit(value):
            if isinstance(value, Label):
                if value.missing and (not value.keys or value.keys[0] not in texts):
                    issue = {**value.missing, 'technology': result['technology_id']}
                    if issue not in self.diagnostics:
                        self.diagnostics.append(issue)
                text = next((texts[k] for k in value.keys if k in texts), None)
                if text is None:
                    if value.keys:
                        issue = {'reason': 'missing_localization', 'keys': list(value.keys)}
                        if issue not in self.diagnostics:
                            self.diagnostics.append(issue)
                    return value.fallback
                if value.arguments is not None:
                    text = text.format(**visit(value.arguments))
                return f'§{value.color}{text}§!' if value.color else text
            if isinstance(value, list):
                return [visit(entry) for entry in value]
            if isinstance(value, dict):
                if value.get('kind') == 'unrecognized':
                    return value
                if '_negative_text' in value:
                    phrase = value['_negative_text']
                    if any(key in texts for key in phrase.keys):
                        child, = value['children']
                        return {**child, 'text': visit(phrase), 'negated': True}
                    visit(phrase)  # Report the missing translation and render the original NOT group.
                    return {k: visit(v) for k, v in value.items() if k != '_negative_text'}
                return {k: visit(v) for k, v in value.items()}
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
                if self.language == 'ru':
                    keys.insert(0, determine_key(self.rules, 'dlc_project_name', r['id']))
                self._dlcs[scalar(r['body'], 'name')] = keys
        return self.label(*self._dlcs.get(name, (name,)), fallback=name)

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
        return self.label(value, fallback=value)
