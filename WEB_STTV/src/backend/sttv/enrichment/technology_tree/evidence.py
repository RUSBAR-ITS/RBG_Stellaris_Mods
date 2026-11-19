"""Prepare shared evidence once; own-effect comparisons remain variant-aware."""

from dataclasses import dataclass, field
from . import economy, groups, relations
from .inputs import Catalog
from .projections import Projections


@dataclass
class Evidence:
    witnesses: dict = field(default_factory=dict)
    groups: dict = field(default_factory=dict)
    production: dict = field(default_factory=dict)
    capacity: dict = field(default_factory=dict)


def prepare(catalog, technologies, rules, weapon_routes=()):
    result = Evidence()
    for rule in rules['rules']:
        if not rule['enabled']:
            continue
        key, options = rule['id'], rule['parameters']
        if key in ('direct_upgrades', 'direct_relations', 'indirect_affinity'):
            handler = {'direct_upgrades': relations.upgrades, 'direct_relations': relations.direct,
                       'indirect_affinity': relations.indirect}[key]
            result.witnesses[key] = handler(catalog, technologies, options)
        elif key == 'functional_groups':
            result.groups = groups.collect(catalog, technologies, options, weapon_routes)
        elif key == 'production_affinity':
            result.production = economy.production_index(catalog, options)
        elif key == 'capacity_affinity':
            result.capacity = economy.capacity_index(catalog, options)
    return result


def load(settings, technologies, reader):
    with Projections(reader, settings.storage.workers) as projections:
        records = projections.load([kind for kind in settings.registry if kind not in ('technologies', 'events')])
        records['technologies'] = list(technologies.values())
        catalog = Catalog(records)
        functional = next((r for r in settings.rules['rules'] if r['id'] == 'functional_groups' and r['enabled']), None)
        route_list = groups.routes(catalog, technologies, functional['parameters']['weapon']) if functional else []
        wanted = {event for route in route_list for event in route['events']}
        records.update(projections.load(['events'], wanted))
    catalog = Catalog(records)
    return prepare(catalog, technologies, settings.rules, route_list)
