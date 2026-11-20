"""Inventory condition inputs from the prepared technology snapshot, read-only."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

SECTIONS = {'potential', 'starting_potential', 'weight', 'weight_modifier', 'prerequisites'}


def fields(body):
    return [(n['key']['text'], n) for n in body.get('items', []) if n.get('kind') == 'assignment']


def plain(node):
    if not isinstance(node, dict):
        return node
    kind = node.get('kind')
    if kind == 'scalar':
        return node['text']
    if kind == 'assignment':
        return [node['key']['text'], node['operator'], plain(node['value'])]
    if kind == 'block':
        return [plain(n) for n in node['items']]
    keys = {'logical_operation': ('operator', 'body'), 'script_value': ('scope', 'body'),
            'scripted_trigger_test': ('operator', 'value', 'body'), 'conditional': ('parameter', 'negated', 'items'),
            'tagged_block': ('tag', 'block'), 'formula': ('opener', 'body')}.get(kind)
    if keys is None:
        raise ValueError(f'Unhandled syntax: {kind}')
    return {'kind': kind, **{k: [plain(v) for v in node[k]] if isinstance(node[k], list)
                            else plain(node[k]) for k in keys}}


def source(node):
    origin = node.get('origin', {})
    return {'file': origin.get('file'), 'line': origin.get('span', node.get('span', {})).get('line')}


def walk(node, path=()):
    kind = node.get('kind')
    if kind == 'assignment':
        yield path, node
        yield from walk(node['value'], path + (node['key']['text'],))
    elif kind == 'logical_operation':
        yield from walk(node['body'], path + (node['operator'],))
    elif kind in ('script_value', 'scripted_trigger_test'):
        yield from walk(node['body'], path + (f'@{kind}',))
    elif kind in ('block', 'conditional'):
        for child in node['items']:
            yield from walk(child, path)
    elif kind == 'tagged_block':
        yield from walk(node['block'], path + ('@tagged_block',))
    elif kind not in ('scalar', 'formula'):
        raise ValueError(f'Unhandled syntax: {kind}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, required=True, help='Directory containing manifest.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((args.snapshot / 'manifest.json').read_text(encoding='utf-8'))
    technology_rows, groups, observations = [], {}, []
    counts, section_techs = Counter(), defaultdict(set)
    for descriptor in manifest['datasets']['technologies']['documents']:
        raw = (args.snapshot / descriptor['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == descriptor['file_hash']
        document = json.loads(raw)
        for root in document['items']:
            if 'technology_tree' not in root.get('enrichments', {}):
                continue
            tech = root['key']['text']
            sections, row = [], {'id': tech, 'source': source(root), 'fields': {}, 'variants': []}
            loc = root.get('enrichments', {}).get('localization', {})
            row['names'] = {lang: loc.get(lang, {}).get('name', {}).get('text') for lang in ('ru', 'en')}
            for key, field in fields(root['value']):
                counts[key] += 1
                if key in SECTIONS:
                    sections.append((key, None, field['value']))
                    section_techs[key].add(tech)
                    row['fields'].setdefault(key, []).append(plain(field['value']))
                elif key in ('tier', 'start_tech', 'levels', 'area', 'is_rare', 'is_dangerous', 'category', 'weight_groups', 'mod_weight_if_group_picked'):
                    row['fields'].setdefault(key, []).append(plain(field['value']))
                elif key == 'technology_swap':
                    variant = {k: plain(v['value']) for k, v in fields(field['value']) if k in ('name', 'area', 'category')}
                    index = len(row['variants'])
                    for vk, vf in fields(field['value']):
                        if vk in ('trigger', 'weight'):
                            sections.append((f'technology_swap.{vk}', index, vf['value']))
                            section_techs[f'technology_swap.{vk}'].add(tech)
                            variant[vk] = plain(vf['value'])
                    row['variants'].append(variant)
            technology_rows.append(row)
            for section, variant, body in sections:
                for path, node in walk(body):
                    key = node['key']['text']
                    signature = key, node['value']['kind']
                    group = groups.setdefault(signature, {'key': key, 'value_kind': signature[1], 'count': 0,
                        'technologies': set(), 'sections': Counter(), 'values': Counter(), 'paths': Counter(), 'examples': []})
                    group['count'] += 1
                    group['technologies'].add(tech)
                    group['sections'][section] += 1
                    value = plain(node['value'])
                    if node['value']['kind'] == 'scalar':
                        group['values'][value] += 1
                    group['paths']['/'.join(path)] += 1
                    observation = {'technology': tech, 'section': section, 'variant': variant,
                        'path': list(path), 'key': key, 'operator': node['operator'], 'value': value, 'source': source(node)}
                    if len(group['examples']) < 3:
                        group['examples'].append(observation)
                    observations.append(observation)
    rows = []
    for group in groups.values():
        group['technologies'] = sorted(group['technologies'])
        for name in ('sections', 'values', 'paths'):
            group[name] = dict(sorted(group[name].items()))
        rows.append(group)
    rows.sort(key=lambda row: (row['key'], row['value_kind']))
    result = {'snapshot_revision': manifest['snapshot_revision'], 'source_revision': manifest['datasets']['technologies']['source_revision'],
        'documents': len(manifest['datasets']['technologies']['documents']), 'technologies': len(technology_rows),
        'variants': sum(len(r['variants']) for r in technology_rows), 'root_fields': dict(sorted(counts.items())),
        'section_technologies': {k: len(v) for k, v in sorted(section_techs.items())},
        'assignment_shapes': len(rows), 'groups': rows}
    for name, data in [('inventory', result), ('technologies', technology_rows), ('observations', observations)]:
        (args.output / f'{name}.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'groups'}, indent=2))
    print('KEY | KIND | TECHNOLOGIES | OCCURRENCES | VALUES')
    for group in rows:
        print(group['key'], group['value_kind'], len(group['technologies']), group['count'],
              ', '.join(group['values'])[:210], sep=' | ')


if __name__ == '__main__':
    main()
