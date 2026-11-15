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
from sttv.database.storage import read_database
from sttv.script.nodes import Located
from sttv.script.parser import parse_text
from sttv.sources.expansion import expansion_context
from sttv.sources.files import selected_files
from sttv.sources.settings import load_settings


def compare(expected, actual):
    """Compare every AST field independently of the production serializer."""
    count = 0
    if is_dataclass(expected):
        names = {field.name for field in fields(expected)}
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


def audit():
    variables = PRODUCT_ROOT / 'global_variables.json'
    original = load_settings(variables, PRODUCT_ROOT / 'config/backend.json')
    folder = output_path(original.work, 'stage6', original.protected)
    folder.mkdir(parents=True, exist_ok=True)
    options = original.options
    options['outputs'] = {'database': 'stage6/database.json', 'report': 'stage6/build_report.json'}
    config = folder / 'backend.json'
    config.write_text(json_text(options), encoding='utf-8')
    settings = load_settings(variables, config)
    selected = selected_files(settings)
    before = {str(path): digest(path) for path, _ in selected}
    started = perf_counter()
    first = build(variables, config)
    assert first['status'] == 'success', first
    build_seconds = perf_counter() - started
    database = read_database(settings.database)
    context = expansion_context(settings)
    nodes = 0
    assert len(selected) == len(database['documents'])
    for (path, encoding), saved in zip(selected, database['documents']):
        relative = path.relative_to(settings.game).as_posix()
        assert saved['source'] == {'root': 'STELLARIS_ROOT', 'file': relative}
        parsed = parse_text(path.read_text(encoding=encoding), settings.syntax, relative, expansion=context)
        nodes += compare(parsed.items, saved['items'])
        compare(parsed.metadata, saved['metadata'])
    assert nodes == first['counts']['nodes']
    initial = digest(settings.database)
    second = build(variables, config)
    assert second['status'] == 'success', second
    assert digest(settings.database) == initial
    assert all(digest(Path(path)) == value for path, value in before.items())
    assert all(digest(settings.inline_directory / path) == value for path, value in first['inline_sources'].items())
    report = {'status': 'success', 'counts': first['counts'], 'database_sha256': initial,
              'database_bytes': settings.database.stat().st_size, 'build_seconds': round(build_seconds, 3),
              'total_seconds': round(perf_counter() - started, 3), 'ast_fields_match': True,
              'repeatable': True, 'sources_unchanged': True, 'templates_unchanged': True}
    (folder / 'real_validation_report.json').write_text(json_text(report), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    audit()
