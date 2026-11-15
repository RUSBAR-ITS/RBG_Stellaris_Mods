"""Optional read-only corpus audit; invoke from the backend test directory."""

import hashlib
import json
from pathlib import Path

from support import PRODUCT_ROOT
from sttv.common.errors import BuildError
from sttv.common.paths import output_path
from sttv.script.parser import parse_text
from sttv.sources.settings import load_settings
from script.assertions import check_document

PROSE = {"common/HOW_TO_MAKE_NEW_SHIPS.txt", "common/edicts/99_README_EDICTS.txt"}
EXPECTED = {"common/named_colors/01_trait_colors.txt": ("missing_operator", 65)}


def audit():
    settings = load_settings(PRODUCT_ROOT / 'global_variables.json', PRODUCT_ROOT / 'config/backend.json')
    files = sorted(path for folder in ('common', 'events')
                   for path in (settings.game / folder).rglob('*.txt') if path.is_file())
    report = {'files': len(files), 'parsed': 0, 'empty': 0, 'significant_tokens': 0,
              'prose': [], 'diagnostics': [], 'unexpected': [], 'sources_unchanged': True}
    for path in files:
        relative = path.relative_to(settings.game).as_posix()
        raw = path.read_bytes()
        if relative in PROSE:
            report['prose'].append(relative)
            continue
        try:
            document = parse_text(raw.decode('utf-8'), settings.syntax, relative)
            report['significant_tokens'] += check_document(document, settings.syntax)
            report['parsed'] += 1
            report['empty'] += not bool(document.items)
            if relative in EXPECTED:
                report['unexpected'].append({'file': relative, 'error': 'Expected diagnostic missing'})
        except BuildError as exc:
            row = {'file': relative, 'code': exc.code, 'line': exc.line, 'message': str(exc)}
            report['diagnostics'].append(row)
            if EXPECTED.get(relative) != (exc.code, exc.line):
                report['unexpected'].append(row)
        except AssertionError as exc:
            report['unexpected'].append({'file': relative, 'error': 'Reconstruction mismatch: ' + str(exc)})
        report['sources_unchanged'] &= hashlib.sha256(raw).digest() == hashlib.sha256(path.read_bytes()).digest()
    output = output_path(settings.work, 'stage3/corpus_report.json', settings.protected)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    return bool(report['unexpected']) or not report['sources_unchanged']


if __name__ == '__main__':
    raise SystemExit(audit())
