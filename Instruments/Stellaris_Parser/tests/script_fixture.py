"""Small game/mod overlay covering all five library kinds and root include history."""

import json
from pathlib import Path

SOURCES = {
    'game/common/inline_scripts/emit.txt': 'wrong = 0',
    'mod/common/inline_scripts/emit.txt': 'amount = @count',
    'game/common/inline_scripts/catalog.txt': 'inline_script = { script = effects NAME = "$NAME$" }',
    'game/common/inline_scripts/effects.txt': '$NAME$_one = { inline_script = emit }\n$NAME$_two = {}',
    'game/common/inline_scripts/empty.txt': '# No definitions',
    'game/common/scripted_effects/source.txt': (
        'first = {}\ninline_script = { script = catalog NAME = alpha }\n'
        'inline_script = empty\ninline_script = { script = catalog NAME = beta }\nlast = {}'),
    'game/common/scripted_variables/globals.txt': '@count = @base',
    'game/common/scripted_variables/base.txt': '@base = 7',
    'game/common/scripted_triggers/checks.txt': 'is_sample = { test = yes }',
    'game/common/script_values/numbers.txt': 'number = { base = 3 }',
    'game/common/technology/demo.txt': 'wrong = 0',
    'mod/common/technology/demo.txt': (
        '@local = 13\nsample = { alpha_one = yes is_sample = yes value = value:number n = @local }'),
    'game/events/demo.txt': '@local = 9\nother = { beta_one = yes n = @local }',
}


def make_fixture(root):
    for name, text in SOURCES.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
    config = root / 'parser.json'
    config.write_text(json.dumps({
        'roots': ['mod', 'game'], 'library_directory': 'artifacts/libraries',
        'batch': {'directories': ['common', 'common/technology', 'events'], 'workers': 2,
                  'output': 'artifacts/scripts', 'exclude_files': ['common/technology/docs.txt']}
    }), encoding='utf-8')
    return config
