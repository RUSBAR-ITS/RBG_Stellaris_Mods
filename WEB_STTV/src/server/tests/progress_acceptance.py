"""Compare indexed grants from a parser snapshot with an independent source inventory."""

import argparse
from collections import Counter
from decimal import Decimal
import json
from pathlib import Path

from sttv_server.progress_sources import ProgressSources, REWARD_SOURCES, key, text
from sttv_server.progress_amounts import quantity


def compare(snapshot, inventory):
    baseline = json.loads(inventory.read_bytes())
    branches = [b for b in baseline['branches'] if b['command'] == 'add_tech_progress'
                and b['status'] == 'source_branch']
    expected = Counter((b['target'], b['source'], format(Decimal(b['percent']).normalize(), 'f')
                        if b['percent'] is not None else b['progress']) for b in branches)
    techs = {key(n) for p in (snapshot / 'common/technology').glob('*.json')
             for n in json.loads(p.read_bytes())['items'] if n.get('value', {}).get('kind') == 'block'}
    found = Counter()
    for collection in REWARD_SOURCES:
        folder = {'events': 'events', 'psionic_auras': 'common/patrons/psionic_auras'}.get(
            collection, 'common/' + collection)
        for path in sorted((snapshot / folder).glob('*.json')):
            raw = path.read_bytes()
            if b'"add_tech_progress"' not in raw:
                continue
            result = ProgressSources(techs, ())
            data = json.loads(raw)
            del raw
            for i, node in enumerate(data['items']):
                body = node.get('value', {})
                if body.get('kind') != 'block':
                    continue
                identifier = text(body, 'id') if collection == 'events' else key(node)
                if identifier:
                    result.add(collection, {'_id': identifier, 'pointer': f'/items/{i}', 'tree': node,
                                            'source': data['source']})
            for target, sources in result.grants.items():
                for (_, source), rewards in sources.items():
                    for reward in rewards:
                        amount = quantity(reward['amount'])
                        value = ('value:experimental_testing_insight_gain' if 'per_subject' in amount
                                 else amount.get('percent', 'unknown'))
                        found[target, source, value] += 1
            del data, result
    missing, extra = expected - found, found - expected
    print(json.dumps({'technologies': len({tech for tech, source, value in found}), 'branches': found.total(),
                      'missing': [[*k, count] for k, count in missing.items()],
                      'extra': [[*k, count] for k, count in extra.items()]}, indent=2))
    return int(bool(missing or extra))


def compare_callers(snapshot, inventory):
    baseline = json.loads(inventory.read_bytes())
    events = {b['source'] for b in baseline['branches'] if b['source_type'] == 'event'
              and b['command'] == 'add_tech_progress' and b['status'] == 'source_branch'}
    files = {snapshot / Path(ref['file']).with_suffix('.json') for event in events
             for ref in baseline['incoming_event_references'][event]}
    files = {path for path in files if path.is_file()}
    for directory in ('situations', 'astral_rifts'):
        files.update((snapshot / 'common' / directory).glob('*.json'))
    confirmed = set()
    for path in sorted(files):
        index = ProgressSources([], events)
        data = json.loads(path.read_bytes())
        for i, node in enumerate(data['items']):
            if node.get('value', {}).get('kind') == 'block':
                index.add(path.parent.name, {'_id': key(node), 'tree': node,
                          'source': data['source'], 'pointer': f'/items/{i}'})
        confirmed.update(index.incoming)
        del index, data
    missing = sorted(events - confirmed)
    print(json.dumps({'files': len(files), 'confirmed': len(confirmed), 'missing': missing}))
    return int(bool(missing))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('inventory', type=Path)
    parser.add_argument('--callers', action='store_true')
    args = parser.parse_args()
    run = compare_callers if args.callers else compare
    raise SystemExit(run(args.snapshot, args.inventory))
