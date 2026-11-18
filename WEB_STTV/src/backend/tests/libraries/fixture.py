"""Small mixed library, including generated definitions and static environments."""

import json
from pathlib import Path

from support import BuildFixture
from sttv.common.json_io import read_json
from sttv.sources.settings import load_settings
from sttv.libraries.operation import library_operation


class LibraryFixture(BuildFixture):
    def setUp(self):
        super().setUp()
        (self.inline/'part.txt').write_text('amount = $COUNT$ value = value:sample_value', encoding='utf-8')
        (self.inline/'definition.txt').write_text('generated = { n = $N$ }', encoding='utf-8')
        (self.effects/'effect.txt').write_text(
            '@local = 3\n effect_a = { inline_script = { script = part COUNT = $N$ } '
            'generated = yes test_a = yes amount = @local }\n'
            'inline_script = { script = definition N = 8 }', encoding='utf-8')
        (self.triggers/'trigger.txt').write_text('test_a = { always = yes }', encoding='utf-8')
        (self.values/'value.txt').write_text('sample_value = { base = @external }', encoding='utf-8')
        self.write_script('base.txt', 'tech_a = { tier = 1 effect_a = { N = 7 } effect_a = { N = 9 } }')
        self.persist()

    def persist(self):
        for path, value in ((self.variable_file, self.variables), (self.config_file, self.options)):
            path.write_text(json.dumps(value), encoding='utf-8')

    def settings(self):
        return load_settings(self.variable_file, self.config_file)

    def prepare(self, mode='rebuild'):
        with library_operation(self.settings(), mode) as snapshot:
            return snapshot

    def manifest(self):
        return Path(self.variables['WORK_DIR'])/'libraries/manifest.json'

    def artifacts(self):
        root = Path(self.variables['WORK_DIR'])
        return [self.manifest(), *(root/row['path'] for row in read_json(self.manifest())['artifacts'])]

    def configuration(self):
        from support import PRODUCT_ROOT
        path = Path(self.variables['WORK_DIR'])/'libraries_config.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        options = read_json(PRODUCT_ROOT/'config/libraries.json')
        self.options['libraries'] = {'base': 'work', 'path': path.name}
        self.persist()
        return path, options
