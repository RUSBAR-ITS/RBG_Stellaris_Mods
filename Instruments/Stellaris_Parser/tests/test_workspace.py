"""Independent CLI acceptance with a selected mod, nested calls and variables."""

import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


class WorkspaceTests(unittest.TestCase):
    def test_mod_override_and_expansion(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            sources = {
                'game/common/inline_scripts/part.txt': 'wrong = 0',
                'game/common/scripted_variables/globals.txt': '@count = 7',
                'game/common/scripted_effects/apply.txt': 'do_sample = { amount = @count }',
                'mod/common/inline_scripts/part.txt': 'do_sample = yes',
                'mod/common/technology/demo.txt': 'sample = { inline_script = part }',
            }
            for name, text in sources.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding='utf-8')
            (root / 'sources.json').write_text(json.dumps({'roots': ['mod', 'game'],
                                                         'library_directory': 'artifacts/libraries'}), encoding='utf-8')
            cmd = [sys.executable, '-m', 'stellaris_parser', 'parse', '--config', 'sources.json',
                   '--rebuild-libraries', '--output', 'tree.json', 'common/technology/demo.txt']
            subprocess.run(cmd, cwd=root, check=True)
            document = json.loads((root / 'tree.json').read_text(encoding='utf-8'))
            fields = document['items'][0]['value']['items']
            self.assertEqual([(n['key']['text'], n['value']['text']) for n in fields], [('amount', '7')])
            self.assertEqual([e['kind'] for e in document['metadata']['expansions']],
                             ['inline_script', 'scripted_effect'])
            cmd[cmd.index('tree.json')] = 'mod/common/technology/demo.txt'
            self.assertNotEqual(subprocess.run(cmd, cwd=root, capture_output=True).returncode, 0)
            self.assertEqual((root / 'mod/common/technology/demo.txt').read_text(), sources['mod/common/technology/demo.txt'])
