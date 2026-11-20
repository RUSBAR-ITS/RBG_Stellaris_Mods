"""Verify token preservation and source immutability; inventory definable families."""

from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re

from measure_patterns import DOCUMENTS, paths
from structure_probe import Probe, lex


def rebuild(nodes):
    result = []
    for node in nodes:
        if node.form == 'conditional':
            result += [node.start.text, *rebuild(node.children), ']']
        elif node.form == 'anonymous_block':
            result += ['{', *rebuild(node.children), '}']
        elif node.form == 'labelled_block':
            result += [node.tag.text, '{', *rebuild(node.children), '}']
        elif node.form == 'bare_scalar':
            result.append(node.value.text)
        else:
            result += [node.key.text, node.operator]
            if node.tag:
                result.append(node.tag.text)
            if node.children is not None:
                result += ['{', *rebuild(node.children), '}']
            else:
                result.append(node.value.text)
    return result


def main():
    root, output = paths()
    base = json.loads((output / 'baseline_audit.json').read_text())
    patterns = json.loads((output / 'pattern_audit.json').read_text())
    if Path(base["root"]).resolve() != root:
        raise ValueError("Source does not match the measured corpus")
    launcher = root / "launcher-settings.json"
    version = json.loads(launcher.read_text(encoding="utf-8-sig"))["version"] if launcher.exists() else None
    summary = {'root': str(root), 'version': version,
               'totals': {}, 'non_txt': [], 'folders': {}, 'families': {}, 'verification': {}}
    for folder in ('common', 'events'):
        files = [f for f in base['files'] if f['file'].startswith(folder + '/')]
        txt = [f for f in files if f['extension'] == '.txt']
        summary['totals'][folder] = {'files': len(files), 'txt': len(txt),
                                     'non_txt': len(files) - len(txt),
                                     'txt_bytes': sum(f['bytes'] for f in txt),
                                     'txt_lines': sum(f['lines'] for f in txt)}
    families = defaultdict(list)
    document_roots, roundtrips, hashes, tokens_total = Counter(), 0, 0, 0
    scope_stats = defaultdict(Counter)
    for item in base['files']:
        path = item['file']
        raw = (root / path).read_bytes()
        assert sha256(raw).hexdigest() == item['sha256'], path
        hashes += 1
        if item['extension'] != '.txt':
            summary['non_txt'].append(item)
            continue
        if path in DOCUMENTS:
            continue
        tokens = list(lex(raw.decode('utf-8-sig')))
        nodes = Probe(tokens).sequence()
        expected = [t.text for t in tokens if t.kind not in ('space', 'comment')]
        assert rebuild(nodes) == expected, path
        roundtrips += 1
        tokens_total += len(expected)
        document_roots.update(n.form for n in nodes)
        parts = Path(path).parts
        folder = '/'.join(parts[:2]) if parts[0] == 'common' else 'events'
        scope_stats[folder]['files'] += 1
        scope_stats[folder].update(n.form for n in nodes)
        if folder in ('common/scripted_triggers', 'common/scripted_effects',
                      'common/script_values', 'common/scripted_variables'):
            for n in nodes:
                if n.key:
                    families[folder].append({'id': n.key.text, 'file': path, 'line': n.start.line,
                                              'form': n.form})
        if folder == 'common/inline_scripts' and nodes:
            text = ''.join(t.text for t in tokens if t.kind != 'comment')
            parameters = sorted(set(re.findall(r'\$([A-Za-z_][A-Za-z_0-9]*)(?:\|[^$]*)?\$', text)))
            families[folder].append({'file': path, 'parameters': parameters})
    for folder, records in families.items():
        ids = [r['id'] for r in records if 'id' in r and not r['id'].startswith('@')]
        summary['families'][folder] = {'records': len(records), 'named_definitions': len(ids),
                                       'unique_names': len(set(ids)),
                                       'local_at_definitions': sum(r.get('id', '').startswith('@') for r in records)}
    summary['folders'] = dict(sorted(scope_stats.items()))
    summary['verification'] = {'unchanged_file_hashes': hashes,
                                'token_roundtrip_files': roundtrips,
                                'significant_tokens_roundtripped': tokens_total,
                                'lexical_reconstruction_files': roundtrips,
                                'separately_reviewed_prose_files': sorted(DOCUMENTS),
                                'unresolved_structural_files': len(patterns['failures']),
                                'observed_maximum_depth': patterns['max_depth']}
    summary['status_counts'] = dict(Counter(f['status'] for f in patterns['files']))
    summary['operators'] = patterns['operators']
    summary['form_counts'] = {k: patterns['counts'].get(k, 0) for k in
                              ('key_scalar', 'key_block', 'bare_scalar', 'anonymous_block',
                               'labelled_block', 'tagged_value', 'conditional')}
    summary['document_roots'] = document_roots
    summary['encoding'] = dict(Counter(f['encoding'] for f in base['files'] if 'encoding' in f))
    summary['directories'] = base['directories']
    (output / 'definition_catalog.json').write_text(json.dumps(families, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')
    (output / 'corpus_summary.json').write_text(json.dumps(summary, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('directories','folders','non_txt')}, indent=2))


if __name__ == '__main__':
    main()
