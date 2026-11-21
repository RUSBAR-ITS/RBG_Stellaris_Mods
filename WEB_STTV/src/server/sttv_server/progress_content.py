"""Localize research rewards and their conditions for the applied DLC selection."""

from decimal import Decimal
import json

from .acquisition_mechanics import acquisition_rules
from .condition_text import scope_name, scope_parts
from .tooltip_scopes import ScopeContext
from .progress_amounts import quantity
from .progress_sources import key
from .technology_tooltip import Content
from .localization import determine_key


def line(text, children=()):
    return {'kind': 'progress', 'text': text, 'children': list(children)}


class ProgressContent(Content):
    def __init__(self, labels, index, enabled):
        super().__init__(labels, index)
        self.enabled = enabled

    def node(self, node, path):
        name = key(node).casefold()
        operand = node.get('value', {}).get('text')
        if name in ('has_tech_option', 'last_increased_tech') and operand:
            return self.term('condition', name, technology=self.labels.technology(operand, reference=True))
        if name in ('current_situation_approach', 'is_situation_type') and operand:
            return self.term('condition', 'progress_' + name, name=self.labels.label(operand, fallback=operand))
        if name in ('host_has_dlc', 'has_dlc') and operand:
            if operand not in self.index.dlc_names.values():
                return self.unknown(node)
            disabled = self.enabled is not None and operand not in self.enabled
            condition = self.term('condition', 'progress_dlc_disabled' if disabled else 'progress_dlc',
                                  dlc=self.labels.dlc(operand))
            condition['text'].disabled_dlc = operand
            key_name = determine_key(self.labels.rules, 'tooltip_condition', 'progress_dlc_disabled')
            if key_name:
                self.labels.keys.add(key_name)
            return condition
        return super().node(node, path)

    def conditions_for(self, guards, entry, *, stages=None):
        result, previous = [], []
        for negative, node in guards:
            self.origin = {'object': list(entry['source']), 'file': entry['file'],
                           'pointer': node.get('guard_pointer') or entry['pointer']}
            self.labels.scope = ScopeContext(self.labels, self.index, entry['source'], self.origin,
                                             stages=entry['stages'] if stages is None else stages)
            scopes = node.get('guard_scopes', ())
            headings = [self.scoped_step(s, recipient=False) for s in scopes]
            condition = self.node(node, (self.section,))
            if condition:
                for i in reversed(range(len(scopes))):
                    scope = scopes[i]
                    condition = {'kind': 'scope', 'key': scope,
                                 'text': headings[i],
                                 'children': [condition]}
                if node.get('guard_pointer'):
                    condition['address'] = self.origin.copy()
            group = previous if negative else result
            if condition and condition not in group:
                group.append(condition)
        if previous:
            result.insert(0, line(self.labels.phrase('progress_excluded'), previous))
        return result

    def circumstances(self, entry):
        result = []
        self.labels.scope = ScopeContext(self.labels, self.index, entry['source'],
                                         {k: entry[k] for k in ('file', 'pointer')}, stages=entry['stages'])
        for scope in entry['scopes']:
            self.scoped_step(scope, recipient=False)
        if entry.get('delay'):
            result.append(line(self.labels.phrase('progress_delay_days', value=entry['delay'])))
        if entry.get('from_binding'):
            result.append(line(self.labels.phrase('progress_call_from', name=scope_name(self.labels, entry['from_binding']))))
        if entry.get('pool'):
            result.extend(self.pool_conditions(entry))
        if entry['option']:
            result.append(line(self.labels.phrase('progress_choose', name=self.labels.label(entry['option'], 'sttv_tooltip_source_unknown_option'))))
        for stage in entry['stages']:
            result.append(line(self.stage_name(entry['source'], stage)))
        for kind, value in entry['chance']:
            phrase = 'progress_random_' + kind if value else 'progress_random'
            result.append(line(self.labels.phrase(phrase, value=value or '')))
        return result

    def pool_conditions(self, entry):
        args = entry['criteria']
        command = entry['pool']
        result = [line(self.labels.phrase(command))]
        for k in ('area', 'category', 'tier'):
            if k in args:
                value = self.labels.label(determine_key(self.labels.rules, 'research_area', args[k])) if k == 'area' else (
                    self.labels.label(args[k]) if k == 'category' else args[k])
                result.append(line(self.labels.phrase('pool_' + k, value=value)))
        if command == 'add_random_research_option':
            for k, default in [('ignore_prereqs', 'no'), ('ignore_rare', 'yes'), ('only_rare', 'no'), ('ignore_insight', 'yes')]:
                if k == 'only_rare' and args.get(k, default) == 'no':
                    continue
                result.append(line(self.labels.phrase('pool_' + k + '_' + args.get(k, default))))
            if any(key(n) == 'fail_effects' for n in entry['operand'].get('items', [])):
                result.append(line(self.labels.phrase('pool_empty')))
        elif args.get('who'):
            result.append(line(self.labels.phrase('pool_donor', name=scope_name(self.labels, args['who']))))
        return result

    def scoped_step(self, scope, *, recipient):
        for part in scope_parts(self.labels, scope):
            role = self.labels.scope.enter(part)
        if scope == 'every_playable_country':
            return self.labels.phrase('matching_empire' if recipient else 'empire_under_test')
        return role.label

    def recipient(self, entry):
        self.labels.scope = ScopeContext(self.labels, self.index, entry['source'],
                                         {k: entry[k] for k in ('file', 'pointer')}, stages=entry['stages'])
        label = self.labels.scope.stack[0].label
        for scope in entry['scopes']:
            label = self.scoped_step(scope, recipient=True)
        return line(self.labels.phrase('progress_recipient', name=label))

    def amount(self, node):
        item = quantity(node)
        fmt = self.labels.numeric
        if 'percent' in item:
            return fmt(item['percent'], prefix='+', suffix='%')
        if 'per_subject' in item:
            return self.labels.phrase('progress_subjects', rate=fmt(item['per_subject']), maximum=fmt(item['maximum']))
        self.labels.diagnostics.append({'reason': 'unknown_progress_amount', 'expression': node})
        return self.labels.phrase('progress_variable')

    def path_entry(self, entry):
        source = entry['source']
        description = [*self.circumstances(entry), *self.conditions_for(entry['conditions'], entry)]
        for op, value, guards in self.index.spawn.get(source, ()):
            sign = '+' if op == 'add' and value and not value.startswith('-') else '×' if op != 'add' else ''
            description.append(line(self.labels.phrase('progress_spawn_weight', value=sign + (value or '?')),
                                    self.conditions_for(((False, g) for g in guards), entry, stages=('spawn_chance',))))
        return {**line(self.name(source), description), 'source': list(source),
                'address': {'file': entry['file'], 'pointer': entry['pointer']}}

    def incoming(self, source):
        edges = self.index.incoming if source[0] == 'events' else self.index.projects
        routes = self.index.routes()
        paths = []
        for entry in edges.get(source[1], ()):
            parent = entry['source']
            upstream = routes
            if parent not in routes and entry['scopes'] and entry['scopes'][-1] in (
                'every_playable_country', 'random_playable_country', 'observation_outpost_owner'
            ):
                upstream = self.index.execution
            if entry['issue'] or parent not in upstream or parent == source:
                continue
            route = self.path_entry(entry)
            visited = {source, parent}
            child = route
            while ancestor := upstream.get(parent):
                next_parent = ancestor['source']
                if upstream is routes and next_parent not in routes and ancestor['scopes'] and ancestor['scopes'][-1] in (
                    'every_playable_country', 'random_playable_country', 'observation_outpost_owner'
                ):
                    upstream = self.index.execution
                parent = next_parent
                if parent in visited:
                    break
                visited.add(parent)
                kind, target = child['source']
                siblings = self.index.incoming if kind == 'events' else self.index.projects
                alternatives = [e for e in siblings.get(target, ())
                                if e['source'] == parent and not e['issue']]
                step = (line(self.name(parent), [line(self.labels.phrase('or'),
                        [self.path_entry(e) for e in alternatives])]) if len(alternatives) > 1
                        else self.path_entry(ancestor))
                step['children'].append(child)
                step.setdefault('source', list(parent))
                child = step
            else:
                paths.append(child)
        return paths

    def sections(self, technology, section='research_progress'):
        self.section = section
        groups = []
        for source, entries in sorted(self.index.rewards[section].get(technology, {}).items()):
            rewards = []
            for entry in entries:
                reason = self.index.issue(entry)
                if reason:
                    self.labels.diagnostics.append({'reason': reason, 'section': section, 'source': list(source),
                                                    'address': {k: entry[k] for k in
                                                        ('file', 'pointer', 'definition', 'calls') if k in entry}})
                else:
                    rewards.append(entry)
            if not rewards:
                continue
            common = [c for c in rewards[0]['conditions'] if all(c in r['conditions'] for r in rewards[1:])]
            shared = self.conditions_for(common, rewards[0])
            same_scope = all(r['scopes'] == rewards[0]['scopes'] for r in rewards)
            if same_scope:
                shared.insert(0, self.recipient(rewards[0]))
            paths = self.incoming(source) if source[0] in ('events', 'special_projects') else []
            if paths:
                shared.insert(0, paths[0] if len(paths) == 1 else line(self.labels.phrase('or'), paths))
            common_context = all(all(r.get(k) == rewards[0].get(k) for k in ('option', 'stages', 'chance', 'pool', 'criteria', 'operand')) for r in rewards)
            if common_context:
                shared.extend(self.circumstances(rewards[0]))
            for entry in rewards:
                details = [] if common_context else self.circumstances(entry)
                if not same_scope:
                    details.append(self.recipient(entry))
                details.extend(self.conditions_for((c for c in entry['conditions'] if c not in common), entry))
                reward = line(self.amount(entry['amount']), details) if 'amount' in entry else line(
                    self.labels.phrase('acquisition_' + section), details)
                reward['address'] = {k: entry[k] for k in ('file', 'pointer', 'definition', 'calls') if k in entry}
                reward['method'] = entry.get('pool', 'named')
                shared.append(reward)
            outcomes = []
            for entry in rewards:
                result = self.amount(entry['amount']) if 'amount' in entry else self.labels.phrase('acquisition_' + section)
                if result not in outcomes:
                    outcomes.append(result)
            beneficiaries = []
            for entry in rewards:
                label = self.recipient(entry)['text']
                if label not in beneficiaries:
                    beneficiaries.append(label)
            summary = list(beneficiaries)
            option = rewards[0]['option']
            if option and all(entry['option'] == option for entry in rewards):
                summary.append(self.labels.phrase('progress_choose', name=self.labels.label(
                    option, 'sttv_tooltip_source_unknown_option')))
            if all(entry.get('pool') for entry in rewards):
                summary.append(self.labels.phrase('progress_pool_selection'))
            groups.append({**line(self.name(source), shared), 'source': list(source),
                           'summary': [*summary, *outcomes]})
        if section == 'research_progress':
            groups.extend(self.debris(technology))
        return groups

    def debris(self, technology):
        groups = []
        for design, components in sorted(self.index.mechanics.carriers.get(technology, {}).items()):
            sites = [e for e in self.index.mechanics.spawns[design] if e['debris_allowed']]
            if not sites:
                continue
            carrier = self.labels.label(design, 'sttv_tooltip_name_unavailable', color='Y')
            details = [line(self.labels.phrase('debris_conditions'))]
            for component in sorted(components):
                details.append(line(self.labels.phrase('debris_equipment', name=self.labels.label(
                    component, 'sttv_tooltip_name_unavailable', color='Y'))))
            identical = {}
            for site in sites:
                context = {key: site[key] for key in ('source', 'conditions', 'scopes', 'stages', 'option', 'chance')}
                signature = json.dumps(context, sort_keys=True)
                if signature not in identical:
                    node = self.path_entry(site)
                    node['sites'] = []
                    identical[signature] = node
                    details.append(node)
                identical[signature]['sites'].append({k: site[k] for k in ('file', 'pointer', 'definition', 'calls') if k in site})
            rule = acquisition_rules()['debris']
            percent = format((Decimal(rule['fraction']) * 100).normalize(), 'f')
            groups.append({**line(self.labels.phrase('debris_carrier', name=carrier), details),
                           'source': ['global_ship_designs', design],
                           'basis': rule,
                           'summary': [self.labels.phrase('debris_progress', value=self.labels.numeric(percent))]})
        return groups
