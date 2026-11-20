"""Enclosing trait context survives nested icon calls without inferred game rules."""
from stellaris_parser.schema import CONFIG


import copy
import json
from pathlib import Path

from support import BuildFixture, PRODUCT_ROOT
from sttv.common.json_io import read_json


class TraitClassTests(BuildFixture):
    def setUp(self):
        super().setUp()
        rule = next(copy.deepcopy(r) for r in read_json(CONFIG / 'source_exceptions.json')['rules']
                    if r['id'] == 'sttv_trait_icon_class')
        rule['match'].update(root_files=['common/technology/base.txt'], definition_file='common/inline_scripts/part.txt')
        path = Path(self.variables['WORK_DIR']) / 'trait_corrections.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'format_version': 1, 'rules': [rule]}), encoding='utf-8')
        self.options['parser']['source_exceptions'] = {'base': 'work', 'path': path.name}
        (self.inline / 'part.txt').write_text('icon_class=$CLASS$', encoding='utf-8')
        (self.inline / 'outer.txt').write_text('nested={inline_script=part}', encoding='utf-8')

    def test_single_multiple_and_explicit_with_original_provenance(self):
        self.write_script('base.txt', 'one={inline_script=outer leader_class={commander}} '
            'two={leader_class={scientist official} inline_script=part} '
            'three={leader_class={commander} inline_script={script=part CLASS=explicit}}')
        before = self.hashes()
        report = self.run_build()
        self.assertEqual(report['status'], 'success', report['diagnostics'])
        self.assertEqual(self.hashes(), before)
        rows = self.database()['documents'][0]['items']
        first = rows[0]['value']['items'][0]['value']['items'][0]['value']
        self.assertEqual(first['text'], 'commander')
        self.assertEqual(first['origin']['file'], 'common/technology/base.txt')
        self.assertEqual(rows[1]['value']['items'][1]['value']['text'], 'leader')
        self.assertEqual(rows[2]['value']['items'][1]['value']['text'], 'explicit')
        self.assertEqual(len(report['source_exceptions']), 2)
        self.assertIn('one/leader_class', report['source_exceptions'][0]['value_source'])
        self.assertEqual(len(report['source_exceptions'][0]['call_chain']), 2)

    def test_invalid_missing_duplicate_and_wrong_context_are_errors(self):
        for text in ('bad={inline_script=part}',
                     'bad={leader_class=commander inline_script=part}',
                     'bad={leader_class={mystery} inline_script=part}',
                     'bad={leader_class={} inline_script=part}',
                     'bad={leader_class={commander} leader_class={scientist} inline_script=part}',
                     'other={leader_class={commander}} inline_script=part'):
            with self.subTest(text=text):
                self.write_script('base.txt', text)
                self.assertIn('source_exception_object', self.errors(self.run_build()))

    def test_explicit_ancestor_argument_is_forwarded_without_reclassification(self):
        self.write_script('base.txt', 'trait={leader_class={scientist} inline_script={script=outer CLASS=leader}}')
        report = self.run_build()
        self.assertEqual(report['status'], 'success', report['diagnostics'])
        node = self.database()['documents'][0]['items'][0]['value']['items'][1]['value']['items'][0]
        self.assertEqual(node['value']['text'], 'leader')
        self.assertEqual(node['value']['origin']['file'], 'common/technology/base.txt')
        self.assertTrue(report['source_exceptions'][0]['value_source'].endswith(':class'))
        self.assertNotIn('unused_inline_argument', [d['code'] for d in report['diagnostics']])

    def test_other_file_and_template_remain_unresolved(self):
        self.write_script('outside.txt', 'trait={leader_class={commander} inline_script=part}')
        self.assertIn('missing_inline_parameter', self.errors(self.run_build()))
        self.write_script('outside.txt', '')
        (self.inline / 'other.txt').write_text('icon_class=$CLASS$', encoding='utf-8')
        self.write_script('base.txt', 'trait={leader_class={commander} inline_script=other}')
        self.assertIn('missing_inline_parameter', self.errors(self.run_build()))
