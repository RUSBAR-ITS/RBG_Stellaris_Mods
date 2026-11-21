"""Find executable research grants and event entry points in loader documents."""

from collections import defaultdict
from dataclasses import dataclass, replace

from .acquisition_paths import recipient_issue, recipient_scope, rooted_routes
from .acquisition_mechanics import AcquisitionMechanics, POOL_COMMANDS, SHIP_CREATION
from .tree.ast import compact, fields, number


REWARD_SOURCES = ('events', 'traditions', 'council_agendas', 'astral_actions', 'resolutions',
                  'situations', 'psionic_auras')
CALLERS = ('special_projects', 'archaeological_site_types', 'anomalies', 'first_contact',
           'on_actions', 'megastructures', 'buildings', 'astral_rifts', 'artifact_actions')
COLLECTIONS = (*REWARD_SOURCES, *CALLERS, 'ascension_perks', 'crisis_levels', 'focus_rewards',
               'federation_perks', 'specialist_subject_perks', 'tradable_actions', 'patrons',
               'fallen_empires', 'solar_system_initializers')
COMMANDS = {'add_research_option': 'research_options', 'give_technology': 'researched_grants',
            'add_tech_progress': 'research_progress'}
CONDITIONS = ('trigger', 'potential', 'allow', 'possible', 'limit')
SKIP = {*CONDITIONS, 'tooltip', 'custom_tooltip', 'effect_tooltip', 'desc', 'title', 'name',
        'modifier', 'ai_weight', 'ai_chance', 'weight', 'event_weight', 'spawn_chance'}


def key(node):
    return node.get('key', {}).get('text', '')


def first(node, name):
    return next(iter(fields(node, name)), {})


def text(node, name):
    return first(node, name).get('text')


def title_keys(kind, identifier, body):
    name = text(body, 'title') or text(body, 'name')
    if kind == 'on_actions':
        return ('sttv_tooltip_progress_' + identifier, identifier)
    if kind == 'events':
        return tuple(k for k in ('sttv_tooltip_title_' + identifier, name, identifier + '.name',
                                 'sttv_tooltip_event_' + identifier) if k)
    if kind == 'council_agendas':
        return ('sttv_tooltip_title_' + identifier, 'council_agenda_' + identifier + '_name', identifier + '_name', identifier)
    if kind == 'focus_rewards':
        return ('sttv_tooltip_title_' + identifier, identifier, 'sttv_tooltip_focus_' + str(text(body, 'category')))
    if kind == 'first_contact':
        summaries = {text(stage, 'summary') for stage in fields(body, 'stage_event')}
        summary = next(iter(summaries)) if len(summaries) == 1 else None
        return tuple(k for k in ('sttv_tooltip_title_' + identifier, name, identifier, summary) if k)
    return tuple(k for k in ('sttv_tooltip_title_' + identifier, name, identifier) if k)


@dataclass(frozen=True)
class Context:
    guards: tuple = ()
    option: str | None = None
    scopes: tuple = ()
    stages: tuple = ()
    chance: tuple = ()
    debris_allowed: bool = True

    def when(self, parts, negative=False, pointer=None):
        return replace(self, guards=self.guards + tuple((negative, n, self.scopes, pointer) for n in parts
                       if negative or n.get('kind') != 'block' or n.get('items')))

    def freeze(self):
        return {'conditions': [(neg, {**compact(n), 'guard_scopes': list(scopes), 'guard_pointer': pointer})
                               for neg, n, scopes, pointer in self.guards],
                'option': self.option, 'scopes': self.scopes, 'stages': self.stages,
                'chance': self.chance}


def predicate(name, value):
    return {'kind': 'assignment', 'operator': '=', 'key': {'kind': 'scalar', 'text': name},
            'value': {'kind': 'scalar', 'text': value}}


def spawn_modifiers(body):
    chances = []
    for spawn in fields(body, 'spawn_chance'):
        for modifier in fields(spawn, 'modifier'):
            operations = [(key(n), n['value'].get('text')) for n in modifier['items']
                          if key(n) in ('add', 'factor', 'mult')]
            guards = [compact(n) for n in modifier['items'] if key(n) not in ('add', 'factor', 'mult')]
            chances.extend((op, value, guards) for op, value in operations)
    return chances


def walk(body, path, context, parent='', event_ids=frozenset()):
    """Yield only effects and calls. Branch guards are frozen only for actual hits."""
    previous = []
    stage_number = 0
    switch = text(body, 'trigger') if parent in ('switch', 'inverted_switch') else None
    for index, node in enumerate(body.get('items', [])):
        raw_name = key(node)
        name = raw_name.casefold()
        ptr = f'{path}/items/{index}'
        branch = context
        value = node.get('value', {})
        operand = value.get('text')
        weighted_success = parent == 'on_success' and number(name) is not None
        if weighted_success:
            branch = replace(branch, chance=(*branch.chance, ('weight', name)))
        if parent in ('events', 'random_events') or (weighted_success and operand is not None):
            target = node.get('text') or operand
            if target in event_ids:
                if parent == 'random_events':
                    branch = replace(branch, chance=(*branch.chance, ('weight', name)))
                yield 'event', target, 'dispatch' if parent in ('events', 'random_events') else 'anomaly_event', ptr, branch, node
            continue
        if name in SKIP or not name:
            continue
        if name in ('save_event_target_as', 'save_global_event_target_as') and operand:
            yield 'saved_target', operand, None, ptr, branch, node
        if name.endswith('_flag') and name.startswith(('set_', 'remove_')):
            flag = operand or text(value, 'flag')
            if flag:
                yield 'flag_change', flag, name, ptr, branch, node
        if name == 'create_fleet':
            branch = replace(branch, debris_allowed=not any(text(settings, 'spawn_debris') == 'no'
                             for settings in fields(value, 'settings')))
        if name in SHIP_CREATION:
            design = text(value, 'design') or text(value, 'global_design')
            if design:
                yield 'carrier', design, None, ptr, branch, node
        if name in POOL_COMMANDS:
            yield 'pool', name, compact(value), ptr, branch, node
            # A nested failure effect runs only when the pool is empty.
            for i, child in enumerate(value.get('items', [])):
                if key(child) == 'fail_effects':
                    failure = replace(branch, stages=(*branch.stages, 'empty_pool'))
                    yield from walk(child['value'], f'{ptr}/value/items/{i}/value', failure, name, event_ids)
            continue
        if name == 'start_situation' and text(value, 'type'):
            yield 'situation_target', text(value, 'type'), text(value, 'target'), ptr, branch, node
        if name == 'enable_special_project' and text(value, 'name'):
            owner = (text(value, 'owner') or 'this').casefold()
            if owner in ('root.owner', 'root.controller', 'root'):
                branch = replace(branch, scopes=tuple(owner.split('.')))
            elif owner != 'this':
                parts = owner.removeprefix('this.').split('.')
                branch = replace(branch, scopes=(*branch.scopes, *parts))
            yield 'project', text(value, 'name'), None, ptr, branch, node
            continue
        if name in ('add_research_option', 'give_technology'):
            target = operand if name == 'add_research_option' else text(value, 'tech') or operand
            yield COMMANDS[name], target, None, ptr, branch, node
            continue
        if name == 'add_tech_progress':
            target, amount = text(value, 'tech'), first(value, 'progress')
            yield 'research_progress', target, compact(amount) if amount else None, ptr, branch, node
            continue
        if name in ('if', 'else_if', 'else'):
            if name == 'if':
                previous = []
            else:
                branch = branch.when(previous, negative=True, pointer=ptr)
            limit = first(value, 'limit')
            if limit:
                branch = branch.when((limit,), pointer=ptr)
                previous.append(limit)
        elif switch:
            if name in ('on_trigger', 'trigger'):
                continue
            negative = parent == 'inverted_switch'
            branch = branch.when(previous, negative=not negative, pointer=ptr)
            if name != 'default':
                check = predicate(switch, raw_name)
                branch = branch.when((check,), negative=negative, pointer=ptr)
                previous.append(check)
        else:
            previous = []
        if name.endswith('_event') or name in ('event', 'on_success'):
            target = operand or text(value, 'id')
            if target in event_ids:
                if name == 'on_success':
                    branch = replace(branch, stages=(*branch.stages, name))
                yield 'event', target, None, ptr, branch, node
                continue
        if value.get('kind') != 'block':
            continue
        if name == 'option':
            branch = replace(branch, option=text(value, 'name'))
        if name in ('random', 'random_list', 'locked_random_list') or parent in ('random_list', 'locked_random_list'):
            if name == 'random':
                branch = replace(branch, chance=(*branch.chance, ('percent', text(value, 'chance'))))
            if parent in ('random_list', 'locked_random_list'):
                branch = replace(branch, chance=(*branch.chance, ('weight', name)))
                for mod in fields(value, 'modifier'):
                    if number(text(mod, 'factor')) == 0:
                        guard = {'kind': 'block', 'items': [n for n in mod['items'] if key(n) != 'factor']}
                        branch = branch.when((guard,), negative=True, pointer=ptr)
        if name.startswith('on_') or name in ('stage', 'approach') or parent == 'stages':
            stage = text(value, 'name') or name
            if parent == 'archaeological_site_types' and name == 'stage':
                stage_number += 1
                stage = 'archaeology_stage:' + str(stage_number)
            branch = replace(branch, stages=(*branch.stages, stage))
        scope = recipient_scope(name, parent)
        if scope:
            branch = replace(branch, scopes=(*branch.scopes, scope))
        for i, item in enumerate(value.get('items', [])):
            guard = key(item)
            if guard == 'limit' and name in ('if', 'else_if', 'else'):
                continue
            if guard in CONDITIONS and item['value'].get('kind') == 'block':
                branch = branch.when((item['value'],), pointer=f'{ptr}/value/items/{i}/value')
        yield from walk(value, ptr + '/value', branch, name, event_ids)


class ProgressSources:
    def __init__(self, technology_ids, event_ids):
        self.technology_ids = set(technology_ids)
        self.event_ids = set(event_ids)
        self.rewards = {section: defaultdict(lambda: defaultdict(list)) for section in COMMANDS.values()}
        self.grants = self.rewards['research_progress']
        self.projects = defaultdict(list)
        self.unresolved = []
        self.witness = None
        self.incoming = defaultdict(list)
        self.names = {}
        self.spawn = {}
        self.triggered = set()
        self.event_bases = {}
        self.hidden = set()
        self.event_types = {}
        self.event_choices = {}
        self.operation_incidents = {}
        self.caller_country_types = {}
        self.project_scopes = {}
        self.dlc_names = {}
        self.mechanics = AcquisitionMechanics()
        self.situation_targets = defaultdict(set)
        self.situation_starts = defaultdict(list)
        self.flag_sites = defaultdict(dict)
        self.saved_targets = defaultdict(list)

    def add(self, collection, document):
        self.witness = None
        root = document['tree']
        body = root['value']
        if text(body, 'is_test_event') == 'yes':
            return []
        identifier = document['_id'] if isinstance(document['_id'], str) else key(root)
        source = (collection, identifier)
        self.names[source] = title_keys(collection, identifier, body)
        if collection == 'special_projects':
            self.project_scopes[identifier] = text(body, 'event_scope')
        if collection == 'events':
            self.event_types[identifier] = key(root)
            # Only direct positive conjuncts constrain every route into this event.
            for guard in fields(body, 'trigger'):
                types = {text(item['value'], 'is_country_type') for item in guard.get('items', ())
                         if key(item).casefold() == 'from' and item.get('operator') == '='}
                types.discard(None)
                if len(types) == 1:
                    self.caller_country_types[identifier] = types.pop()
            # An unconditional alternative is a choice even if setup scheduled this event.
            self.event_choices[identifier] = {text(o, 'name') for o in fields(body, 'option')
                                              if text(o, 'name') and not fields(o, 'trigger')}
            if (key(root) == 'espionage_operation_event' and text(body, 'espionage_operation') == 'yes'
                    and any(text(scope, 'set_espionage_operation_progress_locked') == 'yes'
                            for effect in fields(body, 'immediate') for scope in fields(effect, 'from'))):
                self.operation_incidents[identifier] = [document['source']['file'], document['pointer']]
            if base := text(body, 'base'):
                self.event_bases[identifier] = base
            if text(body, 'hide_window') == 'yes':
                self.hidden.add(identifier)
        if collection == 'anomalies':
            self.spawn[source] = spawn_modifiers(body)
        if collection == 'events' and text(body, 'is_triggered_only') == 'yes':
            self.triggered.add(source)
        start_context = Context()
        for i, item in enumerate(body.get('items', [])):
            if key(item) in CONDITIONS and item['value'].get('kind') == 'block':
                start_context = start_context.when((item['value'],), pointer=f"{document['pointer']}/value/items/{i}/value")
        added = []
        for action, target, amount, ptr, context, node in walk(
                body, document['pointer'] + '/value', start_context,
                parent='archaeological_site_types' if collection == 'archaeological_site_types' else '',
                event_ids=self.event_ids):
            if action == 'saved_target':
                scope = context.scopes[-1] if context.scopes else key(root)
                self.saved_targets[target].append({'source': source, 'scope': scope,
                    'file': document['source']['file'], 'pointer': ptr})
                continue
            if action == 'situation_target':
                country_target = collection == 'events' and key(root) == 'country_event' and amount == 'root'
                self.situation_targets[target].add(country_target)
                self.situation_starts[target].append({**context.freeze(), 'source': source,
                    'file': document['source']['file'], 'pointer': ptr})
                continue
            if action == 'flag_change':
                verb, _, scope = amount.partition('_')
                scope = scope.removeprefix('timed_')
                self.flag_sites['has_' + scope, target][source, ptr] = {
                    'source': source, 'file': document['source']['file'], 'pointer': ptr,
                    'scope': context.scopes, 'action': amount, 'option': context.option,
                    'stages': context.stages, 'days': text(node.get('value', {}), 'days'),
                    'who': text(node.get('value', {}), 'who'),
                    'guards': [{'negated': neg, 'scope': scopes, 'pointer': pointer}
                               for neg, _, scopes, pointer in context.guards]}
                continue
            entry = {**context.freeze(), 'file': document['source']['file'], 'pointer': ptr,
                     'origin': node.get('origin'), 'source': source}
            entry['issue'] = recipient_issue(collection, key(root), context.scopes, entry['conditions'],
                                             caller=action in ('event', 'project'))
            if action == 'event':
                call = node.get('value', {})
                if collection == 'on_actions' and amount == 'dispatch':
                    entry['forwarded_scopes'] = True
                if collection == 'anomalies' and (amount == 'anomaly_event' or
                        key(node).casefold() in ('anomaly_event', 'on_success') or
                        key(node).casefold() == 'ship_event'):
                    entry['anomaly_call'] = 'ship' if key(node).casefold() == 'ship_event' else 'anomaly'
                binding = text(first(call, 'scopes'), 'from')
                if binding:
                    entry['from_binding'] = binding
                caller_scopes = first(call, 'scopes')
                explicit = {key(item).lower(): item['value']['text'] for item in caller_scopes.get('items', ())
                            if item.get('kind') == 'assignment' and item.get('operator') == '=' and
                            key(item).lower() in ('from', 'fromfrom', 'fromfromfrom', 'fromfromfromfrom') and
                            'text' in item['value']}
                if explicit:
                    entry['caller_scopes'] = explicit
                if delay := text(call, 'days'):
                    entry['delay'] = delay
                self.incoming[target].append(entry)
            elif action == 'project':
                self.projects[target].append(entry)
            elif action == 'carrier':
                entry['debris_allowed'] = context.debris_allowed
                self.mechanics.spawns[target].append(entry)
                added.append(entry)
            elif action == 'pool':
                self.mechanics.pools.append((target, amount, entry))
                added.append(entry)
            else:
                if target not in self.technology_ids or action == 'research_progress' and amount is None:
                    self.unresolved.append({'action': action, 'target': target, 'file': entry['file'],
                                            'pointer': ptr, 'reason': 'unresolved_reward_operand'})
                    continue
                if amount is not None:
                    entry['amount'] = amount
                self.rewards[action][target][source].append(entry)
                added.append(entry)
        return added

    def event_keys(self, identifier):
        keys, seen = [], set()
        while identifier and identifier not in seen:
            seen.add(identifier)
            keys.extend(self.names.get(('events', identifier), (identifier + '.name',)))
            identifier = self.event_bases.get(identifier)
        return tuple(dict.fromkeys(keys))

    def routes(self):
        if self.witness is None:
            self.resolve_call_scopes()
            self.witness = rooted_routes(self)
        return self.witness

    def resolve_call_scopes(self):
        for target, callers in self.incoming.items():
            for call in callers:
                if call['issue'] != 'unresolved_recipient':
                    continue
                kind, ident = call['source']
                scopes = call['scopes']
                resolved = False
                if kind == 'situations' and scopes == ('target',):
                    resolved = self.situation_targets[ident] == {True}
                elif kind == 'events' and self.event_types.get(target) == self.event_types.get(ident):
                    # Entering one object and returning to PREV restores the event root.
                    resolved = len(scopes) == 2 and scopes[-1] == 'prev'
                if kind == 'events' and scopes == ('from',):
                    parents = self.incoming.get(ident, ())
                    resolved = bool(parents) and all(
                        p.get('from_binding') == 'from.controller' or
                        p.get('from_binding') == 'prev' and p['scopes'][-2:] == ('random_playable_country', 'root')
                        for p in parents)
                if resolved:
                    call['issue'] = None

    def issue(self, entry):
        if entry['issue']:
            return entry['issue']
        if entry['source'] not in self.routes():
            return 'unconfirmed_source'
        return None

    @classmethod
    def build(cls, db):
        from .tree.inputs import records
        result = cls(db.technologies.distinct('_id'), db.events.distinct('_id'))
        result.mechanics.load(db)
        result.dlc_names = {r['id']: text(r['body'], 'name') for r in records(db, 'dlcs', ['name'])}
        for collection in COLLECTIONS:
            histories = {}
            with db[collection].find({}, {'pointer': 1, 'source': 1, 'tree': 1}).batch_size(12) as rows:
                for document in rows:
                    rewards = result.add(collection, document)
                    if rewards:
                        attach_origins(db, collection, document, rewards, histories)
        result.routes()
        result.index_pools()
        return result

    def index_pools(self):
        for command, definition, entry in self.mechanics.pools:
            args = {key(n): n['value'].get('text') for n in definition.get('items', [])
                    if n.get('kind') == 'assignment' and key(n) != 'fail_effects'}
            issue = self.issue(entry)
            sites = [] if issue else list(self.mechanics.pool_candidates(command, args))
            if not sites:
                domain = {'progress_all_researches': 'research_currently_in_progress',
                          'copy_techs_from': 'donor_knowledge_minus_exclusions',
                          'copy_random_tech_from': 'eligible_donor_knowledge',
                          'add_random_research_option': 'eligible_research_options'}[command]
                self.unresolved.append({'action': command, 'reason': issue or 'undetermined_campaign_pool',
                    'domain': domain, 'operand': definition, **{k: entry[k] for k in (
                        'source', 'scopes', 'file', 'pointer', 'definition', 'calls') if k in entry}})
                continue
            fraction = first(definition, 'add_progress' if command == 'add_random_research_option' else 'progress')
            section = 'researched_grants' if command == 'copy_random_tech_from' and not fraction else 'research_options'
            candidate = {**entry, 'pool': command, 'criteria': args, 'operand': definition}
            for technology in sites:
                self.rewards[section][technology][entry['source']].append(candidate)
                if fraction:
                    self.grants[technology][entry['source']].append({**candidate, 'amount': fraction})


def attach_origins(db, collection, document, rewards, histories):
    """Resolve the few origin table entries used by grants, including their original call sites."""
    locations = db[collection + '_provenance'].find_one({'_id': document['_id']},
                                                         {'origins': 1, 'spans': 1, 'files': 1, 'expansions': 1})
    source = document['source']
    file_key = (source['root'], source['file'])
    for reward in rewards:
        index = reward.pop('origin')
        if index is None:
            continue
        origin = locations['origins'][index]
        reward['definition'] = {'file': locations['files'][origin['file']],
                                'line': locations['spans'][origin['span']]['line']}
        if origin.get('expansion_id') is None:
            continue
        if file_key not in histories:
            record = db.script_history.find_one({'_id': source}, {'metadata.expansions.id': 1,
                'metadata.expansions.parent_id': 1, 'metadata.expansions.call_site.file': 1,
                'metadata.expansions.call_site.span.line': 1})
            histories[file_key] = {e['id']: e for e in record['metadata']['expansions']}
        expansion = locations['expansions'][origin['expansion_id']]
        chain = []
        while expansion:
            entry = histories[file_key][expansion]
            site = entry['call_site']
            chain.append({'file': site['file'], 'line': site['span']['line']})
            expansion = entry['parent_id']
        reward['calls'] = list(reversed(chain))
