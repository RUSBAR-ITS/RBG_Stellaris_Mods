"""Expansion behavior, argument isolation, metadata, and diagnostics."""

from copy import deepcopy
import unittest

from support import PRODUCT_ROOT, syntax
from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.script.inline import Expansion, MemoryTemplates
from sttv.script.nodes import InlineInvocation, LogicalOperation
from sttv.script.parser import parse_text
from support import syntax_payload
from sttv.script.syntax import make_syntax


class InlineExpansionTests(unittest.TestCase):
    def expand(self, text, templates, options=None, selected=None):
        options = options or read_json(PRODUCT_ROOT / 'config/parser/inline_scripts.json')
        self.context = Expansion(MemoryTemplates(templates, options), options)
        return parse_text(text, selected or syntax(), 'caller.txt', expansion=self.context)

    def test_forms_order_duplicates_and_empty_insertions(self):
        text = 'x=0 box={ inline_script="empty" } inline_script=p x=2 inline_script={script=p}'
        doc = self.expand(text, {'p.txt': 'x=1 x=1', 'empty.txt': ''})
        self.assertEqual([n.key.text for n in doc.items], ['x', 'box', 'x', 'x', 'x', 'x', 'x'])
        self.assertEqual(doc.items[1].value.items, [])
        calls = doc.metadata['inline_scripts']
        self.assertEqual([r['insertion']['count'] for r in calls], [0, 2, 2])
        self.assertEqual([r['insertion']['index'] for r in calls], [0, 2, 5])

    def test_nested_forwarding_dynamic_paths_and_isolation(self):
        templates = {'outer.txt': 'inline_script={script=inner_$N$ TECH=$TECHNOLOGY$}',
                     'inner_1.txt': 'inline_script={script=last TECH=$TECH$}',
                     'last.txt': 'has_technology=$TECH$'}
        doc = self.expand('inline_script={script=outer N=1 TECHNOLOGY=tech_a} '
                          'inline_script={script=outer N=1 TECHNOLOGY=tech_b}', templates)
        self.assertEqual([n.value.text for n in doc.items], ['tech_a', 'tech_b'])
        calls = doc.metadata['inline_scripts']
        self.assertEqual(calls[1]['arguments'], [{'name': 'TECH', 'raw': '$TECHNOLOGY$', 'value': 'tech_a'}])
        self.assertEqual(calls[1]['script']['raw'], 'inner_$N$')
        self.assertEqual([c['parent_id'] for c in calls], [None, 'inline_1', 'inline_2', None, 'inline_4', 'inline_5'])
        self.assertEqual(self.context.counts['max_depth'], 3)
        self.assertEqual([c['insertion']['index'] for c in calls], [0, 0, 0, 1, 1, 1])

    def test_logical_parameter_is_scalar_and_inserted_code_is_logic(self):
        doc = self.expand('inline_script={script=p NOT=no BODY="AND={ a=yes } b=no"}',
                          {'p.txt': 'flag=$NOT$ $BODY$'})
        self.assertEqual(doc.items[0].value.text, 'no')
        self.assertIsInstance(doc.items[1], LogicalOperation)
        self.assertEqual(doc.items[2].key.text, 'b')

    def test_parameters_in_keys_strings_formulas_and_empty_values(self):
        doc = self.expand('inline_script={script=p KEY=foo N=2 EMPTY=""}',
                          {'p.txt': '$KEY$_x="pre_$KEY$_$EMPTY$" count=@[ $N$ + 1 ]'})
        self.assertEqual(doc.items[0].key.text, 'foo_x')
        self.assertEqual(doc.items[0].value.text, 'pre_foo_')
        self.assertEqual(doc.items[1].value.body.strip(), '2 + 1')

    def test_comments_are_not_required_bindings_and_unused_warns(self):
        doc = self.expand('inline_script={script=p UNUSED=1}', {'p.txt': '# $MISSING$\nx=yes'})
        self.assertEqual(len(doc.items), 1)
        self.assertEqual(self.context.warnings[0]['code'], 'unused_inline_argument')

    def test_error_table_and_no_silent_skips(self):
        cases = [('{script=p X=1 X=2}', 'x=$X$', 'duplicate_inline_argument'),
                 ('{script=p script=p}', '', 'duplicate_inline_path'),
                 ('{}', '', 'invalid_inline_path'), ('""', '', 'invalid_inline_path'),
                 ('{script=p X={}}', '', 'invalid_inline'),
                 ('p', 'x=$MISSING$', 'missing_inline_parameter'),
                 ('p', 'x=$X|no$', 'unsupported_inline_default'),
                 ('p', '[[X] x=yes ]', 'unsupported_inline_conditional'),
                 ('../p', '', 'invalid_inline_path'), ('missing', '', 'missing_inline_template'),
                 ('{script=p X="$X$"}', 'x=$X$', 'unresolved_inline_parameter')]
        for payload, template, code in cases:
            with self.subTest(code=code), self.assertRaises(BuildError) as error:
                self.expand('inline_script=' + payload, {'p.txt': template})
            self.assertEqual(error.exception.code, code)
            self.assertEqual(len(error.exception.call_chain), 1)
            self.assertEqual(self.context.counts['failed'], 1)

    def test_cycles_and_depth_boundary(self):
        options = read_json(PRODUCT_ROOT / 'config/parser/inline_scripts.json')
        options['max_depth'] = 2
        self.expand('inline_script=p', {'p.txt': 'inline_script=q', 'q.txt': 'x=yes'}, options)
        for templates, code in [({'p.txt': 'inline_script=p'}, 'inline_cycle'),
                                ({'p.txt': 'inline_script=q', 'q.txt': 'inline_script=p'}, 'inline_cycle')]:
            with self.subTest(code=code), self.assertRaises(BuildError) as error:
                self.expand('inline_script=p', templates)
            self.assertEqual(error.exception.code, code)
            self.assertEqual(self.context.counts['failed'], self.context.counts['encountered'])
        with self.assertRaises(BuildError) as error:
            self.expand('inline_script=p', {'p.txt': 'inline_script=q', 'q.txt': 'inline_script=r'}, options)
        self.assertEqual(error.exception.code, 'inline_depth')

    def test_multiline_error_points_to_argument_and_keeps_chain(self):
        with self.assertRaises(BuildError) as error:
            self.expand('inline_script={script=p CODE="x=yes\ny = ="}', {'p.txt': '$CODE$'})
        self.assertEqual(error.exception.provenance['file'], 'caller.txt')
        self.assertEqual(error.exception.provenance['span']['line'], 2)
        self.assertEqual(error.exception.call_chain[0]['template'], 'p.txt')

    def test_template_role_requires_no_loader_and_source_role_does(self):
        text = 'inline_script={script=p X=$OUTER$}'
        doc = parse_text(text, syntax(), role='template')
        self.assertIsInstance(doc.items[0], InlineInvocation)
        with self.assertRaises(BuildError) as error:
            parse_text(text, syntax())
        self.assertEqual(error.exception.code, 'inline_context_required')

    def test_configuration_changes_names_case_and_delimiters(self):
        forms = deepcopy(syntax().constructs)
        forms['inline_script']['keyword'] = 'include'
        forms['parameters'] = {'open': '%', 'close': '%', 'default_separator': '|'}
        selected = make_syntax(syntax().lexical, forms, syntax().logical_operators)
        options = read_json(PRODUCT_ROOT / 'config/parser/inline_scripts.json')
        options.update(path_field='file', parameter_case_sensitive=False)
        doc = self.expand('include={file=p key=yes}', {'p.txt': 'x=%KEY%'}, options, selected)
        self.assertEqual(doc.items[0].value.text, 'yes')

    def test_manual_inclusion_matches_projected_values(self):
        doc = self.expand('box={ inline_script={script=p X=yes} }', {'p.txt': 'a=$X$ OR={b=no}'})
        manual = parse_text('box={a=yes OR={b=no}}', syntax())
        self.assertEqual(syntax_payload(doc), syntax_payload(manual))
        before = syntax_payload(doc)
        doc.metadata['inline_scripts'].append({'irrelevant': 'a a a'})
        self.assertEqual(before, syntax_payload(doc))

    def test_generated_call_and_escaped_quotes_keep_argument_source(self):
        text = r'inline_script={script=outer BODY="inline_script={script=last TECH=tech_a} title=\"hello world\""}'
        doc = self.expand(text, {'outer.txt': '$BODY$', 'last.txt': 'has_technology=$TECH$'})
        call = doc.metadata['inline_scripts'][1]
        self.assertEqual(call['arguments'], [{'name': 'TECH', 'raw': 'tech_a', 'value': 'tech_a'}])
        self.assertEqual(call['script']['raw'], 'last')
        self.assertEqual(call['call_site']['file'], 'caller.txt')
        self.assertEqual(doc.items[1].value.text, 'hello world')

    def test_nested_calls_do_not_inherit_unpassed_bindings(self):
        with self.assertRaises(BuildError) as error:
            self.expand('inline_script={script=outer X=yes}',
                        {'outer.txt': 'inline_script=inner', 'inner.txt': 'x=$X$'})
        self.assertEqual(error.exception.code, 'missing_inline_parameter')
        self.assertEqual(len(error.exception.call_chain), 2)

    def test_frequency_and_scalar_consumers_ignore_history(self):
        from script.corpus_statistics import Statistics
        templates = {'p.txt': 'name=$NAME$ AND={is_ai=no}' }
        doc = self.expand('inline_script={script=p NAME=alpha} inline_script={script=p NAME=alpha}', templates)
        manual = parse_text('name=alpha AND={is_ai=no} name=alpha AND={is_ai=no}', syntax())
        first, second = Statistics(), Statistics()
        first.consume(doc)
        second.consume(manual)
        def signatures(stats):
            return {name: [(r['text'], r['count'], r['roles'], r['right_hand_types']) for r in rows]
                    for name, rows in stats.lists().items()}
        self.assertEqual(signatures(first), signatures(second))
        self.assertEqual(first.logical, second.logical)
        doc.metadata['inline_scripts'].append({'text': 'extra', 'count': 999})
        third = Statistics()
        third.consume(doc)
        self.assertEqual(signatures(first), signatures(third))
