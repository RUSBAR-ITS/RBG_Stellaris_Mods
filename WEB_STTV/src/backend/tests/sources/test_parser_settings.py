"""Parser selection, persistence boundaries, and shared analyzer integration."""

import json
import subprocess
import sys
from pathlib import Path

from support import BuildFixture, PRODUCT_ROOT
from sttv.analysis.operations import analyze
from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.sources.settings import load_settings


class ParserSettingsTests(BuildFixture):
    def initialize(self):
        self.assertEqual(self.run_build()['status'], 'success')
        return load_settings(self.variable_file, self.config_file)

    def select_work_configs(self):
        work = Path(self.variables['WORK_DIR'])
        folder = work / 'parser'
        folder.mkdir(parents=True, exist_ok=True)
        for name in ('lexical', 'constructs', 'logical_operators'):
            (folder / f'{name}.json').write_bytes((PRODUCT_ROOT / f'config/parser/{name}.json').read_bytes())
            self.options['parser'][name] = {'base': 'work', 'path': f'parser/{name}.json'}
        return folder

    def test_both_bases_and_other_process_directory(self):
        self.initialize()
        baseline = self.database_path().read_bytes()
        self.select_work_configs()
        self.assertEqual(self.run_build()['status'], 'success')
        result = subprocess.run([sys.executable, '-B', str(PRODUCT_ROOT / 'src/backend/main.py'),
                                 '--variables', str(self.variable_file), '--config', str(self.config_file)],
                                cwd=self.root, capture_output=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(baseline, self.database_path().read_bytes())

    def test_missing_logical_config_or_selection_never_uses_defaults(self):
        self.initialize()
        baseline = self.database_path().read_bytes()
        folder = self.select_work_configs()
        (folder / 'logical_operators.json').unlink()
        result = self.run_build()
        self.assertEqual(result['status'], 'failed')
        self.assertIn('logical_operators.json', result['diagnostics'][0]['message'])
        del self.options['parser']['logical_operators']
        self.assertEqual(self.run_build()['status'], 'failed')
        self.assertEqual(baseline, self.database_path().read_bytes())

    def test_logical_configuration_is_protected_from_outputs(self):
        self.initialize()
        folder = self.select_work_configs()
        path = folder / 'logical_operators.json'
        before = path.read_bytes()
        self.options['outputs']['database'] = 'parser/logical_operators.json'
        self.assertIn('output_collision', self.errors(self.run_build()))
        self.assertEqual(path.read_bytes(), before)

    def test_invalid_or_missing_selected_config_preserves_all_outputs_without_fallback(self):
        settings = self.initialize()
        before = {path: path.read_bytes() for path in (settings.database, settings.registry,
                  settings.generation_report, settings.report)}
        folder = self.select_work_configs()
        for content in ('{"format_version": 999}', '{"format_version":1,"format_version":1}', None):
            path = folder / 'lexical.json'
            if content is None:
                path.unlink()
            else:
                path.write_text(content, encoding='utf-8')
            result = self.run_build()
            self.assertEqual(result['status'], 'failed')
            self.assertFalse(result['registry_written'])
            self.assertIn('lexical.json', result['diagnostics'][0]['message'])
            self.assertEqual(before, {path: path.read_bytes() for path in before})

    def test_config_files_are_protected_from_output_collisions(self):
        self.initialize()
        folder = self.select_work_configs()
        baseline = (folder / 'lexical.json').read_bytes()
        self.options['outputs']['database'] = 'parser/lexical.json'
        result = self.run_build()
        self.assertIn('output_collision', self.errors(result))
        self.assertEqual(baseline, (folder / 'lexical.json').read_bytes())

    def test_registry_operator_mismatch_is_rejected_before_registry_write(self):
        settings = self.initialize()
        before = {path: path.read_bytes() for path in (settings.database, settings.registry, settings.generation_report)}
        folder = self.select_work_configs()
        path = folder / 'lexical.json'
        lexical = read_json(path)
        lexical['operators'] = ['=']
        path.write_text(json.dumps(lexical), encoding='utf-8')
        result = self.run_build()
        self.assertIn('syntax_registry_mismatch', self.errors(result))
        self.assertEqual(before, {path: path.read_bytes() for path in before})

    def test_new_syntax_cannot_replace_database_with_a_lossy_conversion(self):
        self.initialize()
        baseline = self.database_path().read_bytes()
        for body in ('cost = @[ 2 * 3 ]', 'potential = { [[P] is_ai = no ] }',
                     'potential = { { is_ai = no } }', 'potential = rgb { 0 1 0 }'):
            with self.subTest(body=body):
                self.write_script('base.txt', 'tech_a = { ' + body + ' }')
                result = self.run_build()
                self.assertIn('unsupported_database_form', self.errors(result))
                self.assertEqual(baseline, self.database_path().read_bytes())

    def test_analyzer_reports_unsupported_forms_and_uses_selected_syntax(self):
        self.initialize()
        folder = self.select_work_configs()
        lexical_path = folder / 'lexical.json'
        lexical = read_json(lexical_path)
        lexical['line_comment'] = '//'
        lexical_path.write_text(json.dumps(lexical), encoding='utf-8')
        self.config_file.write_text(json.dumps(self.options), encoding='utf-8')
        settings = load_settings(self.variable_file, self.config_file)
        analysis_path = self.root / 'analysis.json'
        analysis_path.write_bytes((PRODUCT_ROOT / 'config/analysis.json').read_bytes())
        self.write_script('base.txt', '// missing = }\ntech_a = { potential = { is_ai = no } }')
        self.assertEqual(analyze(settings, analysis_path)['status'], 'complete')
        self.write_script('base.txt', '// missing = }\ntech_a = { potential = { [[P] is_ai = no ] } }')
        result = analyze(settings, analysis_path)
        self.assertEqual(result['status'], 'partial')
        errors = [row for row in result['diagnostics'] if row['code'] == 'unsupported_analysis_form']
        self.assertEqual(len(errors), 1)
        self.assertEqual((errors[0]['file'], errors[0]['line']), ('base.txt', 2))

    def test_analyzer_rejects_incompatible_registry_before_reading_sources(self):
        self.initialize()
        folder = self.select_work_configs()
        path = folder / 'lexical.json'
        lexical = read_json(path)
        lexical['operators'] = ['=']
        path.write_text(json.dumps(lexical), encoding='utf-8')
        self.config_file.write_text(json.dumps(self.options), encoding='utf-8')
        settings = load_settings(self.variable_file, self.config_file)
        with self.assertRaises(BuildError) as error:
            analyze(settings, PRODUCT_ROOT / 'config/analysis.json')
        self.assertEqual(error.exception.code, 'syntax_registry_mismatch')
