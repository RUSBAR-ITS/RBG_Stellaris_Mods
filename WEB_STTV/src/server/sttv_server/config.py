"""Load server settings and localization key rules relative to the settings file."""

import json
from pathlib import Path


def load_config(path: Path):
    settings = json.loads(path.read_text(encoding='utf-8'))
    rules_path = path.parent / settings['localization_keys_file']
    settings['key_rules'] = json.loads(rules_path.read_text(encoding='utf-8'))
    if 'condition_rules_file' in settings:
        rules = json.loads((path.parent / settings['condition_rules_file']).read_text(encoding='utf-8'))
        settings['key_rules']['condition_rules'] = rules
    if 'tree_rules_file' in settings:
        settings['tree_rules'] = json.loads((path.parent / settings['tree_rules_file']).read_text(encoding='utf-8'))
    return settings
