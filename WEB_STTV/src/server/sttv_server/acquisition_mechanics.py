"""Identify conditional acquisition through ship equipment and research pools."""

from collections import defaultdict, deque
from functools import cache
import json
from pathlib import Path

from .tree.ast import fields, number, prerequisite, references, requirements
from .acquisition_paths import player_predicate


POOL_COMMANDS = {'add_random_research_option', 'copy_random_tech_from', 'copy_techs_from',
                 'progress_all_researches'}
SHIP_CREATION = {'create_ship', 'create_multiple_voidworm_ship', 'create_voidworm_ship',
                 'create_voidworm_fleet'}


@cache
def acquisition_rules():
    return json.loads((Path(__file__).resolve().parents[1] / 'config/acquisition_rules.json').read_bytes())


def values(body, name):
    return [v.get('text') for v in fields(body, name)]


def draw_blocked(body):
    """Prove a zero draw weight only in simple, entirely multiplicative definitions."""
    weights = values(body, 'weight')
    blocks = fields(body, 'weight_modifier')
    if len(weights) > 1:
        return False
    zero = len(weights) == 1 and number(weights[0]) == 0
    for block in blocks:
        for node in block.get('items', []):
            key = node.get('key', {}).get('text')
            if key == 'factor':
                zero |= number(node['value'].get('text')) == 0
                continue
            if key != 'modifier':
                return False
            items = node['value'].get('items', [])
            if any(item.get('key', {}).get('text') == 'add' for item in items):
                return False
            if any(number(v) == 0 for v in values(node['value'], 'factor')) and all(
                item.get('key', {}).get('text') == 'factor' or
                item.get('key', {}).get('text') == 'always' and item['value'].get('text') == 'yes'
                for item in items
            ):
                zero = True
    return zero


class AcquisitionMechanics:
    def __init__(self):
        self.technologies = {}
        self.carriers = defaultdict(lambda: defaultdict(set))
        self.spawns = defaultdict(list)
        self.pools = []
        self.blocked = set()
        self.diagnostics = []

    def load(self, db):
        from .tree.inputs import records
        self.technologies = {r['id']: r['body'] for r in records(db, 'technologies', [
            'prerequisites', 'is_reverse_engineerable', 'area', 'category', 'is_rare', 'is_insight',
            'is_insight_tech', 'tier', 'weight', 'weight_modifier', 'can_be_stolen', 'potential'])}
        self.blocked = {t for t, b in self.technologies.items() if draw_blocked(b)}
        by_component = {}
        for r in records(db, 'components', ['prerequisites', 'is_reverse_engineerable']):
            req = references(prerequisite(r['body']))
            if len(req) > 1:
                self.diagnostics.append({'reason': 'multiple_component_prerequisites',
                                         'component': r['id'], 'technologies': sorted(req)})
            if len(req) == 1 and 'no' not in values(r['body'], 'is_reverse_engineerable'):
                tech, = req
                if tech in self.technologies and 'no' not in values(self.technologies[tech], 'is_reverse_engineerable'):
                    by_component[r['id']] = tech
        for r in records(db, 'global_ship_designs', ['section', 'required_component']):
            parts = set(values(r['body'], 'required_component'))
            for section in fields(r['body'], 'section'):
                for slot in fields(section, 'component'):
                    parts.update(values(slot, 'template'))
            for component in parts & by_component.keys():
                self.carriers[by_component[component]][r['id']].add(component)

    def indirect(self, technology):
        """Follow prerequisites up to blocked draws, keeping alternative paths conditional."""
        found, visited = {}, {technology: True}
        queue = deque([(technology, True)])
        while queue:
            current, required = queue.popleft()
            all_ids, mandatory, _ = requirements(prerequisite(self.technologies.get(current, {})), strict=False)
            for parent in sorted(all_ids - {technology}):
                certain = required and parent in mandatory
                if parent in self.blocked:
                    found[parent] = found.get(parent, False) or certain
                elif parent not in visited or certain and not visited[parent]:
                    visited[parent] = certain
                    queue.append((parent, certain))
        return sorted(found.items())

    def pool_candidates(self, command, args):
        """A campaign-wide effect without a bounded pool has no individual technology address."""
        if command not in ('add_random_research_option', 'copy_random_tech_from'):
            return
        if not any(args.get(k) for k in ('category', 'area', 'tier')) and args.get('only_rare') != 'yes':
            return
        supported = ({'category', 'area', 'tier', 'add_progress', 'ignore_rare', 'only_rare',
                      'ignore_insight', 'ignore_prereqs'} if command == 'add_random_research_option'
                     else {'category', 'area', 'who', 'progress'})
        if args.keys() - supported or command == 'copy_random_tech_from' and not args.get('who'):
            return
        for key in ('ignore_rare', 'only_rare', 'ignore_insight', 'ignore_prereqs'):
            if key in args and args[key] not in ('yes', 'no'):
                return
        for tech, body in self.technologies.items():
            # A generic pool supplies no evidence for including event-only or prohibited entries.
            if tech in self.blocked or any(player_predicate(n) is False for n in fields(body, 'potential')):
                continue
            if any(args[k] not in values(body, k) for k in ('area', 'tier') if k in args):
                continue
            cats = {v for n in fields(body, 'category') for v in references(n)}
            if 'category' in args and args['category'] not in cats:
                continue
            if command == 'copy_random_tech_from':
                if 'no' in values(body, 'can_be_stolen'):
                    continue
            else:
                rare = 'yes' in values(body, 'is_rare')
                if (rare and args.get('ignore_rare', 'yes') == 'yes' or
                        not rare and args.get('only_rare') == 'yes'):
                    continue
                if args.get('ignore_insight', 'yes') == 'yes' and any(
                    'yes' in values(body, k) for k in ('is_insight', 'is_insight_tech')
                ):
                    continue
            yield tech
