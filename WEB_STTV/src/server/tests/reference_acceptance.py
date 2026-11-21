"""Run the HTTP profile matrix against a dedicated reference-tree test namespace."""

import argparse
import hashlib
import json
import re
from pathlib import Path
from time import perf_counter
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from sttv_server.config import load_config
from sttv_server.database import connect


def request(url, method, body=None):
    payload = json.dumps(body).encode() if body is not None else None
    with urlopen(Request(url, data=payload, method=method, headers={'Content-Type': 'application/json'}), timeout=600) as response:
        return json.load(response)


def verify(rows, items, ids):
    assert {r['_id'] for r in rows} == ids and len(rows) == len(ids)
    shown = {r['_id']: r for r in items}
    assert len(shown) == len(items)
    assert shown == {r['_id']: r for r in rows if r['availability']}
    cells = set()
    for row in rows:
        key, parent, children = row['_id'], row['parent_tech'], row['children']
        if not row['availability']:
            assert (parent, children, row['location']) == (None, [], None)
            continue
        assert children == sorted(set(children))
        assert all(shown[c]['parent_tech'] == key for c in children)
        if parent:
            assert key in shown[parent]['children']
        seen = {key}
        while parent:
            assert parent not in seen
            seen.add(parent)
            parent = shown[parent]['parent_tech']
        for lang in ('ru', 'en'):
            xy = tuple(row['location'][lang])
            cell = (lang, row['area'], xy)
            assert len(xy) == 2 and all(type(v) is int and v >= 0 for v in xy) and cell not in cells
            cells.add(cell)
    return set(shown)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    config = load_config(args.config)
    prefix = config['tree_collection_prefix']
    assert re.fullmatch(r'tree_test_[a-z0-9]+_', prefix)
    url = 'http://127.0.0.1:%d/api/trees/reference' % config['http']['port']
    matrix = json.loads((Path(__file__).parent / 'fixtures/reference_profiles.json').read_text(encoding='utf-8'))
    with connect(config['mongodb']) as client:
        db = client[config['mongodb']['database']]
        registry = db[prefix + 'configs']
        assert registry.count_documents({}) == 0, 'Start with an empty isolated registry'
        all_dlc = set(db.dlcs.distinct('_id'))
        dlcs = request(url + '/dlcs', 'GET')['items']
        assert {r['id'] for r in dlcs} == all_dlc
        assert all(set(r['name']) == {'ru', 'en'} and all(r['name'].values()) for r in dlcs)
        ids = set(db.technologies.distinct('_id'))
        catalog_query = {'name': {'$in': config['tree_rules']['catalogs']}}
        def versions():
            return {r['name']: r['info']['uuid'] for r in db.list_collections(filter=catalog_query)}
        sources = versions()
        report = []
        for label, selection, present, absent in matrix:
            if selection == '{}':
                enabled = sorted(all_dlc)
            elif selection == '[]':
                enabled = []
            elif selection.startswith('!'):
                enabled = sorted(all_dlc - set(selection[1:].split()))
            else:
                enabled = selection.split()
            start = perf_counter()
            body = {} if selection == '{}' else {'enabled_dlc': enabled}
            result = request(url, 'POST', body)
            elapsed = perf_counter() - start
            tree_id = result['tree_id']
            canonical = {'mode': 'reference', 'enabled_dlc': sorted(set(enabled))}
            assert tree_id == hashlib.sha256(json.dumps(canonical, separators=(',', ':')).encode()).hexdigest()
            assert result['enabled_dlc'] == canonical['enabled_dlc']
            meta = registry.find_one({'_id': tree_id, 'state': 'ready'})
            assert meta and meta['enabled_dlc'] == canonical['enabled_dlc']
            rows = list(db[prefix + tree_id].find())
            shown = verify(rows, result['items'], ids)
            diffs = sorted((set(present) - shown) | (set(absent) & shown))
            repeat = perf_counter()
            again = request(url, 'POST', {'enabled_dlc': enabled[::-1] + enabled[:1]})
            repeat = perf_counter() - repeat
            assert again == result and registry.find_one({'_id': tree_id}) == meta
            report.append(dict(profile=selection, enabled_dlc=enabled, tree_id=tree_id, visible=len(shown),
                               hidden=len(ids)-len(shown), differences=diffs, seconds=meta['seconds'],
                               open_seconds=elapsed, reuse_seconds=repeat))
            args.report.write_text(json.dumps(report, indent=2) + '\n')
            print(selection, len(shown), diffs, flush=True)
        assert len({p['tree_id'] for p in report}) == len(matrix) == 12
        assert registry.count_documents({}) == 12
        for invalid in ({'enabled_dlc': 'all'}, {'enabled_dlc': ['missing']}, {'mode': 'other'}):
            try:
                request(url, 'POST', invalid)
            except HTTPError as exc:
                assert exc.code == 400
            else:
                raise AssertionError(invalid)
        assert request(url, 'DELETE')['removed_collections'] == 12
        assert not registry.count_documents({}) and request(url, 'DELETE')['removed_collections'] == 0
        assert not set(db.list_collection_names()) & {prefix + r['tree_id'] for r in report}
        assert request(url, 'POST', body)['tree_id'] == report[-1]['tree_id']
        assert registry.count_documents({}) == 1 and request(url, 'DELETE')['removed_collections'] == 1
        assert sources == versions()
        assert not any(p['differences'] for p in report), 'Control technologies differ'
        print('PASS: 12 profiles, cache reuse, cleanup, reopen and source UUIDs')


if __name__ == '__main__':
    main()
