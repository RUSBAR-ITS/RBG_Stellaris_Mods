"""Syntax acceptance and preservation independently of game command rules."""

import unittest
from unittest.mock import patch

from support import syntax
from script.assertions import check_document
from sttv.common.errors import BuildError
from stellaris_parser.script.nodes import Assignment, Block, Conditional, Formula, Scalar, TaggedBlock
from stellaris_parser.script.parser import parse_text
from stellaris_parser.script.serialization import serialize_document


class SyntaxNodeTests(unittest.TestCase):
    def parse(self, text):
        document = parse_text(text, syntax(), 'fixture.txt')
        check_document(document, syntax())
        return document

    def test_unknown_commands_have_no_profile_dependency(self):
        selected = syntax()
        with patch('sttv.common.json_io.read_json', side_effect=AssertionError('No file reads')):
            document = parse_text('invented_command >= arbitrary:value', selected)
        node = document.items[0]
        self.assertEqual((node.key.text, node.operator, node.value.text),
                         ('invented_command', '>=', 'arbitrary:value'))

    def test_coordinates_trivia_unicode_and_multiline_quoted_keys(self):
        text = '\ufeff# comment\r\n"multi\nkey" = "\u0410 # { }\nB"\n'
        doc = self.parse(text)
        node = doc.items[0]
        self.assertTrue(node.key.quoted)
        self.assertEqual(node.key.text, 'multi\nkey')
        self.assertEqual((node.span.line, node.span.column), (2, 1))
        self.assertEqual((node.value.span.end_line, node.value.span.end_column), (4, 3))
        self.assertEqual(text[node.value.span.start:node.value.span.end], node.value.raw)
        self.assertEqual(node.value.parameters, ())

    def test_backslash_runs_do_not_decode_string_content(self):
        for count in range(1, 7):
            content = 'a' + '\\' * count
            text = 'key = "' + content + ('"b"' if count % 2 else '"')
            node = self.parse(text).items[0]
            self.assertEqual(node.value.text, content + ('"b' if count % 2 else ''))

    def test_lists_anonymous_blocks_tags_numeric_keys_and_repetitions(self):
        text = 'items = { { x = y } rgb { 1 2 3 4 } "bare" 10 = {} n = 1 n = 2 }'
        doc = self.parse(text)
        items = doc.items[0].value.items
        self.assertIsInstance(items[0], Block)
        self.assertIsInstance(items[1], TaggedBlock)
        self.assertIsInstance(items[2], Scalar)
        self.assertEqual(len(items[1].block.items), 4)
        self.assertEqual([item.key.text for item in items[3:]], ['10', 'n', 'n'])
        self.assertIsInstance(self.parse('rgb { 0 1 2 }').items[0], TaggedBlock)

    def test_formulas_remain_whole_with_nested_wrappers(self):
        text = 'a = @[ 5 % 2 + @\\[ $P|]$ * 3 ] + "]" # ] ignored\n ]'
        node = self.parse(text).items[0].value
        self.assertIsInstance(node, Formula)
        self.assertIn('5 % 2', node.body)
        self.assertIn('@\\[ $P|]$ * 3 ]', node.body)
        self.assertEqual(node.opener, '@[')
        self.assertEqual(self.parse('x = @\\[ x + 2 ]').items[0].value.opener, '@\\[')

    def test_parameter_fragments_and_empty_defaults(self):
        doc = self.parse('pre_$NAME$_post = "$A$/$B|$/$C|hello world$" $BODY$')
        key, value = doc.items[0].key, doc.items[0].value
        self.assertEqual(key.parameters[0].name, 'NAME')
        self.assertEqual([(p.name, p.default) for p in value.parameters],
                         [('A', None), ('B', ''), ('C', 'hello world')])
        self.assertEqual(doc.items[1].parameters[0].name, 'BODY')
        for scalar in (key, value, doc.items[1]):
            for fragment in scalar.parameters:
                self.assertEqual(doc.source.text[fragment.span.start:fragment.span.end], fragment.raw)

    def test_nested_conditions_preserve_parameters_without_evaluation(self):
        doc = self.parse('[[P] a = { [[!Q] b = $Q|no$ ] } [[R] c = yes ] ]')
        condition = doc.items[0]
        self.assertIsInstance(condition, Conditional)
        self.assertEqual((condition.parameter, condition.negated), ('P', False))
        inner = condition.items[0].value.items[0]
        self.assertEqual((inner.parameter, inner.negated), ('Q', True))

    def test_reference_spelling_and_string_substitutions(self):
        text = "owner?={ @x = @y e = event_target:foo s = value:bar|P|3 id = abc.2 "
        text += "flag = violation@prev.owner fleet = Avogadro's_Moles text = \"[This.GetName] $\" }"
        doc = self.parse(text)
        self.assertEqual(doc.items[0].key.text, 'owner?')
        self.assertEqual(doc.items[0].value.items[-1].value.text, '[This.GetName] $')

    def test_structural_failures_have_file_line_column_and_offset(self):
        examples = {'a = @[': 'unterminated_formula', '[[P] a = 1': 'unterminated_conditional',
                    'a = $P': 'unterminated_parameter', 'a = {': 'unterminated_block',
                    'a = "bad': 'unterminated_string', 'a =': 'missing_value',
                    'a { x = 1 }': 'missing_operator', ']': 'unexpected_token',
                    'a = }': 'missing_value', 'a = = 1': 'missing_value'}
        for text, code in examples.items():
            with self.subTest(text=text), self.assertRaises(BuildError) as error:
                self.parse('\n' + text)
            self.assertEqual(error.exception.code, code)
            self.assertEqual(error.exception.line, 2)
            self.assertGreaterEqual(error.exception.column, 1)
            self.assertIn('fixture.txt:2:', str(error.exception))

    def test_deep_nesting_becomes_a_diagnostic(self):
        with self.assertRaises(BuildError) as error:
            self.parse('x={' * 1500 + '}' * 1500)
        self.assertEqual(error.exception.code, 'nesting_depth')

    def test_serialization_keeps_previously_unrepresentable_nodes(self):
        for text in ('x = @[ 1 + 2 ]', '[[P] x = yes ]', '{ x = yes }',
                     'color = rgb { 0 1 2 }', 'x = { { a = b } }'):
            with self.subTest(text=text):
                self.assertTrue(serialize_document(self.parse(text))["items"])
