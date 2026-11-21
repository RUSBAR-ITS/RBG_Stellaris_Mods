"""Classify base technologies from research weight and the causes of playable rewards."""

from collections import defaultdict, deque

from ..acquisition_paths import player_predicate
from ..progress_amounts import constant, quantity
from .ast import fields, number


EVENT_ROOTS = {'events', 'anomalies', 'archaeological_site_types', 'astral_rifts', 'first_contact'}
START_ACTIONS = {'on_game_start', 'on_game_start_country'}
UNKNOWN_ISSUES = {'unconfirmed_source', 'unresolved_recipient', 'unresolved_event_recipient',
                  'unresolved_initializer_recipient'}


def root_kind(source):
    kind, identifier = source
    if kind == 'on_actions':
        return 'start' if identifier in START_ACTIONS else 'event'
    return 'event' if kind in EVENT_ROOTS else kind


def gameplay_outcome(index, entry, options):
    kind, ident = entry['source']
    if kind in ('first_contact', 'anomalies', 'archaeological_site_types', 'astral_rifts'):
        return True
    if kind in ('special_projects', 'situations'):
        return bool(set(entry.get('stages', ())) & {
            'on_success', 'on_fail', 'on_progress_complete', 'on_abort', 'on_roll_failed', 'on_cancel'})
    return bool(kind == 'events' and ident not in index.hidden and entry.get('option')
                and index.event_choices.get(ident, set()) - options)


def acquisition_causes(index, witnesses=None):
    """Propagate independent paths; a project outcome can follow an unrelated setup effect."""
    index.routes()
    execution = index.execution
    causes, outgoing = defaultdict(set), defaultdict(list)
    pending = deque()
    for source, witness in execution.items():
        if witness is None and not (source[0] == 'situations' and source[1] in index.situation_starts):
            causes[source].add(root_kind(source))
            pending.append(source)
    for kind, mapping in [('events', index.incoming), ('special_projects', index.projects),
                          ('situations', index.situation_starts)]:
        for identifier, entries in mapping.items():
            target = kind, identifier
            for entry in entries:
                source = entry['source']
                if not any(player_predicate(n, human=False) is neg for neg, n in entry['conditions']):
                    outgoing[source].append((target, entry))
    options = defaultdict(set)
    for source, edges in outgoing.items():
        for target, entry in edges:
            options[source, target].add(entry.get('option'))
    while pending:
        source = pending.popleft()
        for target, entry in outgoing[source]:
            outcome = gameplay_outcome(index, entry, options[source, target])
            for basis in tuple(sorted(causes[source])):
                result = 'event' if outcome and basis in ('start', 'artifact_actions', 'situations') else basis
                if result not in causes[target]:
                    causes[target].add(result)
                    if witnesses is not None:
                        witnesses[target, result] = source, basis, entry
                    pending.append(target)
    return causes


def weight_status(body):
    weights = {number(n.get('text')) for n in fields(body, 'weight')}
    if not weights:
        return 'unknown_weight'
    if weights != {0}:
        if len(weights) > 1:
            return 'conflicting_weights'
        return 'unknown_weight' if None in weights else 'ordinary_weight'
    for modifier in fields(body, 'weight_modifier'):
        for clause in [modifier, *fields(modifier, 'modifier')]:
            if clause.get('kind') != 'block':
                return 'unknown_add'
            for add in fields(clause, 'add'):
                value = constant(add['body']) if add.get('kind') == 'formula' else number(add.get('text'))
                if value is None:
                    return 'unknown_add'
                if value > 0:
                    return 'positive_add'
    return 'zero_weight'


def classify(index, technologies):
    witnesses = {}
    causes = acquisition_causes(index, witnesses)
    result = {}
    for tech, data in technologies.items():
        status = weight_status(index.mechanics.technologies[tech])
        sources = set()
        outcomes = set()
        paths = []
        issues = set()
        if status == 'zero_weight':
            if data['starting']:
                sources.add('start')
            for section, rewards in index.rewards.items():
                for source, entries in rewards.get(tech, {}).items():
                    options = {e.get('option') for e in entries}
                    for entry in entries:
                        issue = index.issue(entry)
                        if issue and issue not in UNKNOWN_ISSUES:
                            continue
                        if section == 'research_progress':
                            amount = quantity(entry['amount'])
                            if 'percent' in amount and number(amount['percent']) <= 0:
                                continue
                            if 'expression' in amount:
                                issue = 'unknown_progress_amount'
                            if 'per_subject' in amount and (number(amount['per_subject']) <= 0
                                                            or number(amount['maximum']) <= 0):
                                continue
                        if not issue:
                            outcomes.add(section)
                        kinds = causes.get(source)
                        incident = (source[0] == 'events' and index.operation_incidents.get(source[1])
                                    and entry.get('option') and
                                    '.'.join(entry['scopes']).split('.')[:2] == ['from', 'owner'])
                        if not kinds and incident:
                            # This option awards the owner of an operation paused for this incident.
                            kinds = {'event'}
                        if issue:
                            issues.add(issue)
                        for basis in sorted(kinds or {'unknown'}):
                            outcome = gameplay_outcome(index, entry, options)
                            method = 'event' if outcome and basis in ('start', 'artifact_actions', 'situations') else basis
                            sources.add(method)
                            chain = []
                            position = source, basis
                            while position in witnesses:
                                parent, before, call = witnesses[position]
                                chain.append([*parent, call['file'], call['pointer']])
                                position = parent, before
                            paths.append({'method': method, 'origin': position[1], 'reward': section,
                                          'source': list(source), 'file': entry['file'], 'pointer': entry['pointer'],
                                          'via': chain[::-1], **({'operation_incident': index.operation_incidents[source[1]]}
                                                                  if incident else {}), **({'issue': issue} if issue else {})})
            for design in index.mechanics.carriers.get(tech, {}):
                for site in index.mechanics.spawns.get(design, ()):
                    if (not site['debris_allowed'] or site['source'] not in index.execution or
                            any(player_predicate(n, human=False) is neg for neg, n in site['conditions'])):
                        continue
                    sources.add('debris')
                    outcomes.add('research_progress')
                    paths.append({'method': 'debris', 'design': design, 'source': list(site['source']),
                                  'file': site['file'], 'pointer': site['pointer'], 'reward': 'research_progress'})
            # An uncertain recipient on another event-only path cannot introduce a different
            # acquisition method when a playable reward has already been established.
            if ('unknown_progress_amount' in issues or not sources or 'unknown' in sources or
                    not outcomes and sources <= {'event', 'debris'}):
                status = 'unresolved_acquisition'
        marked = status == 'zero_weight' and bool(sources) and sources <= {'event', 'debris'}
        classification = {'event_only': marked}
        if status != 'ordinary_weight':
            classification['acquisition_basis'] = {'status': status, 'sources': sorted(sources),
                                                   'rewards': sorted(outcomes)}
            if paths:
                classification['acquisition_basis']['paths'] = paths
            if issues:
                classification['acquisition_basis']['issues'] = sorted(issues)
        result[tech] = classification
    return result
