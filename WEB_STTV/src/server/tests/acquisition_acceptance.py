"""Audit player reward paths for every base technology in a local parser snapshot."""

import argparse
from collections import Counter
import json
from pathlib import Path

from sttv_server.progress_sources import COLLECTIONS, ProgressSources, key, text


def documents(directory, collection):
    for path in sorted(directory.glob('*.json')):
        raw = json.loads(path.read_bytes())
        for i, node in enumerate(raw['items']):
            body = node.get('value', {})
            if body.get('kind') != 'block':
                continue
            identifier = key(node)
            if collection == 'events':
                identifier = text(body, 'id')
            elif collection == 'special_projects':
                identifier = next((item['value']['text'] for item in body['items'] if key(item).lower() == 'key'), None)
            if identifier:
                yield {'_id': identifier, 'tree': node, 'source': raw['source'], 'pointer': f'/items/{i}'}


def audit(snapshot, report):
    dirs = {c: snapshot / 'common' / c for c in COLLECTIONS}
    dirs.update(events=snapshot / 'events', focus_rewards=snapshot / 'common/country_focus/focus_rewards',
                psionic_auras=snapshot / 'common/patrons/psionic_auras')
    ids = {row['_id'] for row in documents(snapshot / 'common/technology', 'technologies')}
    events = {row['_id'] for row in documents(dirs['events'], 'events')}
    index = ProgressSources(ids, events)
    for name, directory in dirs.items():
        assert directory.is_dir(), directory
        seen = set()
        for doc in documents(directory, name):
            if name != 'on_actions':
                assert doc['_id'] not in seen, (name, doc['_id'])
            seen.add(doc['_id'])
            index.add(name, doc)
    totals = {}
    rows = {id_: {} for id_ in sorted(ids)}
    for kind, rewards in index.rewards.items():
        counts = Counter()
        for tech, sources in rewards.items():
            entries = []
            for source, hits in sources.items():
                for hit in hits:
                    reason = index.issue(hit) or 'confirmed'
                    origin = hit['origin']
                    entry = {'source': source, 'file': hit['file'], 'pointer': hit['pointer'], 'status': reason,
                             'recipient_scopes': hit['scopes'], 'option': hit['option'], 'stages': hit['stages'],
                             'branch_weights': hit['chance'], 'amount': hit.get('amount'),
                             'definition': {'file': origin['file'], 'line': origin['span']['line']},
                             'expansion': origin.get('expansion_id')}
                    if reason == 'unconfirmed_source':
                        callers = index.incoming if source[0] == 'events' else index.projects
                        entry['incoming'] = [
                            {'source': e['source'], 'recipient_scopes': e['scopes'], 'file': e['file'],
                             'pointer': e['pointer'], 'status': e['issue'] or 'no_established_entry'}
                            for e in callers.get(source[1], ())]
                    entries.append(entry)
                    counts[reason] += 1
            rows[tech][kind] = entries
        totals[kind] = {'technologies': len(rewards), 'sites': counts.total(), 'by_status': counts}
    dynamic_calls = []
    for command, operands, hit in index.mechanics.pools:
        origin = hit['origin']
        entry = {k: hit[k] for k in ('source', 'file', 'pointer', 'scopes', 'issue')}
        entry['issue'] = index.issue(hit)
        entry['definition'] = {'file': origin['file'], 'line': origin['span']['line']}
        entry['expansion'] = origin.get('expansion_id')
        dynamic_calls.append((command, operands, entry))
    report.write_text(json.dumps({'total_technologies': len(ids), 'totals': totals, 'technologies': rows,
                                  'dynamic_calls': dynamic_calls,
                                  'unknown_targets': index.unresolved}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(totals))
    for tech, kind, source in (
            ('tech_trinary_computing', 'research_options', 'fircon.10'),
            ('tech_ordered_retreat', 'research_options', 'fircon.10'),
            ('tech_alloy_fossilization', 'research_options', 'extreme_frontiers.435'),
            ('tech_cryovault', 'research_options', 'extreme_frontiers.1020'),
            ('tech_thrusters_bio_integration', 'research_options', 'grand_archive.7400'),
            ('tech_thrusters_bio_integration', 'research_options', 'grand_archive.7401'),
            ('tech_thrusters_bio_integration', 'researched_grants', 'grand_archive.7200'),
            ('tech_mine_living_metal', 'research_options', 'distar.150'),
            ('tech_mine_living_metal', 'research_progress', 'distar.150'),
            ('tech_crystal_armor_1', 'research_progress', 'grand_archive.2410'),
            ('tech_crystal_armor_1', 'research_progress', 'story.205')):
        assert any(row['source'][1] == source and row['status'] == 'confirmed' for row in rows[tech][kind]), (tech, source)
    assert not any(row['source'][1] == 'colony.9850' and row['status'] == 'confirmed'
                   for record in rows.values() for row in record.get('researched_grants', ()))
    for event, technologies, sites in [('origin.21', 14, 14), ('preftl.2070', 13, 26)]:
        recipients = [tech for tech, sections in rows.items() for section in sections.values()
                      for row in section if row['source'] == ('events', event) and row['status'] == 'confirmed']
        assert (len(set(recipients)), len(recipients)) == (technologies, sites), event


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    audit(args.snapshot, args.report)
