"""Builder/analyzer integration and intentional inline exclusion accounting."""

from pathlib import Path
from unittest.mock import patch

from support import BuildFixture, PRODUCT_ROOT
from sttv.analysis.operations import analyze
from sttv.common.json_io import json_text, read_json
from sttv.sources.settings import load_settings


class StageFourIntegrationTests(BuildFixture):
    def test_builder_and_analyzer_skip_without_signature_validation(self):
        self.write_script('base.txt', '''tech_a = {
 potential = { and = { is_ai = no inline_script = { bad = = $OPEN } } }
 weight_modifier = { inline_script = unknown/path }
 technology_swap = { name = tech_a_variant trigger = { inline_script = {} } }
}''')
        before = self.hashes()
        with patch('sttv.script.rules.ScriptRules.inline', side_effect=AssertionError('No inline validation')):
            result = self.run_build()
            self.assertEqual(result['status'], 'success', result['diagnostics'])
            self.assertEqual(result['counts']['skipped_inline_scripts'], 3)
            fields = self.database()['technologies']['tech_a']['fields']
            self.assertEqual(fields['potential']['entries'][0]['key'], 'AND')
            self.assertEqual(fields['weight_modifier'][0]['entries'], [])
            settings = load_settings(self.variable_file, self.config_file)
            analysis = analyze(settings, PRODUCT_ROOT / 'config/analysis.json')
            self.assertEqual(analysis['status'], 'complete')
            self.assertEqual(analysis['counts']['skipped_inline_scripts'], 3)
            self.assertFalse(any(row['command'] == 'inline_script' for row in analysis['observations']))
        self.assertEqual(before, self.hashes())

    def test_unknown_commands_and_broken_boundaries_still_preserve_database(self):
        self.assertEqual(self.run_build()['counts']['skipped_inline_scripts'], 0)
        before = self.database_path().read_bytes()
        for text, code in [('tech_a = { potential = { future_command = yes } }', 'unsupported_command'),
                           ('tech_a = { inline_script = {', 'unterminated_block')]:
            with self.subTest(code=code):
                self.write_script('base.txt', text)
                result = self.run_build()
                self.assertEqual(result['status'], 'failed')
                self.assertIn(code, self.errors(result))
                self.assertEqual(before, self.database_path().read_bytes())

    def test_selected_logical_configuration_reaches_analyzer(self):
        self.assertEqual(self.run_build()['status'], 'success')
        work = Path(self.variables['WORK_DIR'])
        path = work / 'logical.json'
        config = read_json(PRODUCT_ROOT / 'config/parser/logical_operators.json')
        config['operators'] = ['CustomLogic']
        path.write_text(json_text(config), encoding='utf-8')
        self.options['parser']['logical_operators'] = {'base': 'work', 'path': 'logical.json'}
        self.config_file.write_text(json_text(self.options), encoding='utf-8')
        self.write_script('base.txt', 'tech_a = { potential = { customlogic = { is_ai = no } } }')
        settings = load_settings(self.variable_file, self.config_file)
        result = analyze(settings, PRODUCT_ROOT / 'config/analysis.json')
        self.assertTrue(any(row['command'] == 'CustomLogic' for row in result['observations']))
        self.assertEqual(result['counts']['skipped_inline_scripts'], 0)
