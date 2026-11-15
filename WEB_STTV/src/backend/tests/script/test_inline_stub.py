"""Opaque inline values are skipped before their internal syntax is interpreted."""

from copy import deepcopy
import unittest
from unittest.mock import patch

from support import syntax
from script.assertions import check_document
from sttv.common.errors import BuildError
from sttv.script.inline import expand_inline_script
from sttv.script.nodes import Assignment, LogicalOperation
from sttv.script.parser import parse_text
from sttv.script.serialization import data_entries
from sttv.script.syntax import make_syntax


class InlineStubTests(unittest.TestCase):
    def parse(self, text, selected=None):
        selected = selected or syntax()
        document = parse_text(text, selected, 'fixture.txt')
        check_document(document, selected)
        return document

    def test_reference_block_empty_and_nested_parent_preservation(self):
        for value in ('path/name', '"path/name"', '{}', '{ script = path/name COUNT = 2 }'):
            with self.subTest(value=value):
                text = 'before = 1 parent = { inline_script = ' + value + ' } after = 2'
                doc = self.parse(text)
                self.assertEqual([n.key.text for n in doc.items], ['before', 'parent', 'after'])
                self.assertEqual(doc.items[1].value.items, [])
                self.assertEqual(data_entries(doc)[1].value, [])
                span = doc.skipped_inline_scripts[0]
                self.assertEqual(text[span.start:span.end], 'inline_script = ' + value)

    def test_hook_gets_exact_opaque_value_once_and_does_no_io(self):
        value = '{ inline_script = { script = nested } AND = { bad = = $UNFINISHED } }'
        selected = syntax()
        with patch('sttv.script.parser.expand_inline_script', wraps=expand_inline_script) as hook:
            with patch('builtins.open', side_effect=AssertionError('No file reads')):
                doc = self.parse('inline_script = ' + value, selected)
        hook.assert_called_once()
        payload, source = hook.call_args.args
        self.assertEqual((payload.raw, payload.form), (value, 'block'))
        self.assertEqual(source.text[payload.span.start:payload.span.end], value)
        self.assertEqual(doc.items, [])
        self.assertEqual(len(doc.skipped_inline_scripts), 1)
        self.assertEqual([t.kind for t in doc.tokens].count('opaque_value'), 1)

    def test_braces_in_comments_and_escaped_multiline_strings_are_ignored(self):
        value = '{ # } ignored\n x = "{ \\" }\nmore" nested = { bad = } }'
        doc = self.parse('inline_script = ' + value + '\nOR = {}')
        self.assertEqual(len(doc.items), 1)
        self.assertIsInstance(doc.items[0], LogicalOperation)
        self.assertEqual(doc.skipped_inline_scripts[0].end, len('inline_script = ' + value))

    def test_parameters_formulas_and_conditional_headers_are_not_validated(self):
        for value in ('{ $missing }', '{ x = @[ missing }', '{ [[missing }', '$PATH',
                      '"$PATH"', '{ x = = = }'):
            with self.subTest(value=value):
                self.assertEqual(self.parse('inline_script = ' + value).items, [])

    def test_trivia_and_multiple_calls_keep_ordered_whole_invocation_spans(self):
        text = '\ufeffINLINE_SCRIPT # first\n = # value\n {} x = 1 inline_script = p'
        doc = self.parse(text)
        self.assertEqual(len(doc.skipped_inline_scripts), 2)
        first, second = doc.skipped_inline_scripts
        self.assertEqual((first.line, first.column), (1, 2))
        self.assertLess(first.end, second.start)
        self.assertEqual(doc.items[0].key.text, 'x')

    def test_missing_value_and_unclosed_outer_boundaries_still_fail(self):
        cases = {'': 'missing_value', '# nothing': 'missing_value', '}': 'missing_value',
                 '{': 'unterminated_block', '"bad': 'unterminated_string',
                 '{ x = "bad }': 'unterminated_string'}
        for value, code in cases.items():
            with self.subTest(value=value), self.assertRaises(BuildError) as error:
                self.parse('\ninline_script = ' + value)
            self.assertEqual(error.exception.code, code)
            self.assertEqual(error.exception.line, 2)
            self.assertIn('fixture.txt:2:', str(error.exception))

    def test_non_calls_and_literal_code_are_preserved(self):
        doc = self.parse('x = inline_script "inline_script" = {} inline_script != {} '
                         'text = "inline_script = { }"')
        self.assertEqual(doc.skipped_inline_scripts, [])
        self.assertTrue(all(isinstance(n, Assignment) for n in doc.items))

    def test_inline_keyword_case_and_alternate_delimiters_are_configurable(self):
        forms = deepcopy(syntax().constructs)
        forms['inline_script'] = {'keyword': 'include', 'case_sensitive': True}
        lexical = {**syntax().lexical, 'block': {'open': '(', 'close': ')'}, 'line_comment': '//'}
        selected = make_syntax(lexical, forms, syntax().logical_operators)
        doc = self.parse('include = ( // )\n x = "(" ( bad = ) ) INCLUDE = ()', selected)
        self.assertEqual(len(doc.skipped_inline_scripts), 1)
        self.assertEqual(doc.items[0].key.text, 'INCLUDE')

    def test_explicit_template_document_is_not_skipped_by_its_path(self):
        doc = parse_text('AND = { flag = $P$ }', syntax(), 'common/inline_scripts/test.txt')
        self.assertIsInstance(doc.items[0], LogicalOperation)
        self.assertEqual(doc.skipped_inline_scripts, [])
