"""Calculation over one published input revision, shared by subsequent DLC selections."""

import logging
from time import perf_counter

from ..localization import determine_key, lookup
from .availability import Analysis
from .inputs import load_inputs
from .layout import place
from .selection import criterion
from .event_technologies import classify


log = logging.getLogger(__name__)


class PreparedTree:
    def __init__(self, db, options, key_rules, read_strings, acquisition):
        self.options = options
        self.names, self.techs, catalog, self.evidence = load_inputs(db, options)
        self.analysis = Analysis(self.techs, self.names, options['dlc'], catalog)
        self.event_classes = classify(acquisition(), self.techs)
        for tech, classification in self.event_classes.items():
            basis = classification.get('acquisition_basis')
            if basis and basis['status'].startswith(('unknown', 'unresolved', 'conflicting')):
                log.warning('tree_acquisition tech=%s basis=%s', tech, basis)
        self.ranks = {}
        keys = {tech: determine_key(key_rules, 'technology_name', tech) for tech in self.techs}
        for language, locale in options['layout']['sort_locales'].items():
            rows = lookup(language, list(keys.values()), read_strings)['items']
            titles = {r['key']: r['text'] for r in rows}
            values = []
            for tie, (tech, key) in enumerate(sorted(keys.items())):
                title = titles[key]
                values.append({'id': tech, 'title': title if title is not None else f'⟦{key}⟧', 'tie': tie})
            ordered = db.aggregate([{'$documents': values}, {'$sort': {'title': 1, 'tie': 1}}],
                                   collation={'locale': locale})
            self.ranks[language] = {row['id']: i for i, row in enumerate(ordered)}

    def availability(self, enabled):
        graph = self.analysis.graph
        values = graph.evaluate(enabled)
        nodes = {}
        for key, roots in self.analysis.roots.items():
            potential = roots['potential']
            hidden = values[potential] is False and graph.baseline[potential] is not False
            hidden |= any(values[w] is True and graph.baseline[w] is not True for w in roots['weights'])
            nodes[key] = {'_id': key, 'availability': not hidden, 'area': self.techs[key]['area'],
                          **self.event_classes[key], 'layout_area': None,
                          'parent_tech': None, 'children': [], 'location': None if hidden else {}}
            if not hidden:
                unknown = set()
                pending = [potential, *roots['weights']]
                visited = set()
                while pending:
                    index = pending.pop()
                    if index in visited or values[index] is not None:
                        continue
                    visited.add(index)
                    node = graph.nodes[index]
                    if node.get('unknown'):
                        unknown.add((node['unknown'], node.get('pointer', ''), node.get('target', '')))
                    pending.extend(node['children'])
                if unknown:
                    log.info('tree_condition_unknown tech=%s conditions=%s', key, sorted(unknown, key=str))
        return nodes, values

    def parents(self, nodes, values, settings):
        compiler = self.analysis.compiler
        context = self.options, lambda n, scope: values.get(compiler.compiled.get((id(n), scope)))
        for key, row in nodes.items():
            if not row['availability']:
                continue
            tech = self.techs[key]
            current = [p for p in tech['parents'] if nodes[p]['availability']]
            for rule in self.options['parent_rules']:
                if len(current) < 2:
                    break
                if rule['enabled'] and not (rule['id'] == 'same_area' and settings['mixed_trees']):
                    matches, witnesses, unknown = criterion(rule, tech, current, self.techs, self.evidence, context)
                    if rule['id'] == 'standard_empire':
                        log.info('empire_context settings=%s tech=%s candidates=%s branches=%s', settings, key, current, witnesses)
                    if matches and not unknown:
                        current = matches
            if len(current) == 1:
                row['parent_tech'] = current[0]
                nodes[current[0]]['children'].append(key)
            elif tech['parents']:
                log.warning('%s settings=%s tech=%s candidates=%s', 'ambiguous_parent' if current else 'no_visible_parent',
                            settings, key, current or tech['parents'])
        for row in nodes.values():
            row['children'].sort()

    def build(self, enabled, settings):
        started = perf_counter()
        nodes, values = self.availability(enabled)
        first = perf_counter()
        self.parents(nodes, values, settings)
        second = perf_counter()
        place(nodes, self.techs, self.ranks, self.options['layout'], settings['mixed_trees'])
        if settings['hide_event_technologies']:
            for row in nodes.values():
                if row['event_only']:
                    row['availability'] = False
        return list(nodes.values()), {'availability': first - started, 'parents': second - first,
                                      'layout': perf_counter() - second}
