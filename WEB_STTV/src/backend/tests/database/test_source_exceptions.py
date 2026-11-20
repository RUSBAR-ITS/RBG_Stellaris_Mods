"""Scoped import corrections, structural effect calls, and parameter environments."""
from stellaris_parser.schema import CONFIG


import copy
import json
from pathlib import Path

from support import BuildFixture, PRODUCT_ROOT
from sttv.common.json_io import read_json


class SourceExceptionTests(BuildFixture):
    def configure(self, rule):
        config = Path(self.variables['WORK_DIR']) / 'corrections.json'
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(json.dumps({'format_version': 1, 'rules': rule}), encoding='utf-8')
        self.options['parser']['source_exceptions'] = {
            'base': 'work', 'path': config.name}

    def missing_rule(self):
        rule = copy.deepcopy(read_json(CONFIG / 'source_exceptions.json')['rules'][1])
        rule['match'].update(root_files=['common/technology/base.txt'], definition_file='common/inline_scripts/part.txt')
        return rule

    def test_relic_alias_scoping_existing_values_comments_and_discarded_branches(self):
        rule = self.missing_rule()
        self.configure([rule])
        (self.inline / 'part.txt').write_text('# gave_relic_$RELIC$\n'
            '[[OFF] ignored=gave_relic_$RELIC$] flag=gave_relic_$RELIC$', encoding='utf-8')
        self.write_script('base.txt', 'inline_script={script=part SELECTED_RELIC=selected}')
        before = self.hashes()
        report = self.run_build()
        self.assertEqual(report['status'], 'success', report['diagnostics'])
        self.assertEqual(self.hashes(), before)
        self.assertEqual(self.database()['documents'][0]['items'][0]['value']['text'], 'gave_relic_selected')
        self.assertEqual(report['counts']['source_exceptions'][rule['id']], 1)
        self.assertEqual(report['source_exceptions'][0]['value_source'], 'SELECTED_RELIC')
        self.write_script('base.txt', 'inline_script={script=part SELECTED_RELIC=selected RELIC=explicit}')
        self.assertEqual(self.run_build()['counts']['source_exceptions'][rule['id']], 0)
        self.assertEqual(self.database()['documents'][0]['items'][0]['value']['text'], 'gave_relic_explicit')
        self.write_script('base.txt', '')
        self.write_script('outside.txt', 'inline_script={script=part SELECTED_RELIC=selected}')
        self.assertIn('missing_inline_parameter', self.errors(self.run_build()))

    def test_conflicting_rules_fail_instead_of_selecting_a_winner(self):
        first = self.missing_rule()
        second = copy.deepcopy(first)
        second['id'] = 'another'
        self.configure([first, second])
        (self.inline / 'part.txt').write_text('flag=gave_relic_$RELIC$', encoding='utf-8')
        self.write_script('base.txt', 'inline_script={script=part SELECTED_RELIC=x}')
        self.assertIn('source_exception_conflict', self.errors(self.run_build()))

    def test_case_insensitive_nested_arguments_and_structural_effect_no(self):
        (self.effects / 'test.txt').write_text('give={inline_script={script=part Bonus=$BONUS$}} empty={value=1}', encoding='utf-8')
        (self.inline / 'part.txt').write_text('amount=$bonus$', encoding='utf-8')
        self.write_script('base.txt', 'give={bonus=7} empty=no')
        result = self.run_build()
        self.assertEqual(result['status'], 'success', result['diagnostics'])
        document = self.database()['documents'][0]
        self.assertEqual([n['value']['text'] for n in document['items']], ['7', '1'])
        self.assertEqual(document['metadata']['expansions'][-1]['invocation']['raw'], 'no')
        self.write_script('base.txt', 'give={bonus=7 BONUS=8}')
        self.assertIn('duplicate_scripted_argument', self.errors(self.run_build()))

    def test_composed_variable_uses_one_common_declaration_but_not_equal_different_locals(self):
        (self.static / 'test.txt').write_text('@prefix_value=1500', encoding='utf-8')
        (self.effects / 'test.txt').write_text('give={amount=@prefix_$END$}', encoding='utf-8')
        self.write_script('base.txt', 'give={END=value}')
        report = self.run_build()
        self.assertEqual(report['status'], 'success', report['diagnostics'])
        self.assertEqual(self.database()['documents'][0]['items'][0]['value']['text'], '1500')
        (self.effects / 'test.txt').write_text('@prefix_value=1500 give={amount=@prefix_$END$}', encoding='utf-8')
        self.write_script('base.txt', '@prefix_value=1500 give={END=value}')
        self.assertIn('ambiguous_static_environment', self.errors(self.run_build()))

    def test_reference_correction_is_exact_logged_and_keeps_original_history(self):
        rule = copy.deepcopy(read_json(CONFIG / 'source_exceptions.json')['rules'][0])
        rule['match'].update(root_files=['common/technology/base.txt'], file='common/technology/base.txt')
        self.configure([rule])
        (self.values / 'test.txt').write_text('scripted_modifier_mult={base=$MODIFIER$}', encoding='utf-8')
        self.write_script('base.txt', 'amount=' + rule['match']['scalar'])
        report = self.run_build()
        self.assertEqual(report['status'], 'success', report['diagnostics'])
        self.assertEqual(report['counts']['source_exceptions'][rule['id']], 1)
        history = self.database()['documents'][0]['metadata']['expansions'][0]
        self.assertEqual(history['invocation']['raw'], rule['match']['scalar'])
        self.write_script('base.txt', 'amount=' + rule['action']['replace_scalar'])
        self.assertEqual(self.run_build()['counts']['source_exceptions'][rule['id']], 0)
        self.write_script('base.txt', 'amount=value:scripted_modifier_mult|MODIFIER|other||')
        self.assertIn('invalid_script_value_arguments', self.errors(self.run_build()))

    def test_literal_argument_has_configuration_provenance_and_existing_value_wins(self):
        rule = copy.deepcopy(read_json(CONFIG / 'source_exceptions.json')['rules'][2])
        rule['match'].update(root_files=['common/technology/base.txt'],
                             definition_file='common/scripted_effects/test.txt', call_name='give')
        self.configure([rule])
        (self.effects / 'test.txt').write_text('give={amount=$RANDOM$}', encoding='utf-8')
        for extra, expected, applications in [('', '0', 1), ('RANDOM=9', '9', 0)]:
            self.write_script('base.txt', 'give={POP_GROUP=x ETHOS=y PERCENTAGE=1 ' + extra + '}')
            report = self.run_build()
            self.assertEqual(report['status'], 'success', report['diagnostics'])
            value = self.database()['documents'][0]['items'][0]['value']
            self.assertEqual(value['text'], expected)
            self.assertEqual(report['counts']['source_exceptions'][rule['id']], applications)
            if applications:
                self.assertIn('WORK_DIR', json.dumps(value['origin']))
