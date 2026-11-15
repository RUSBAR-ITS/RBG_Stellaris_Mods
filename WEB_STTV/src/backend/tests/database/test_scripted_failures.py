"""Failure isolation, source confinement, and mixed expansion boundaries."""

from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import json

from support import BuildFixture, PRODUCT_ROOT
from sttv.common.errors import BuildError
from sttv.database.validation import validate_database


class ScriptedFailureTests(BuildFixture):
    def effect(self, text):
        (self.effects / 'base.txt').write_text(text, encoding='utf-8')

    def options_for_calls(self, **updates):
        options = json.loads((PRODUCT_ROOT / 'config/parser/scripted_calls.json').read_text())
        options.update(updates)
        work = Path(self.variables['WORK_DIR'])
        work.mkdir(parents=True, exist_ok=True)
        (work / 'calls.json').write_text(json.dumps(options), encoding='utf-8')
        self.options['parser']['scripted_calls'] = dict(base='work', path='calls.json')

    def test_cycles_depth_and_node_budget(self):
        self.effect('first={second=yes} second={first=yes}')
        self.write_script('base.txt', 'first=yes')
        result = self.run_build()
        self.assertIn('scripted_cycle', self.errors(result))
        self.assertEqual(len(result['diagnostics'][0]['call_chain']), 3)
        self.effect('first={inline_script=middle}')
        (self.inline / 'middle.txt').write_text('first=yes', encoding='utf-8')
        self.assertIn('scripted_cycle', self.errors(self.run_build()))
        self.effect('first={second=yes} second={value=yes}')
        self.options_for_calls(max_call_depth=1)
        self.assertIn('expansion_depth', self.errors(self.run_build()))
        self.options_for_calls(max_call_depth=2, max_expanded_nodes=5)
        self.assertIn('expansion_size', self.errors(self.run_build()))
        self.options_for_calls(max_call_depth=2, max_expanded_nodes=6)
        self.assertEqual(self.run_build()['status'], 'success')

    def test_duplicates_and_cross_library_conflicts(self):
        self.effect('known={} KNOWN={}')
        self.assertIn('duplicate_scripted_definition', self.errors(self.run_build()))
        self.effect('known={}')
        (self.triggers / 'base.txt').write_text('known={}', encoding='utf-8')
        self.assertIn('duplicate_scripted_definition', self.errors(self.run_build()))
        (self.triggers / 'base.txt').write_text('OR={}', encoding='utf-8')
        self.assertIn('invalid_scripted_definition', self.errors(self.run_build()))

    def test_unsupported_forms_and_missing_arguments_keep_previous_database(self):
        self.assertEqual(self.run_build()['status'], 'success')
        before = self.database_path().read_bytes()
        self.effect('give={value=$REQUIRED$}')
        for caller, code in [('give=no', 'unsupported_scripted_call'),
                             ('give=yes', 'missing_inline_parameter'),
                             ('give={REQUIRED=1 REQUIRED=2}', 'duplicate_scripted_argument'),
                             ('give={REQUIRED=@absent}', 'unknown_static_variable')]:
            self.write_script('base.txt', caller)
            self.assertIn(code, self.errors(self.run_build()))
            self.assertEqual(self.database_path().read_bytes(), before)

    def test_unused_definitions_are_not_bound_or_expanded(self):
        self.effect('unused={value=$MISSING$ inline_script=absent}')
        self.write_script('base.txt', 'ordinary_unknown_command=yes')
        self.assertEqual(self.run_build()['status'], 'success')

    def test_argument_name_is_not_a_call_and_nested_arguments_are_isolated(self):
        self.effect('known={value=$known$} outer={known=yes}')
        self.write_script('base.txt', 'known={known=9}')
        self.assertEqual(self.run_build()['status'], 'success')
        self.write_script('base.txt', 'outer={known=9}')
        self.assertIn('missing_inline_parameter', self.errors(self.run_build()))

    def test_trigger_path_confinement_and_missing_directory(self):
        self.variables['SCRIPTED_TRIGGERS_DIR'] = '../outside'
        self.assertIn('unsafe_source', self.errors(self.run_build()))
        self.variables['SCRIPTED_TRIGGERS_DIR'] = 'common/missing'
        self.assertIn('source_unavailable', self.errors(self.run_build()))

    def test_corrupt_mixed_history_is_rejected_without_sources(self):
        self.effect('give={inline_script=part}')
        (self.inline / 'part.txt').write_text('value=1', encoding='utf-8')
        self.write_script('base.txt', 'give=yes')
        self.assertEqual(self.run_build()['status'], 'success')
        for change in ('parent', 'kind', 'origin', 'range'):
            database = deepcopy(self.database())
            doc = database['documents'][0]
            record = doc['metadata']['expansions'][1]
            if change == 'parent':
                record['parent_id'] = record['id']
            elif change == 'kind':
                record['kind'] = 'scripted_effect'
            elif change == 'origin':
                doc['items'][0]['origin']['expansion_id'] = 'missing'
            else:
                record['insertion']['index'] = 999
            with self.subTest(change=change), self.assertRaises(BuildError):
                validate_database(database)

    def test_input_change_before_publication_is_detected(self):
        from sttv.sources.verification import verify_inputs
        def changed(settings, report):
            self.effect('changed={}')
            return verify_inputs(settings, report)
        self.effect('before={}')
        self.assertEqual(self.run_build()['status'], 'success')
        before = self.database_path().read_bytes()
        with patch('sttv.builder.verify_inputs', changed):
            self.assertIn('source_changed', self.errors(self.run_build()))
        self.assertEqual(self.database_path().read_bytes(), before)

    def test_nested_declarations_and_ambiguous_reference_are_errors(self):
        self.effect('give={@nested=2}')
        self.write_script('base.txt', 'give=yes')
        self.assertIn('nested_static_declaration', self.errors(self.run_build()))
        self.effect('@prefix_value=2 give={amount=@prefix_$END$}')
        self.write_script('base.txt', '@prefix_value=3 give={END=value}')
        self.assertIn('ambiguous_static_environment', self.errors(self.run_build()))
