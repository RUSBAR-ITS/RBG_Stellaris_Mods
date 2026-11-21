"""Resolve tooltip participants at their use site, keeping caller and lexical scopes separate."""

from contextlib import contextmanager
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Participant:
    kind: str
    label: object
    present: bool = False


SOURCE_ROLES = {
    'technologies': ('country', 'researching_empire'), 'crisis_levels': ('country', 'crisis_empire'),
    'ascension_perks': ('country', 'perk_empire'), 'artifact_actions': ('country', 'artifact_empire'),
    'traditions': ('country', 'tradition_empire'), 'council_agendas': ('country', 'agenda_empire'),
    'first_contact': ('first_contact', 'contact_investigation'), 'situations': ('situation', 'active_situation'),
    'archaeological_site_types': ('excavation', 'excavation'),
    'special_projects': ('project', 'research_project'), 'anomalies': ('anomaly', 'survey_anomaly'),
    'astral_rifts': ('rift', 'investigated_rift'), 'buildings': ('building', 'source_building'),
    'megastructures': ('megastructure', 'source_megastructure'),
    'focus_rewards': ('country', 'focus_empire'), 'astral_actions': ('country', 'astral_empire'),
    'fallen_empires': ('country', 'fallen_empire'),
}
EVENT_KINDS = {'country', 'fleet', 'ship', 'planet', 'system', 'leader', 'starbase', 'first_contact',
               'pop', 'espionage_operation', 'archaeological_site', 'astral_rift', 'situation'}

# The game forwards these slots directly into subscribers of each on_action.
ACTION_SLOTS = {
    'on_space_battle_won': ('victor', 'defeated_empire', 'winning_fleet', 'defeated_fleet'),
    'on_fleet_destroyed_perp': ('destroyer_empire', 'destroyed_fleet_owner', 'attacking_fleet', 'destroyed_fleet'),
    'on_ship_destroyed_perp': ('destroyer_empire', 'destroyed_ship_owner', 'attacking_ship', 'destroyed_ship'),
    'on_colony_defenders_win': ('colony_defender', 'invader_empire', 'defended_colony'),
    'on_custom_diplomacy': ('diplomacy_player', 'diplomacy_contact'),
    'on_colony_defenders_lose': ('colony_owner', 'invader_empire', 'invaded_colony'),
    'on_colony_conquer': ('invaded_colony', 'new_owner', 'previous_owner'),
    'on_ground_combat_started': ('invaded_colony', 'invader_empire'),
    'on_entering_system_first_time': ('entering_ship', 'entered_system', 'exploring_empire'),
    'on_entering_system_fleet': ('entering_fleet', 'entered_system'),
    'on_system_gained': ('new_owner', 'acquired_system', 'previous_owner'),
    'on_survey_planet': ('survey_ship', 'surveyed_planet'),
    'on_fleet_auto_move_arrival': ('arriving_fleet_owner', 'arriving_fleet', 'destination_planet'),
    'on_building_mining_station': ('construction_ship', 'mining_site'),
    'on_building_observation_station': ('construction_ship', 'observed_planet'),
    'on_gaining_station_control': ('transferred_station', 'station_planet'),
    'on_ship_disabled': ('disabled_ship', 'disabling_ship'),
    'on_planet_bombarded': ('bombarded_planet', 'bombarding_empire'),
    'on_leader_death_notify': ('leader_empire', 'deceased_leader'),
    'on_first_contact_finished': ('completed_contact', 'contacted_empire'),
    'on_blocker_cleared': ('cleared_colony',),
    'on_storm_left_system': ('cleared_system', 'departing_storm'),
}
SLOT_KINDS = {'ship': 'ship', 'fleet': 'fleet', 'planet': 'planet', 'colony': 'planet',
              'system': 'system', 'leader': 'leader', 'station': 'ship', 'storm': 'cosmic_storm', 'site': ''}
COUNT_SUBJECTS = {'count_country': 'country', 'count_playable_country': 'country', 'count_owned_fleet': 'fleet',
                  'count_system_megastructure': 'megastructure', 'count_system_planet_colony': 'planet',
                  'count_system_within_border': 'system', 'count_system_within_storm': 'system',
                  'count_controlled_ship': 'ship', 'count_owned_planet': 'planet'}


class ScopeContext:
    def __init__(self, labels, index, source, address=None, callers=(), stages=()):
        self.labels, self.index, self.source = labels, index, source
        self.address = address or {}
        self.callers = callers
        self.stages = stages
        kind, identifier = source
        if kind == 'events' and index:
            event = index.event_types.get(identifier, '').removesuffix('_event')
            if event in EVENT_KINDS:
                role, term = event, 'event_' + event
            else:
                role, term = '', 'event_participant'
        else:
            role, term = SOURCE_ROLES.get(kind, ('', 'source_participant'))
        label = labels.phrase('participant_' + term)
        if term == 'source_participant' and labels.source_title:
            label = labels.phrase('participant_in_action', action=labels.source_title(source))
        if kind == 'crisis_levels' and (level := re.fullmatch(r'crisis_cosmogenesis_level_(\d+)', identifier)):
            label = labels.phrase('participant_cosmogenesis', level=level[1])
        self.stack = [Participant(role, label, bool(role))]
        if kind == 'on_actions' and identifier in ACTION_SLOTS:
            self.stack[0] = self.action_slot(0)
        if kind == 'anomalies' and self.stages:
            participant = self.anomaly_participant(0)
            if participant:
                self.stack[0] = participant
        if kind == 'megastructures' and 'on_build_complete' in self.stages:
            self.stack[0] = Participant('system', labels.phrase('megastructure_system'), True)
        if kind == 'special_projects' and index:
            if self.project_step('on_fail', 'on_cancel'):
                self.stack[0] = Participant('country', labels.phrase('project_empire'), True)
            elif self.project_step('on_start', 'on_success', 'on_progress_25', 'on_progress_50', 'on_progress_75'):
                self.stack[0] = self.project_object()

    def project_step(self, *names):
        return self.source[0] == 'special_projects' and any(s in names for s in self.stages)

    def project_object(self):
        kind = self.index.project_scopes.get(self.source[1])
        if kind in ('ship', 'country', 'planet'):
            return Participant(kind, self.labels.phrase('project_' + kind))
        return Participant('', self.labels.phrase('project_participant'))

    def action_slot(self, depth):
        slots = ACTION_SLOTS.get(self.source[1], ())
        if depth >= len(slots):
            return self.unknown('from' * depth)
        name = slots[depth]
        kind = 'first_contact' if name == 'completed_contact' else SLOT_KINDS.get(name.rsplit('_', 1)[-1], 'country')
        return Participant(kind, self.labels.phrase('participant_' + name), depth == 0)

    def anomaly_participant(self, depth):
        if depth > 1:
            return None
        if 'spawn_chance' in self.stages or 'on_spawn' in self.stages:
            ship = depth == 1
        elif 'on_success' in self.stages:
            ship = depth == 0
        else:
            return None
        if ship:
            return Participant('ship', self.labels.phrase('surveying_ship'), True)
        return Participant('planet', self.labels.phrase('anomaly_location'), True)

    def unknown(self, value, alternatives=()):
        issue = {'reason': 'unresolved_participant', 'id': value, 'source': list(self.source), **self.address}
        self.labels.diagnostics.append(issue)
        if alternatives:
            return Participant('', self.labels.phrase('participant_alternatives', participants={'localized_list':
                               [answer.label for answer in alternatives]}))
        if self.labels.source_title:
            term = 'caller_in_action' if value.startswith('from') else 'outer_in_action'
            return Participant('', self.labels.phrase(term, action=self.labels.source_title(self.source)))
        return Participant('', self.labels.phrase('participant_caller' if value.startswith('from')
                                                 else 'participant_source_participant'))

    def caller(self, depth):
        from .condition_text import scope_parts
        kind, identifier = self.source
        if kind == 'on_actions' and identifier in ACTION_SLOTS:
            return self.action_slot(depth)
        if kind == 'anomalies' and (participant := self.anomaly_participant(depth)):
            return participant
        if kind == 'megastructures' and 'on_build_complete' in self.stages:
            if depth == 1:
                return Participant('country', self.labels.phrase('megastructure_builder'), True)
            if depth == 2:
                return Participant('megastructure', self.labels.phrase('participant_source_megastructure'), True)
            if depth == 3:
                return Participant('fleet', self.labels.phrase('megastructure_fleet'))
        if self.project_step('on_fail', 'on_cancel'):
            if depth == 1:
                return self.project_object()
            if depth == 2:
                return Participant('', self.labels.phrase('project_location'))
        if depth == 1 and self.project_step('on_start', 'on_success', 'on_progress_25', 'on_progress_50', 'on_progress_75'):
            return Participant('', self.labels.phrase('project_location'))
        if kind == 'tradable_actions' and depth == 1:
            reverse = 'on_deal_ended_recipient_effect' in self.stages
            return Participant('country', self.labels.phrase('trade_giver' if reverse else 'trade_recipient'))
        if kind == 'events' and self.index and depth == 1:
            country_type = self.index.caller_country_types.get(identifier)
            if country_type and country_type not in ('default', 'fallen_empire'):
                name = self.labels.label('sttv_tooltip_country_type_' + country_type, 'NAME_' + country_type.capitalize(),
                                         country_type, 'sttv_tooltip_role_country')
                return Participant('country', name)
        if not self.index or self.source in self.callers or self.source[0] != 'events':
            return self.unknown('from' * depth)
        calls = self.index.incoming.get(self.source[1], ())
        slot = 'from' * depth
        signatures = {(c['source'], tuple(c['scopes']), c.get('caller_scopes', {}).get(slot)
                       or (c.get('from_binding') if depth == 1 else None), c.get('forwarded_scopes'),
                       c.get('anomaly_call'), tuple(c.get('stages', ()))) for c in calls}
        if not signatures:
            return self.unknown('from' * depth)
        answers = []
        for source, scopes, binding, forward, anomaly, stages in sorted(signatures, key=repr):
            context = ScopeContext(self.labels, self.index, source, self.address, (*self.callers, self.source), stages)
            if binding:
                for step in scopes:
                    for part in scope_parts(self.labels, step):
                        context.enter(part)
                for step in binding.split('.'):
                    answer = context.enter(step)
            elif forward:
                answer = context.caller(depth)
            elif anomaly and (depth == 1 or (anomaly == 'ship' and depth == 2)):
                is_ship = anomaly == 'ship' and depth == 1
                answer = Participant('ship' if is_ship else 'planet',
                                     self.labels.phrase('surveying_ship' if is_ship else 'anomaly_location'))
            elif depth > 1:
                answer = context.caller(depth - 1)
            else:
                answer = context.stack[0]
            if answer not in answers:
                answers.append(answer)
        return answers[0] if len(answers) == 1 else self.unknown(slot, answers)

    def resolve(self, value):
        from .condition_text import literal_scope
        part = value.casefold().rstrip('?')
        current = self.stack[-1]
        if part in COUNT_SUBJECTS:
            kind = COUNT_SUBJECTS[part]
            return Participant(kind, self.labels.phrase('counted_' + kind), True)
        if part == 'this':
            return current
        if part == 'root':
            return self.stack[0]
        if re.fullmatch('(?:prev)+', part):
            offset = 1 + len(part) // 4
            if offset == len(self.stack) + 1 and self.project_step('on_start', 'on_success', 'on_progress_25',
                                                                  'on_progress_50', 'on_progress_75'):
                return Participant('country', self.labels.phrase('project_empire'))
            return self.stack[-offset] if offset <= len(self.stack) else self.unknown(part)
        if re.fullmatch('(?:from)+', part):
            return self.caller(len(part) // 4)
        if part in ('owner', 'controller', 'leader'):
            term = f'participant_{part}_{current.kind}'
            generic = self.labels.phrase('participant_' + part, subject=current.label)
            label = self.labels.label('sttv_tooltip_' + term, *generic.keys, arguments=generic.arguments)
            return Participant('leader' if part == 'leader' else 'country', label)
        label = literal_scope(self.labels, value.rstrip('?'))
        suffix = part.rsplit('_', 1)[-1]
        kind = suffix if suffix in EVENT_KINDS else ''
        if part in ('any_relation', 'any_member', 'every_member', 'any_attacker', 'any_defender'):
            kind = 'country'
        if part == 'solar_system':
            kind = 'system'
        return Participant(kind, label, bool(kind and part.startswith(('any_', 'every_', 'random_'))))

    def enter(self, value):
        role = self.resolve(value)
        self.stack.append(role)
        return role

    @contextmanager
    def nested(self, parts):
        length = len(self.stack)
        try:
            yield [self.enter(part).label for part in parts]
        finally:
            del self.stack[length:]
