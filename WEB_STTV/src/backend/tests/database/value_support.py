"""Fixtures shared by calculation expansion acceptance tests."""

import json

from support import BuildFixture
from sttv.common.paths import PRODUCT_ROOT


class ValueFixture(BuildFixture):
    def setup_values(self, definitions='constant={base=1.25}', caller='factor=value:constant'):
        (self.values / 'definitions.txt').write_text(definitions, encoding='utf-8')
        self.write_script('base.txt', caller)

    def document(self):
        report = self.run_build()
        self.assertEqual(report['status'], 'success', report['diagnostics'])
        return self.database()['documents'][0], report

    def change_options(self, kind, **changes):
        options = json.loads((PRODUCT_ROOT / f'config/parser/{kind}.json').read_text())
        options.update(changes)
        path = self.root / 'work' / f'{kind}.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(options), encoding='utf-8')
        self.options['parser'][kind] = dict(base='work', path=path.name)
