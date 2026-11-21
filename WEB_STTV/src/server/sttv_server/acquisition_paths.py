"""Classify reward recipients and find rooted paths through the scripted call graph."""

from collections import defaultdict, deque

# Only effect containers known to preserve their input scope belong here.
CONTAINERS = {'immediate', 'after', 'option', 'hidden_effect', 'effect', 'if', 'else_if', 'else',
              'random', 'random_list', 'locked_random_list', 'switch', 'inverted_switch', 'while',
              'events', 'random_events', 'stage_event', 'stage', 'approach', 'tradition_swap', 'activate_effect',
              'active_accord', 'passive_accord', 'stages'}
NPC = {'create_country', 'create_rebels', 'last_created_country', 'create_country_effect'}
PLAYABLE = {'owner', 'controller', 'explorer', 'space_owner', 'every_playable_country',
            'random_playable_country', 'every_member'}


def recipient_scope(name, parent):
    name = name.casefold().rstrip('?')
    if name.startswith('on_') or name in CONTAINERS or parent in ('switch', 'inverted_switch', 'stages') or name.isdecimal():
        return None
    return name


def player_predicate(node, human=True):
    """Evaluate only facts that are fixed for a human recipient. None means undecided."""
    kind = node.get('kind')
    if kind == 'assignment':
        if node.get('operator') != '=':
            return None
        name = node['key']['text'].lower()
        value = node['value'].get('text')
        if human and name == 'is_ai' and value in ('yes', 'no'):
            return value == 'no'
        if name == 'always' and value in ('yes', 'no'):
            return value == 'yes'
        # In the surveyed vanilla country types, only default declares playable = yes.
        if human and name == 'is_country_type' and value and value.isidentifier():
            return value == 'default'
        return None
    if kind == 'block':
        op, items = 'AND', node['items']
    elif kind == 'logical_operation':
        op, items = node['operator'].upper(), node['body']['items']
    else:
        return None
    if op == 'NOT' and len(items) != 1:
        return None
    values = [player_predicate(n, human) for n in items]
    if op in ('AND', 'NAND', 'NOT'):
        result = False if False in values else None if None in values else True
    elif op in ('OR', 'NOR'):
        result = True if True in values else None if None in values else False
    else:
        return None
    return not result if result is not None and op in ('NOT', 'NAND', 'NOR') else result


def recipient_issue(collection, root, scopes, guards, *, caller=False):
    if any(player_predicate(node, human=False) is negative for negative, node in guards):
        return 'unreachable_condition'
    # A playable-country selector starts a new recipient scope, including in an initializer.
    if scopes and scopes[-1] in ('every_playable_country', 'random_playable_country', 'observation_outpost_owner'):
        if any(tuple(n.get('guard_scopes', ())) == scopes and player_predicate(n) is negative for negative, n in guards):
            return 'excluded_by_player_condition'
        return None
    if collection in ('fallen_empires', 'solar_system_initializers'):
        if any(scope in NPC for scope in scopes):
            return 'new_country_recipient'
        return 'npc_source' if collection == 'fallen_empires' else 'unresolved_initializer_recipient'
    if any(scope in NPC for scope in scopes):
        return 'new_country_recipient'
    if any(player_predicate(node) is negative for negative, node in guards):
        return 'excluded_by_player_condition'
    if scopes and scopes[-1] == 'observation_outpost_owner':
        return None
    for scope in scopes:
        if scope == 'prev' and collection == 'special_projects' and caller:
            continue
        if scope in PLAYABLE or scope == 'root':
            continue
        if scope == 'from' and collection == 'tradable_actions':
            continue
        if scope == 'target' and collection == 'specialist_subject_perks':
            continue
        return 'unresolved_recipient'
    if not caller and collection == 'events' and root != 'country_event' and not (set(scopes) & PLAYABLE):
        return 'unresolved_event_recipient'
    return None


def rooted_routes(index):
    """Keep reachable incoming calls and one acyclic upstream witness for each source."""
    outgoing = defaultdict(list)
    for event, entries in index.incoming.items():
        for entry in entries:
            if not entry['issue']:
                outgoing[entry['source']].append((('events', event), entry))
    for project, entries in index.projects.items():
        for entry in entries:
            if not entry['issue']:
                outgoing[entry['source']].append((('special_projects', project), entry))
    roots = [source for source in index.names if source not in index.triggered and
             source[0] != 'special_projects' and
             source[0] not in ('solar_system_initializers', 'fallen_empires')]
    witness = dict.fromkeys(roots)
    queue = deque(roots)
    def follow_playable():
        while queue:
            source = queue.popleft()
            for target, entry in outgoing[source]:
                if target not in witness:
                    witness[target] = entry
                    queue.append(target)
    follow_playable()
    # An event sent to an NPC can itself send a different event to a playable empire.
    # Keep execution witnesses separate from player-reward witnesses.
    executes = defaultdict(list)
    for target, callers in index.incoming.items():
        for call in callers:
            executes[call['source']].append((('events', target), call))
    for target, callers in index.projects.items():
        for call in callers:
            executes[call['source']].append((('special_projects', target), call))
    execution_roots = [s for s in index.names if s not in index.triggered and s[0] != 'special_projects']
    execution = dict.fromkeys(execution_roots)
    pending = deque(execution_roots)
    while pending:
        current = pending.popleft()
        for target, call in executes[current]:
            if target not in execution and not any(
                player_predicate(node, human=False) is negative for negative, node in call['conditions']
            ):
                execution[target] = call
                pending.append(target)
    index.execution = execution
    for source in execution:
        for target, call in outgoing[source]:
            if call['scopes'] and call['scopes'][-1] in ('every_playable_country', 'random_playable_country',
                                                        'observation_outpost_owner') and target not in witness:
                witness[target] = call
                queue.append(target)
    follow_playable()
    return witness
