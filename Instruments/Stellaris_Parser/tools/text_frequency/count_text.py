"""Measure remaining AST text with the current parser and structural exclusions."""

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from stellaris_parser.schema import ROOT as PRODUCT
from document_package.errors import BuildError
from stellaris_parser.script.syntax import Syntax, load_syntax
from frequency_tree import EXCLUDED_TEXTS, MINIMUM_COUNT, frequency_rows, measure
from variable_filter import VARIABLE_FILTER

FOLDERS = ('common', 'events')
PROSE = {'common/HOW_TO_MAKE_NEW_SHIPS.txt', 'common/edicts/99_README_EDICTS.txt'}
EXPECTED_ERRORS = {'common/named_colors/01_trait_colors.txt': ('missing_operator', 65)}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


@dataclass
class Settings:
    game: Path
    output: Path
    syntax: Syntax
    config_files: list[Path]
    reference: Path | None


def settings(reference_help=None):
    parser = argparse.ArgumentParser(description="Analyze script text in a source tree.")
    parser.add_argument("--source", type=Path, required=True, help="Directory containing common/ or events/")
    parser.add_argument("--output", type=Path, required=True, help="Frequency report directory")
    parser.add_argument("--syntax-dir", type=Path, default=PRODUCT / "config")
    if reference_help:
        parser.add_argument("--reference", type=Path, help=reference_help)
    args = parser.parse_args()
    game, output = args.source.resolve(), args.output.resolve()
    if not game.is_dir() or output.is_relative_to(game):
        parser.error("Supply an existing source directory and a separate output directory")
    configs = [args.syntax_dir.resolve() / name for name in
               ("lexical.json", "constructs.json", "logical_operators.json")]
    return Settings(game, output, load_syntax(*configs), configs, getattr(args, "reference", None))


def main():
    selected = settings()
    game, output, syntax = selected.game, selected.output, selected.syntax
    inputs = [*selected.config_files, Path(__file__), Path(__file__).with_name('frequency_tree.py'),
              Path(__file__).with_name('variable_filter.py'),
              *sorted((PRODUCT / 'script').rglob('*.py')),
              *sorted((PRODUCT / 'schemas').glob('*.json'))]
    input_hashes = {str(path): fingerprint(path) for path in inputs}
    files = sorted(p for folder in FOLDERS for p in (game / folder).rglob('*.txt') if p.is_file())
    if not files:
        raise ValueError(f"No scripts in {game} under {FOLDERS}")
    totals, excluded_totals, logical_totals, text_kinds = Counter(), Counter(), Counter(), Counter()
    variable_totals, variable_categories = Counter(), Counter()
    manifest, diagnostics, unexpected = [], [], []
    for index, path in enumerate(files, 1):
        relative, raw = path.relative_to(game).as_posix(), path.read_bytes()
        row = {'file': relative, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        if relative in PROSE:
            row['status'] = 'excluded_prose'
        else:
            try:
                counts, details, excluded = measure(raw.decode('utf-8'), syntax, relative)
                totals.update(counts)
                excluded_totals.update(excluded)
                logical_totals.update(details['logical_operator_counts'])
                text_kinds.update(details['text_kinds'])
                variable_totals.update(details.pop('excluded_variable_counts'))
                variable_categories.update(details['excluded_variable_categories'])
                row.update(status='counted', occurrences_before_minimum_count=sum(counts.values()),
                           excluded_text_occurrences=sum(excluded.values()),
                           raw_occurrences=sum(counts.values()) + sum(excluded.values())
                           + details['excluded_variable_occurrences'], **details)
            except (BuildError, UnicodeDecodeError) as exc:
                expected = EXPECTED_ERRORS.get(relative) == (getattr(exc, 'code', None), getattr(exc, 'line', None))
                row['status'] = 'failed'
                diagnostic = {'file': relative, 'code': getattr(exc, 'code', 'decode_error'),
                              'line': getattr(exc, 'line', None), 'column': getattr(exc, 'column', None),
                              'expected': expected, 'message': str(exc)}
                diagnostics.append(diagnostic)
                if not expected:
                    unexpected.append(diagnostic)
        manifest.append(row)
        if index % 250 == 0:
            print(f'Processed {index}/{len(files)} files', flush=True)
    assert all(fingerprint(game / row['file']) == row['sha256'] for row in manifest)
    assert all(fingerprint(Path(path)) == digest for path, digest in input_hashes.items())
    rows = frequency_rows(totals)
    occurrences = sum(row['count'] for row in rows)
    singletons = sum(count == 1 for count in totals.values())
    assert occurrences + singletons == sum(row.get('occurrences_before_minimum_count', 0) for row in manifest)
    summary = {
        'generated_at': datetime.now(timezone.utc).isoformat(), 'pass': 4,
        'source_root': str(game), 'folders': list(FOLDERS), 'pattern': '*.txt',
        'method': 'current_parser_ast_excluding_logical_names_and_skipped_inline_calls',
        'logical_operator_configuration': syntax.logical_operators,
        'inline_script_configuration': syntax.constructs['inline_script'],
        'case_normalization': 'unicode_casefold', 'excluded_texts': sorted(EXCLUDED_TEXTS),
        'minimum_count': MINIMUM_COUNT, 'txt_files': len(files),
        'counted_files': sum(r['status'] == 'counted' for r in manifest),
        'excluded_prose': [r['file'] for r in manifest if r['status'] == 'excluded_prose'], 'failed_files': len(diagnostics), 'diagnostics': diagnostics,
        'unexpected_diagnostics': unexpected, 'unique_texts': len(rows), 'occurrences': occurrences,
        'raw_occurrences': sum(totals.values()) + sum(excluded_totals.values()) + sum(variable_totals.values()),
        'variable_filter': VARIABLE_FILTER, 'excluded_variable_texts': len(variable_totals),
        'excluded_variable_occurrences': sum(variable_totals.values()),
        'excluded_variable_categories': dict(variable_categories),
        'excluded_text_counts': dict(sorted(excluded_totals.items())),
        'excluded_text_occurrences': sum(excluded_totals.values()), 'excluded_singletons': singletons,
        'logical_operator_counts': dict(sorted(logical_totals.items())),
        'excluded_logical_operators': sum(logical_totals.values()),
        'skipped_inline_scripts': sum(r.get('skipped_inline_scripts', 0) for r in manifest),
        'text_kinds': dict(sorted(text_kinds.items())),
        'source_hashes_unchanged': True, 'input_hashes': input_hashes,
        'validation': {'token_coverage': True, 'ast_token_sequence_match': True, 'totals_match': True},
    }
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / 'frequencies.json', rows)
    write_json(output / 'report.json', summary)
    write_json(output / 'source_manifest.json', manifest)
    lines = [f"{json.dumps(row['text'], ensure_ascii=False)[1:-1]}:{row['count']}" for row in rows]
    (output / 'frequencies.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'summary': {k: v for k, v in summary.items() if k != 'input_hashes'},
                      'top_20': rows[:20]}, ensure_ascii=True, indent=2))
    return bool(unexpected)


if __name__ == '__main__':
    raise SystemExit(main())
