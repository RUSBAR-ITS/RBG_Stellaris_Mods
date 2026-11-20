"""Check acquisition routes and the established DLC matrix on a prepared snapshot."""

import json
from contextlib import closing
from time import perf_counter
from cli import arguments, save
from sttv.storage import open_set
from sttv.enrichment.technology_tree.settings import load
from sttv.enrichment.technology_tree.inputs import technology_input
from sttv.enrichment.technology_tree.representations import prepare
from sttv.enrichment.dlc.analysis import Analysis
from sttv.enrichment.dlc.catalog import read_catalog
from sttv.parallel.memory import Monitor

def run(args, monitor):
    settings = load(args.variables)
    reader = open_set(settings.storage.manifest)
    _, records, _ = technology_input(settings, reader)
    technologies = prepare(records, settings.combination['variants'])
    names = read_catalog(reader, settings.dlc_rules)
    analysis = Analysis(technologies, names, settings.dlc_rules, reader=reader)
    print(json.dumps({'nodes': len(analysis.graph.nodes), 'build_seconds': analysis.build_seconds,
                      'routes': len(analysis.compiler.acquisition.network.routes)}), flush=True)
    profiles = json.loads(args.profiles.read_text(encoding='utf-8'))['profiles']
    rows, read_bytes = [], reader.bytes
    for profile in profiles:
        start = perf_counter()
        result, notes = analysis.evaluate(profile['enabled'])
        rows.append({'profile': profile['profile'], 'enabled': profile['enabled'],
            'visible': sum(v['visible'] for v in result.values()), 'hidden': sorted(k for k,v in result.items() if not v['visible']),
            'seconds': perf_counter() - start})
        if profile['profile'] in ('all', 'none'):
            save(args.output, f"dlc_{profile['profile']}_analysis.json", analysis.report())
            print(json.dumps(rows[-1] | {'hidden': len(rows[-1]['hidden'])}), flush=True)
        if 'dlc036' not in profile['enabled']:
            assert not result['tech_weaver_bio_fire_rate_2']['visible']
        if 'dlc032' not in profile['enabled']:
            for suffix in ('resonator', 'overclocker', 'preserver', 'life_support', 'cogitator', 'validator'):
                assert not result['tech_lathe_' + suffix]['visible'], (profile['profile'], suffix)
            for identifier in ('tech_missiles_1', 'tech_torpedoes_1'):
                assert result[identifier]['visible'], (profile['profile'], identifier)
    assert reader.bytes == read_bytes
    reader.check_snapshot()
    acquisition = analysis.compiler.acquisition
    targets = ('tech_cosmogenesis_world', 'tech_cosmogenesis_escort')
    assert len(analysis.graph.nodes) < settings.dlc_rules['limits']['max_nodes']
    save(args.output, 'matrix.json', {'profiles': rows, 'catalog': names, 'statistics': analysis.graph.statistics,
                        'build_seconds': analysis.build_seconds, 'coverage': reader.coverage(), 'memory': monitor.data,
                        'set_id': reader.manifest['set_id'], 'snapshot_revision': reader.manifest['snapshot_revision']})
    analysis.evaluate([])
    summary = {target: {'root': acquisition.cache.get(target),
                       'value': analysis.values.get(acquisition.cache.get(target)),
                       'routes': [r for r in acquisition.network.routes if r['target'] in ('*', target)
                                  and acquisition.compatible(r, technologies[target])]} for target in targets}
    save(args.output, 'acquisition_summary.json', {'targets': summary, 'coverage': acquisition.network.coverage,
        'unknown_counts': {code: sum(n.get('unknown') == code for n in analysis.graph.nodes.values())
                           for code in {n['unknown'] for n in analysis.graph.nodes.values() if 'unknown' in n}},
        'index': reader.manifest['acquisition']['statistics']})
    print(json.dumps({'profiles': len(rows), 'target_values': {k:v['value'] for k,v in summary.items()}}), flush=True)

if __name__ == '__main__':
    args = arguments(__doc__, profiles=True)
    monitor_root = args.output / 'matrix_monitor'
    monitor_root.mkdir(exist_ok=True)
    with closing(Monitor(monitor_root)) as monitor:
        run(args, monitor)
