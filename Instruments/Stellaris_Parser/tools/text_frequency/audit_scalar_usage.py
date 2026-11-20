"""Build two research lists from current frequency vocabulary and parsed source uses."""

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import json

from count_text import settings, read_json, write_json, fingerprint
from document_package.errors import BuildError
from stellaris_parser.script.nodes import InlineInvocation
from stellaris_parser.script.traversal import walk
from stellaris_parser.script.parser import parse_text
from scalar_usage import UsageInventory, scalar_assignment, scalar_value_only


def save_list(folder, name, rows):
    write_json(folder / (name + '.json'), rows)
    lines = [f"{json.dumps(row['text'], ensure_ascii=False)[1:-1]}:{row['count']}" for row in rows]
    (folder / (name + '.txt')).write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    selected = settings()
    base = selected.output
    output = base / 'scalar_analysis'
    frequencies = read_json(base / 'frequencies.json')
    prior_manifest = read_json(base / 'source_manifest.json')
    prior_report = read_json(base / 'report.json')
    inputs = [*selected.config_files,
              base / 'frequencies.json', base / 'frequencies.txt', base / 'source_manifest.json', base / 'report.json',
              Path(__file__), Path(__file__).with_name('scalar_usage.py'),
              Path(__file__).with_name('variable_filter.py')]
    input_hashes = {str(path): fingerprint(path) for path in inputs}
    inventory = UsageInventory(row['text'] for row in frequencies)
    diagnostics, manifest = [], []
    skipped, logical = 0, 0
    for index, previous in enumerate(prior_manifest, 1):
        relative = previous['file']
        path = selected.game / relative
        raw = path.read_bytes()
        assert fingerprint(path) == previous['sha256'], relative
        row = {'file': relative, 'sha256': previous['sha256']}
        if previous['status'] == 'excluded_prose':
            row['status'] = 'excluded_prose'
        else:
            try:
                document = parse_text(raw.decode('utf-8'), selected.syntax, relative, role='template')
                inventory.consume(document, relative)
                skipped += sum(isinstance(node, InlineInvocation) for node in walk(document.items))
                logical += previous.get('excluded_logical_operators', 0)
                row['status'] = 'counted'
            except (BuildError, UnicodeDecodeError) as exc:
                row['status'] = 'failed'
                diagnostics.append({'file': relative, 'code': getattr(exc, 'code', 'decode_error'),
                                    'line': getattr(exc, 'line', None), 'message': str(exc)})
        assert row['status'] == previous['status'], row
        manifest.append(row)
        if index % 250 == 0:
            print(f'Analyzed {index}/{len(prior_manifest)} files', flush=True)
    rows = inventory.rows()
    assert [{'text': row['text'], 'count': row['count']} for row in rows] == frequencies
    first = [row for row in rows if scalar_assignment(row)]
    second = [row for row in rows if scalar_value_only(row)]
    assert not ({row['text'] for row in first} & {row['text'] for row in second})
    previous_errors = {(row['file'], row['code'], row['line']) for row in prior_report['diagnostics']}
    assert {(row['file'], row['code'], row['line']) for row in diagnostics} == previous_errors
    assert all(fingerprint(selected.game / row['file']) == row['sha256'] for row in manifest)
    assert all(fingerprint(Path(path)) == digest for path, digest in input_hashes.items())
    assert skipped == prior_report['skipped_inline_scripts']
    summary = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'scope': 'current_frequency_vocabulary_current_corpus_outside_skipped_inline_calls',
        'case_normalization': 'unicode_casefold', 'frequency_minimum_count': 2,
        'variable_filter': prior_report['variable_filter'],
        'list_count_meaning': 'total_occurrences_in_original_frequency_list',
        'list_1_rule': 'all_assignment_right_hand_sides_are_Scalar_no_block_tag_or_logical_name_uses',
        'list_2_rule': 'all_occurrences_are_Scalar_values_or_list_items_never_keys_tags_or_headers',
        'txt_files': len(manifest), 'file_statuses': dict(Counter(row['status'] for row in manifest)),
        'vocabulary_size': len(rows), 'vocabulary_occurrences': sum(row['count'] for row in rows),
        'scalar_assignments': len(first), 'scalar_assignment_text_occurrences': sum(row['count'] for row in first),
        'scalar_assignment_key_occurrences': sum(row['roles']['assignment_key'] for row in first),
        'scalar_assignments_also_used_as_values': sum(bool(set(row['roles']) - {'assignment_key'}) for row in first),
        'scalar_values': len(second), 'scalar_value_occurrences': sum(row['count'] for row in second),
        'unclassified_texts': len(rows) - len(first) - len(second), 'skipped_inline_scripts': skipped,
        'diagnostics': diagnostics, 'frequency_totals_match': True, 'source_hashes_unchanged': True,
        'input_hashes': input_hashes,
    }
    output.mkdir(parents=True, exist_ok=True)
    save_list(output, 'scalar_assignments', first)
    save_list(output, 'scalar_values', second)
    write_json(output / 'usage_inventory.json', rows)
    write_json(output / 'source_manifest.json', manifest)
    write_json(output / 'report.json', summary)
    print(json.dumps({key: value for key, value in summary.items() if key != 'input_hashes'}, indent=2))
    print(json.dumps({'scalar_assignments_top': [r['text'] for r in first[:20]],
                      'scalar_values_top': [r['text'] for r in second[:20]]}, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
