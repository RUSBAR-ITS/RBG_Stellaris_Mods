"""Audit expanded sources without changing game files or curated research lists."""

import hashlib
import json
from pathlib import Path

from support import PRODUCT_ROOT
from sttv.common.errors import BuildError
from sttv.common.paths import output_path
from sttv.common.report import Report
from sttv.script.parser import parse_text
from sttv.script.serialization import serialize_document, walk_nodes
from sttv.database.history import validate_history
from sttv.sources.expansion import expansion_context, independent_sources
from sttv.sources.settings import load_settings
from script.corpus_statistics import Statistics

PROSE = {'common/HOW_TO_MAKE_NEW_SHIPS.txt', 'common/edicts/99_README_EDICTS.txt'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    settings = load_settings(PRODUCT_ROOT / 'global_variables.json', PRODUCT_ROOT / 'config/backend.json')
    files = sorted(path for folder in ('common', 'events')
                   for path in (settings.game / folder).rglob('*.txt') if path.is_file())
    roots = list(independent_sources(files, settings))
    protected_lists = {str(p): digest(p) for p in (settings.work / 'text_frequency').rglob('*.txt')}
    diagnostics, statistics = Report(), Statistics()
    expansion = expansion_context(settings, diagnostics)
    report = {'physical_txt_files': len(files), 'independent_files': len(roots), 'parsed': 0,
              'excluded_template_files': len(files) - len(roots), 'empty': 0, 'prose': [],
              'serialized_documents': 0, 'serialized_nodes': 0, 'serialized_bytes': 0,
              'failures': [], 'sources_unchanged': True, 'research_lists_unchanged': True}
    sources = {}
    for index, path in enumerate(roots):
        relative = path.relative_to(settings.game).as_posix()
        sources[str(path)] = digest(path)
        if relative in PROSE:
            report['prose'].append(relative)
            continue
        try:
            document = parse_text(path.read_text(encoding='utf-8-sig'), settings.syntax, relative, expansion=expansion)
            encoded = serialize_document(document)
            content = json.dumps(encoded, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
            loaded = json.loads(content)
            if loaded != encoded:
                raise BuildError('roundtrip_mismatch', 'Serialized document changed after JSON loading')
            validate_history(loaded)
            report['serialized_documents'] += 1
            report['serialized_nodes'] += sum(1 for _ in walk_nodes(loaded['items']))
            report['serialized_bytes'] += len(content.encode('utf-8'))
            del encoded, loaded, content
            statistics.consume(document)
            report['parsed'] += 1
            report['empty'] += not bool(document.items)
        except (BuildError, OSError, ValueError, RecursionError) as exc:
            diagnostics.failure(exc, 'corpus', source='STELLARIS_ROOT', file=relative)
            report['failures'].append({'file': relative, 'code': getattr(exc, 'code', type(exc).__name__),
                                       'message': str(exc)})
        if index % 100 == 0:
            print(f'{index}/{len(roots)} files; {expansion.counts}', flush=True)
    report['sources_unchanged'] = all(digest(Path(path)) == value for path, value in sources.items())
    report['templates_unchanged'] = all(digest(settings.inline_directory / path) == value
                                      for path, value in expansion.templates.manifest.items())
    report['research_lists_unchanged'] = all(digest(Path(path)) == value for path, value in protected_lists.items())
    report['inline_scripts'] = expansion.counts
    report['logical_operations'] = dict(statistics.logical)
    report['expanded_nodes_in_successful_files'] = statistics.node_count
    report['status'] = 'partial' if report['failures'] else 'complete'
    report['excluded_text'] = dict(statistics.excluded)
    report['statistics_scope'] = 'Successfully parsed and fully expanded independent files only.'
    output = output_path(settings.work, 'stage6/corpus_report.json', settings.protected)
    output.parent.mkdir(parents=True, exist_ok=True)
    report['list_counts'] = statistics.write(output.parent / 'text_frequency')
    report['inline_sources'] = dict(sorted(expansion.templates.manifest.items()))
    report['diagnostics'] = diagnostics.data['diagnostics']
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key not in ('diagnostics', 'inline_sources')}, indent=2))
    return not all(report[key] for key in ('sources_unchanged', 'templates_unchanged', 'research_lists_unchanged'))


if __name__ == '__main__':
    raise SystemExit(audit())
