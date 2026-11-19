"""Compare persisted game trees against parser dataclasses and verify repeatability."""

from dataclasses import fields, is_dataclass
from hashlib import sha256
from pathlib import Path
import json
import re
from time import perf_counter

from support import PRODUCT_ROOT
from sttv.builder import build
from sttv.common.json_io import json_text
from sttv.common.paths import output_path
from sttv.storage import open_set
from sttv.script.nodes import Located
from sttv.script.parser import parse_text
from sttv.sources.expansion import expansion_context
from sttv.sources.files import selected_files
from sttv.sources.settings import load_settings
from database.static_oracle import expected_items, shared_values
from database.value_oracle import verify_surroundings


def compare(expected, actual):
    """Compare every AST field independently of the production serializer."""
    count = 0
    if is_dataclass(expected):
        names = {field.name for field in fields(expected) if field.name != 'environment'}
        if isinstance(expected, Located):
            kind = re.sub(r'(?<!^)(?=[A-Z])', '_', type(expected).__name__).lower()
            assert actual['kind'] == kind
            assert set(actual) == names | {'kind'}
            count = 1
        else:
            assert set(actual) == names
        for name in names:
            count += compare(getattr(expected, name), actual[name])
    elif isinstance(expected, (tuple, list)):
        assert isinstance(actual, list) and len(actual) == len(expected)
        count += sum(compare(left, right) for left, right in zip(expected, actual))
    elif isinstance(expected, dict):
        assert isinstance(actual, dict) and actual.keys() == expected.keys()
        count += sum(compare(value, actual[key]) for key, value in expected.items())
    else:
        assert actual == expected and type(actual) is type(expected), (expected, actual)
    return count


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def audit(*, library_mode):
    variables = PRODUCT_ROOT / 'global_variables.json'
    original = load_settings(variables, PRODUCT_ROOT / 'config/backend.json', dataset='technologies')
    folder = output_path(original.work, 'stage9', original.protected)
    folder.mkdir(parents=True, exist_ok=True)
    options = original.options
    options['outputs'] = {'database': 'stage9/database.json', 'report': 'stage9/build_report.json'}
    config = folder / 'backend.json'
    config.write_text(json_text(options), encoding='utf-8')
    settings = load_settings(variables, config)
    selected = selected_files(settings)
    before = {str(path): digest(path) for path, _ in selected}
    previous = {str(path): digest(path) for path in (original.database, original.report) if path.exists()}
    started = perf_counter()
    first = build(variables, config, library_mode=library_mode)
    print(json.dumps({'first_build': first['status'], 'counts': first['counts'],
                      'diagnostics': first['diagnostics'][:8]}), flush=True)
    assert first['status'] == 'success', first
    build_seconds = perf_counter() - started
    database = {'documents': list(open_set(settings.database).iter_documents('technologies'))}
    from sttv.libraries.operation import library_operation
    with library_operation(settings, "reuse") as snapshot:
        context = expansion_context(settings)
        nodes, substitutions = 0, 0
        shared = shared_values(settings, first['static_variable_sources'])
        assert len(selected) == len(database['documents'])
        for (path, encoding), saved in zip(selected, database['documents']):
            relative = path.relative_to(settings.game).as_posix()
            assert saved['source'] == {'root': 'STELLARIS_ROOT', 'file': relative}
            parsed = parse_text(path.read_text(encoding=encoding), settings.syntax, relative, expansion=context)
            expected, changed = expected_items(parsed, shared)
            nodes += compare(expected, saved['items'])
            substitutions += changed
            compare(parsed.metadata, saved['metadata'])
        assert nodes == first['counts']['nodes']
        assert substitutions == first['counts']['static_variables']['substituted']
        value_check = verify_surroundings(settings, selected, database)
        snapshot.inventory.verify()
    initial = digest(settings.database)
    second = build(variables, config, library_mode=library_mode)
    assert second['status'] == 'success', second
    assert digest(settings.database) == initial
    assert all(digest(Path(path)) == value for path, value in before.items())
    assert all(digest(settings.inline_directory / path) == value for path, value in first['inline_sources'].items())
    assert all(digest(settings.game / path) == value for path, value in first['static_variable_sources'].items())
    assert all(digest(settings.game / path) == value for key in ('scripted_effect_sources', 'scripted_trigger_sources', 'script_value_sources')
               for path, value in first[key].items())
    assert all(digest(Path(path)) == value for path, value in previous.items())
    report = {'status': 'success', 'counts': first['counts'], 'database_sha256': initial,
              'database_bytes': settings.database.stat().st_size, 'build_seconds': round(build_seconds, 3),
              'total_seconds': round(perf_counter() - started, 3), 'ast_fields_match': True,
              'repeatable': True, 'sources_unchanged': True, 'templates_unchanged': True,
              'variable_sources_unchanged': True, 'named_sources_unchanged': True, 'previous_outputs_unchanged': True,
              'independent_substitution_check': substitutions, 'independent_value_check': value_check}
    (folder / 'real_validation_report.json').write_text(json_text(report), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    import argparse
    from sttv.libraries.operation import add_mode_arguments
    parser = argparse.ArgumentParser()
    add_mode_arguments(parser)
    audit(library_mode=parser.parse_args().library_mode)
