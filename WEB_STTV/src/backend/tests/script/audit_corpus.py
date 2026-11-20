"""Audit expanded sources without changing game files or curated research lists."""

import hashlib
import json
from collections import Counter
from pathlib import Path

from support import PRODUCT_ROOT
from sttv.common.errors import BuildError
from sttv.common.paths import output_path
from sttv.common.report import Report
from stellaris_parser.script.parser import parse_text
from stellaris_parser.script.serialization import serialize_document, walk_nodes
from sttv.database.history import validate_history
from sttv.sources.expansion import expansion_context, independent_sources, source_exclusion
from sttv.sources.settings import check_sources, load_settings
from sttv.sources.static_variables import variable_processor
from script.corpus_statistics import Statistics

PROSE = {'common/HOW_TO_MAKE_NEW_SHIPS.txt', 'common/edicts/99_README_EDICTS.txt'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(*, library_mode):
    settings = load_settings(PRODUCT_ROOT / 'global_variables.json', PRODUCT_ROOT / 'config/backend.json', dataset='technologies')
    from sttv.libraries.operation import library_operation
    with library_operation(settings, library_mode) as snapshot:
        result = audit_prepared(settings)
        snapshot.inventory.verify()
        return result


def audit_prepared(settings):
    check_sources(settings)
    files = sorted(path for folder in ('common', 'events')
                   for path in (settings.game / folder).rglob('*.txt') if path.is_file())
    roots = list(independent_sources(files, settings))
    exclusions = Counter(source_exclusion(path, settings) for path in files)
    protected_lists = {str(p): digest(p) for p in (settings.work / 'text_frequency').rglob('*.txt')}
    diagnostics, statistics = Report(), Statistics(settings.static_rules)
    variables = variable_processor(settings, diagnostics)
    expansion = expansion_context(settings, diagnostics, variables)
    report = {'physical_txt_files': len(files), 'independent_files': len(roots), 'parsed': 0,
              'excluded_template_files': exclusions['INLINE_SCRIPTS_DIR'],
              'excluded_scripted_effect_files': exclusions['SCRIPTED_EFFECTS_DIR'],
              'excluded_scripted_trigger_files': exclusions['SCRIPTED_TRIGGERS_DIR'],
              'excluded_scripted_variable_files': exclusions['SCRIPTED_VARIABLES_DIR'],
              'excluded_script_value_files': exclusions['SCRIPT_VALUES_DIR'], 'empty': 0, 'prose': [],
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
            variables.apply(document)
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
    report['static_variables'] = diagnostics.data['counts']['static_variables']
    report['scripted_calls'] = expansion.library.counts
    report['parameters'] = expansion.parameter_counts
    report['max_call_depth'] = expansion.max_depth
    report['named_sources_unchanged'] = all(digest(settings.game / path) == value
          for key in ('scripted_effect_sources', 'scripted_trigger_sources', 'script_value_sources') for path, value in diagnostics.data[key].items())
    report['static_variable_sources'] = diagnostics.data['static_variable_sources']
    report['variable_sources_unchanged'] = all(digest(settings.game / path) == value
                                             for path, value in report['static_variable_sources'].items())
    report['logical_operations'] = dict(statistics.logical)
    report['expanded_nodes_in_successful_files'] = statistics.node_count
    report['status'] = 'partial' if report['failures'] else 'complete'
    report['excluded_text'] = dict(statistics.excluded)
    report['statistics_scope'] = 'Successfully expanded independent files after static substitution; declarations excluded.'
    output = output_path(settings.work, 'stage9/corpus_report.json', settings.protected)
    output.parent.mkdir(parents=True, exist_ok=True)
    report['list_counts'] = statistics.write(output.parent / 'text_frequency')
    report['inline_sources'] = dict(sorted(expansion.templates.manifest.items()))
    report['diagnostics'] = diagnostics.data['diagnostics']
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items()
                      if key not in ('diagnostics', 'inline_sources', 'static_variable_sources')}, indent=2))
    return not all(report[key] for key in ('sources_unchanged', 'templates_unchanged', 'variable_sources_unchanged',
                                         'research_lists_unchanged', 'named_sources_unchanged'))


if __name__ == '__main__':
    import argparse
    from sttv.libraries.operation import add_mode_arguments
    parser = argparse.ArgumentParser()
    add_mode_arguments(parser)
    raise SystemExit(audit(library_mode=parser.parse_args().library_mode))
