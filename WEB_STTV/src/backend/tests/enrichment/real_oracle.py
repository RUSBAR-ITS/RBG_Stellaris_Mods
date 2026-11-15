"""Independent real-source checks, without the production localization reader."""

from collections import Counter
from pathlib import Path, PurePosixPath
import re

from sttv.common.json_io import read_json

ENTRY = re.compile(r'^\s*([^\s:#]+):[0-9]*\s*"(.*)"\s*(?:#.*)?$')
REFERENCE = re.compile(r'\$([A-Za-z0-9_.:-]+)\$')


def source_index(variables, options):
    roots = dict(variables)
    for _ in range(len(roots)):
        roots = {key: re.sub(r'\$\{([^}]+)\}', lambda m: roots[m[1]], value)
                 for key, value in roots.items()}
    tables = {}
    for language, spec in options['languages'].items():
        selected = tables[language] = {}
        for tier in spec['sources']:
            root = Path(roots[tier])
            if not root.is_absolute():
                root = Path(roots['STELLARIS_ROOT']) / root
            current = {}
            for path in sorted(root.rglob('*.yml')):
                header = None
                for number, line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
                    if re.fullmatch(r'\s*l_\w+:\s*', line):
                        header = line.strip().rstrip(':')
                    match = ENTRY.fullmatch(line)
                    if match and header == spec['header']:
                        current.setdefault(match[1], []).append((match[2],
                            {'tier': tier, 'file': path.relative_to(root).as_posix(), 'line': number}))
            for key, entries in current.items():
                selected.setdefault(key, entries)
    return tables


def resolved(index, key, trail=()):
    if key not in index:
        return None
    assert key not in trail, trail
    entries = index[key]
    assert len({text for text, _ in entries}) == 1, key
    raw, source = entries[0]
    unresolved = set()
    def substitute(match):
        child = resolved(index, match[1], (*trail, key))
        if child is None:
            unresolved.add(match[0])
            return match[0]
        unresolved.update(child[3])
        return child[1]
    text = REFERENCE.sub(substitute, raw)
    return raw, text, source, sorted(unresolved)


def compare_tree(before, after):
    if isinstance(before, dict):
        assert before.keys() == after.keys() - {'enrichments'}
        return int({'kind', 'span', 'origin'} <= before.keys()) + sum(
            compare_tree(value, after[key]) for key, value in before.items())
    if isinstance(before, list):
        assert len(before) == len(after)
        return sum(compare_tree(left, right) for left, right in zip(before, after))
    assert type(before) is type(after) and before == after, (before, after)
    return 0


def verify(baseline_path, enriched_path, variables, options):
    before, after = read_json(baseline_path), read_json(enriched_path)
    nodes = compare_tree(before, after)
    tables = source_index(variables, options)
    totals, checked, inherited = Counter(), 0, Counter()
    def check(node, key, parent_key=None, parent_path=None):
        nonlocal checked
        for language in ('ru', 'en'):
            for field in ('name', 'description'):
                requested = key + ('_desc' if field == 'description' else '')
                chosen, parent = requested, None
                expected = resolved(tables[language], chosen)
                if expected is None and field == 'description' and parent_key:
                    chosen, parent = parent_key + '_desc', parent_path
                    expected = resolved(tables[language], chosen)
                    inherited[language] += 1
                assert expected is not None, (language, requested)
                raw, text, source, unresolved = expected
                actual = node['enrichments']['localization'][language][field]
                assert actual == {'requested_key': requested, 'key': chosen, 'raw': raw, 'text': text,
                                  'source': source, 'inherited_from': parent,
                                  'unresolved_references': unresolved}, (language, requested)
                checked += 1
    for number, document in enumerate(after['documents']):
        if PurePosixPath(document['source']['file']).parent.as_posix() != variables['TECH_PATH']:
            assert not any('enrichments' in node for node in document['items'])
            continue
        for offset, node in enumerate(document['items']):
            if node['kind'] != 'assignment' or node['value']['kind'] != 'block':
                continue
            key = node['key']['text']
            check(node, key)
            totals['technologies'] += 1
            for child in node['value']['items']:
                if child['kind'] == 'assignment' and child['key']['text'] == 'technology_swap':
                    variant = next(item['value']['text'] for item in child['value']['items']
                                   if item['kind'] == 'assignment' and item['key']['text'] == 'name')
                    check(child, variant, key, f'/documents/{number}/items/{offset}')
                    totals['variants'] += 1
    assert totals == {'technologies': 679, 'variants': 206}, totals
    assert inherited == {'ru': 81, 'en': 81}, inherited
    return {'nodes_unchanged': nodes, 'objects': dict(totals), 'localized_fields_checked': checked,
            'inherited_descriptions': dict(inherited), 'ast_and_history_unchanged': True,
            'independent_sources_and_references_match': True}
