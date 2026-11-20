"""Accept prepared profiles in process, without listeners or access to game inputs."""

import json
from time import perf_counter, sleep
from unittest.mock import patch

from pathlib import Path

from cli import arguments, save
from sttv.common.json_io import read_json
from sttv.common.paths import PRODUCT_ROOT, path_from
from sttv.enrichment.technology_tree.settings import load
from sttv.enrichment.technology_tree.operation import execute
from sttv.parallel.memory import Monitor
from sttv.service.operations import Operations
from sttv.storage.audit import audit

def main():
    args = arguments(__doc__)
    settings = load(args.variables)
    monitor_root = args.output / 'service_monitor'
    monitor_root.mkdir(exist_ok=True)
    monitor = Monitor(monitor_root)
    base = execute(args.variables)
    save(args.output, 'reference_report.json', base)
    assert base['status'] != 'failed', base['error']
    service = Operations({'history_limit': 16}, args.variables, None, settings)
    rows = []
    original_open = Path.open
    game = path_from(read_json(args.variables)['STELLARIS_ROOT'], PRODUCT_ROOT)

    def guarded_open(path, *args, **kwargs):
        assert not path.resolve().is_relative_to(game), str(path)
        return original_open(path, *args, **kwargs)

    try:
        manifest = service.manifest()
        token = service.connect({'setId': manifest['set_id'], 'snapshotRevision': manifest['snapshot_revision']})['token']
        with patch('pathlib.Path.open', guarded_open):
            for label, enabled in [('none', []), ('mixed', ['dlc002', 'dlc036']), ('all', None), ('all_reused', None)]:
                before, started = service.manifest(), perf_counter()
                job = service.start(token, {'requestId': label, 'enabled': enabled,
                    'snapshotRevision': before['snapshot_revision'], 'baseCombinationId': 'reference_default'})
                while job['status'] == 'running' and perf_counter() - started < 600:
                    sleep(0.25)
                    job = service.get(token, job['id'])
                assert job['status'] == 'completed', job.get('error')
                result = job['result']
                row = {k: result[k] for k in ('combinationId', 'counts', 'action', 'timings')}
                row.update(profile=label, seconds=perf_counter() - started,
                    coverage={k:v for k,v in result['coverage'].items() if k != 'documents'},
                    graph_statistics=dict(service.analysis_cache.analysis.graph.statistics))
                rows.append(row)
                print(json.dumps(row), flush=True)
        assert rows[-1]['action'] == 'reused'
        assert rows[1]['graph_statistics']['reused_graph']
        save(args.output, 'publication.json', rows)
    finally:
        service.close()
        monitor.close()
        save(args.output, 'service_memory.json', monitor.data)
    report = audit(settings.storage.manifest)
    save(args.output, 'audit.json', report)
    assert report['status'] == 'success', report['diagnostics']
    print(json.dumps({'audit': report['status'], 'seconds': report['timings']['total'],
                      'verified': report['coverage']['verified']}), flush=True)


if __name__ == '__main__':
    main()
