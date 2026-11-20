"""Generate and verify DLC combinations on a prepared technology snapshot."""

from collections import defaultdict
import json
from time import perf_counter

from cli import arguments, save
from sttv.enrichment.dlc.analysis import Analysis
from sttv.enrichment.dlc.catalog import read_catalog
from sttv.enrichment.technology_tree.inputs import technology_input
from sttv.enrichment.technology_tree.representations import prepare
from sttv.enrichment.technology_tree.settings import load
from sttv.storage import open_set
from sttv.parallel.memory import Monitor


def mixed_profiles(nodes, catalog):
    parents, leaves = defaultdict(list), defaultdict(list)
    for key, node in nodes.items():
        for child in node['children']:
            parents[child].append(key)
        if node['op'] == 'dlc':
            leaves[node['dlc_id']].append(key)

    # A gate depends on a DLC if any leaf for that DLC can reach it through parents.
    dependencies = defaultdict(set)
    for identifier, starts in leaves.items():
        visited, pending = set(), starts.copy()
        while pending:
            key = pending.pop()
            if key in visited:
                continue
            visited.add(key)
            if nodes[key]['op'] in ('AND', 'OR', 'NOR', 'NAND'):
                dependencies[key].add(identifier)
            pending.extend(parents[key])
    return {tuple(sorted(ids)) for ids in dependencies.values() if 1 < len(ids) < len(catalog)}


def matrix(variables, output):
    settings = load(variables)
    reader = open_set(settings.storage.manifest)
    _, records, _ = technology_input(settings, reader)
    technologies = prepare(records, settings.combination['variants'])
    names = read_catalog(reader, settings.dlc_rules)
    monitor_path = output / 'matrix_monitor'
    monitor_path.mkdir(exist_ok=True)
    monitor = Monitor(monitor_path)
    try:
        analysis = Analysis(technologies, names, settings.dlc_rules, reader=reader)
        ids, profiles = sorted(names), {}
        def add(label, enabled):
            profiles.setdefault(tuple(sorted(enabled)), label)
        add('all', ids)
        add('none', [])
        for identifier in ids:
            add('without_' + identifier, set(ids) - {identifier})
            add('only_' + identifier, [identifier])
        mixed = mixed_profiles(analysis.graph.nodes, ids)
        for i, dlcs in enumerate(sorted(mixed)):
            add(f'mixed_{i}', dlcs)
            add(f'mixed_complement_{i}', set(ids) - set(dlcs))
        reports, initial_bytes = [], reader.bytes
        for enabled, label in profiles.items():
            start = perf_counter()
            result, notes = analysis.evaluate(enabled)
            bio = next(key for key, name in names.items() if name == 'BioGenesis')
            if bio not in enabled:
                assert not result['tech_weaver_bio_fire_rate_2']['visible'], label
            row = {'profile': label, 'enabled': enabled, 'visible': sum(v['visible'] for v in result.values()),
                   'hidden': sorted(k for k, v in result.items() if not v['visible']),
                   'seconds': perf_counter() - start}
            reports.append(row)
            if label in ('all', 'none'):
                save(output, f'dlc_{label}_analysis.json', analysis.report())
        assert reader.bytes == initial_bytes
        reader.check_snapshot()
        save(output, 'matrix.json', {'profiles': reports, 'catalog': names, 'mixed_dependency_sets': sorted(mixed),
                            'statistics': analysis.graph.statistics, 'build_seconds': analysis.build_seconds,
                            'coverage': reader.coverage(), 'memory': monitor.data})
        print(json.dumps({'matrix_profiles': len(reports), 'build_seconds': analysis.build_seconds,
                          'nodes': len(analysis.graph.nodes), 'read_documents': len(analysis.library.loaded)}), flush=True)
    finally:
        monitor.close()


if __name__ == '__main__':
    args = arguments(__doc__)
    matrix(args.variables, args.output)
