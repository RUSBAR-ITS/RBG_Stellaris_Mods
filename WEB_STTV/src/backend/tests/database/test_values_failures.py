"""Reject malformed references and preserve earlier published output on failure."""

from database.value_support import ValueFixture


class ValueFailureTests(ValueFixture):
    def test_bad_forms_have_expansion_diagnostics(self):
        for text, code in [('value:', 'invalid_script_value_reference'),
                           ('.value:x', 'invalid_script_value_reference'),
                           ('owner..value:x', 'invalid_script_value_reference'),
                           ('value:x|A|1', 'invalid_script_value_arguments'),
                           ('value:x|A|', 'invalid_script_value_arguments'),
                           ('value:x||1|', 'invalid_script_value_argument'),
                           ('value:x|A|1|A|2|', 'duplicate_scripted_argument'),
                           ('value:missing', 'unknown_script_value')]:
            with self.subTest(text=text):
                self.setup_values('x={base=1}', 'v='+text)
                report = self.run_build()
                self.assertIn(code, self.errors(report))
                error = next(d for d in report['diagnostics'] if d['severity'] == 'error')
                self.assertEqual(error['call_chain'][-1]['kind'], 'script_value')
                self.assertEqual(report['counts']['scripted_calls']['script_value']['failed'], 1)

    def test_case_collisions_and_case_sensitive_selection(self):
        self.setup_values('x={base=1} X={base=2}', 'v=value:x')
        self.assertIn('duplicate_scripted_definition', self.errors(self.run_build()))
        self.change_options('scripted_calls', name_case_sensitive=True)
        doc, _ = self.document()
        self.assertEqual(doc['items'][0]['value']['body']['items'][0]['value']['text'], '1')

    def test_unreached_missing_parameters_and_static_references(self):
        self.setup_values('unused={base=$REQUIRED$ add=@unknown} x={base=2}', 'v=value:x')
        self.document()
        self.write_script('base.txt', 'v=value:unused|REQUIRED|3|')
        report = self.run_build()
        self.assertIn('unknown_static_variable', self.errors(report))
        error = next(d for d in report['diagnostics'] if d['severity'] == 'error')
        self.assertEqual(error['file'], 'common/script_values/definitions.txt')
        self.assertEqual(error['call_chain'][-1]['template'], 'unused')

    def test_nested_arguments_do_not_inherit_parent_bindings(self):
        self.setup_values('outer={base=value:inner} inner={base=$N$}', 'v=value:outer|N|1|')
        self.assertIn('missing_inline_parameter', self.errors(self.run_build()))

    def test_cycles_and_shared_limits(self):
        self.setup_values('x={base=value:y} y={base=value:x}', 'v=value:x')
        self.assertIn('scripted_cycle', self.errors(self.run_build()))
        self.setup_values('x={base=value:y} y={base=1}', 'v=value:x')
        self.change_options('scripted_calls', max_call_depth=1)
        self.assertIn('expansion_depth', self.errors(self.run_build()))
        self.change_options('scripted_calls', max_expanded_nodes=1)
        self.assertIn('expansion_size', self.errors(self.run_build()))

    def test_mixed_cycle_keeps_all_frames(self):
        self.setup_values('x={emit=yes}', 'v=value:x')
        (self.effects/'a.txt').write_text('emit={ready=yes}', encoding='utf-8')
        (self.triggers/'a.txt').write_text('ready={some_field=value:x}', encoding='utf-8')
        report = self.run_build()
        self.assertIn('scripted_cycle', self.errors(report))
        error = next(d for d in report['diagnostics'] if d['severity'] == 'error')
        self.assertEqual([f['kind'] for f in error['call_chain']],
                         ['script_value', 'scripted_effect', 'scripted_trigger', 'script_value'])

    def test_failure_preserves_database_and_refreshes_library(self):
        self.setup_values()
        self.document()
        before = self.database_path().read_bytes()
        (self.values/'definitions.txt').write_text('constant={base=$MISSING$}', encoding='utf-8')
        failed = self.run_build()
        self.assertIn('missing_inline_parameter', self.errors(failed))
        self.assertEqual(self.database_path().read_bytes(), before)
        (self.values/'definitions.txt').write_text('constant={base=7}', encoding='utf-8')
        self.document()
        self.assertNotEqual(self.database_path().read_bytes(), before)

    def test_invalid_markers_and_config_output_collision(self):
        self.setup_values()
        self.change_options('script_values', reference_prefix='=')
        self.assertIn('script_value_configuration', self.errors(self.run_build()))
        self.change_options('script_values')
        self.options['outputs']['database'] = 'script_values.json'
        self.assertEqual(self.run_build()['status'], 'failed')
