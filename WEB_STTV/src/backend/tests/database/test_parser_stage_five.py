"""Builder and analyzer consume expansion, with transactional failures."""

from pathlib import Path
from unittest.mock import patch

from support import BuildFixture, PRODUCT_ROOT
from sttv.analysis.operations import analyze
from sttv.common.json_io import json_text, read_json
from sttv.sources.settings import load_settings
from sttv.technologies.provenance import resolve_pointer


class StageFiveIntegrationTests(BuildFixture):
    def test_builder_and_analyzer_expand_without_signature_validation(self):
        (self.inline / 'condition.txt').write_text('AND={is_ai=$AI$}', encoding='utf-8')
        (self.inline / 'weight.txt').write_text('factor=2', encoding='utf-8')
        (self.inline / 'empty.txt').write_text('', encoding='utf-8')
        self.write_script('base.txt', '''tech_a = {
 potential = { inline_script = { script = condition AI = no } }
 weight_modifier = { inline_script = weight }
 technology_swap = { name = tech_a_variant trigger = { inline_script = empty } }
}''')
        before = self.hashes()
        with patch('sttv.script.rules.ScriptRules.inline', side_effect=AssertionError('No signature validation')):
            result = self.run_build()
            self.assertEqual(result['status'], 'success', result['diagnostics'])
            self.assertEqual(result['counts']['inline_scripts']['expanded'], 3)
            db = self.database()
            self.assertEqual(db['format_version'], 2)
            fields = db['technologies']['tech_a']['fields']
            self.assertEqual(fields['potential']['entries'][0]['key'], 'AND')
            self.assertEqual(fields['weight_modifier'][0]['entries'][0]['value'], '2')
            self.assertEqual(fields['weight_modifier'][0]['entries'][0]['source']['file'], 'weight.txt')
            calls = db['metadata']['inline_scripts']
            self.assertEqual(calls[2]['result_paths'], [])
            for call in calls:
                for pointer in call['result_paths']:
                    resolve_pointer(db, pointer)
            settings = load_settings(self.variable_file, self.config_file)
            analysis = analyze(settings, PRODUCT_ROOT / 'config/analysis.json')
            self.assertEqual(analysis['status'], 'complete', analysis['diagnostics'])
            self.assertEqual(analysis['counts']['inline_scripts']['expanded'], 3)
            self.assertFalse(any(row['command'] == 'inline_script' for row in analysis['observations']))
        self.assertEqual(before, self.hashes())

    def test_failures_preserve_previous_database(self):
        self.assertEqual(self.run_build()['status'], 'success')
        before = self.database_path().read_bytes()
        for text, code in [('tech_a={potential={future_command=yes}}', 'unsupported_command'),
                           ('tech_a={inline_script={', 'unterminated_block'),
                           ('tech_a={inline_script=missing}', 'missing_inline_template')]:
            with self.subTest(code=code):
                self.write_script('base.txt', text)
                result = self.run_build()
                self.assertEqual(result['status'], 'failed')
                self.assertIn(code, self.errors(result))
                self.assertEqual(before, self.database_path().read_bytes())

    def test_template_update_is_read_by_next_build(self):
        self.write_script('base.txt', 'inline_script=definition')
        path = self.inline / 'definition.txt'
        path.write_text('@base=2 tech_a={cost=@base}', encoding='utf-8')
        self.assertEqual(self.run_build()['status'], 'success')
        self.assertEqual(self.database()['technologies']['tech_a']['fields']['cost']['resolved'], 2)
        path.write_text('@base=3 tech_a={cost=@base}', encoding='utf-8')
        self.assertEqual(self.run_build()['status'], 'success')
        db = self.database()
        self.assertEqual(db['technologies']['tech_a']['fields']['cost']['resolved'], 3)
        self.assertEqual(db['file_variables']['base.txt'][0]['source']['root'], 'INLINE_SCRIPTS_DIR')

    def test_selected_logical_configuration_reaches_analyzer(self):
        self.assertEqual(self.run_build()['status'], 'success')
        path = Path(self.variables['WORK_DIR']) / 'logical.json'
        config = read_json(PRODUCT_ROOT / 'config/parser/logical_operators.json')
        config['operators'] = ['CustomLogic']
        path.write_text(json_text(config), encoding='utf-8')
        self.options['parser']['logical_operators'] = {'base': 'work', 'path': 'logical.json'}
        self.config_file.write_text(json_text(self.options), encoding='utf-8')
        self.write_script('base.txt', 'tech_a={potential={customlogic={is_ai=no}}}')
        settings = load_settings(self.variable_file, self.config_file)
        result = analyze(settings, PRODUCT_ROOT / 'config/analysis.json')
        self.assertTrue(any(row['command'] == 'CustomLogic' for row in result['observations']))
        self.assertEqual(result['counts']['inline_scripts']['encountered'], 0)

    def test_projected_error_retains_innermost_template_location(self):
        self.write_script('base.txt', 'tech_a={potential={inline_script=outer}}')
        (self.inline / 'outer.txt').write_text('AND={inline_script=inner}', encoding='utf-8')
        (self.inline / 'inner.txt').write_text('# comment\nunknown_condition=yes', encoding='utf-8')
        result = self.run_build()
        error = next(row for row in result['diagnostics'] if row['code'] == 'unsupported_command')
        self.assertEqual((error['source'], error['file'], error['line'], error['column']),
                         ('INLINE_SCRIPTS_DIR', 'inner.txt', 2, 1))
        self.assertEqual([call['template'] for call in error['call_chain']], ['outer.txt', 'inner.txt'])
        self.assertEqual(error['root_source']['file'], 'base.txt')
        self.assertGreater(error['provenance']['span']['start'], 0)

    def test_independent_scan_excludes_unreachable_templates(self):
        from sttv.sources.expansion import expansion_context, independent_sources
        from sttv.script.parser import parse_text
        self.run_build()
        settings = load_settings(self.variable_file, self.config_file)
        (self.inline / 'unreachable.txt').write_text('inline_script=missing', encoding='utf-8')
        (self.inline / 'called.txt').write_text('is_ai=yes', encoding='utf-8')
        self.write_script('base.txt', 'inline_script=called')
        context = expansion_context(settings)
        for path in independent_sources(self.game.rglob('*.txt'), settings):
            parse_text(path.read_text(encoding='utf-8-sig'), settings.syntax, str(path), expansion=context)
        self.assertEqual(set(context.templates.manifest), {'called.txt'})

    def test_definition_and_variable_errors_have_template_origin(self):
        self.write_script('base.txt', 'tech_a={} inline_script=p')
        for body, code in [('tech_a={}', 'duplicate_definition'), ('@bad={}', 'invalid_variable_definition')]:
            with self.subTest(code=code):
                (self.inline / 'p.txt').write_text('# comment\n' + body, encoding='utf-8')
                result = self.run_build()
                error = next(row for row in result['diagnostics'] if row['code'] == code)
                self.assertEqual((error['source'], error['file'], error['line']), ('INLINE_SCRIPTS_DIR', 'p.txt', 2))
                self.assertEqual(error['call_chain'][0]['template'], 'p.txt')
