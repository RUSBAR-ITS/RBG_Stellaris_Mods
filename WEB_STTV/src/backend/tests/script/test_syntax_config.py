"""Configuration changes affect parsing without changing engine code."""

from copy import deepcopy
import unittest

from support import syntax
from script.assertions import check_document
from sttv.common.errors import BuildError
from stellaris_parser.script.parser import parse_text
from stellaris_parser.script.syntax import make_syntax


class SyntaxConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.lexical = deepcopy(syntax().lexical)
        self.constructs = deepcopy(syntax().constructs)

    def parse(self, text):
        selected = make_syntax(self.lexical, self.constructs, syntax().logical_operators)
        document = parse_text(text, selected)
        check_document(document, selected)
        return document

    def test_custom_operators_comments_and_tags(self):
        self.lexical['operators'] = ['=', '=>', '>']
        self.lexical['line_comment'] = '//'
        self.constructs['tagged_blocks'].append('vector')
        doc = self.parse('// ignored = }\na=>vector { 1 2 } b = hash#name c>2')
        self.assertEqual(doc.items[0].operator, '=>')
        self.assertEqual(doc.items[0].value.tag.text, 'vector')
        self.assertEqual(doc.items[1].value.text, 'hash#name')
        self.assertEqual(doc.items[2].operator, '>')

    def test_alternate_delimiters_are_used_in_all_states(self):
        self.lexical['block'] = {'open': '(', 'close': ')'}
        self.lexical['string'] = {'quote': "'", 'escape': '\\', 'multiline': True}
        self.constructs['parameters'] = {'open': '%', 'close': '%', 'default_separator': ':'}
        self.constructs['formulas'] = [{'open': '&[', 'close': ']'}]
        self.constructs['conditional'] = {'open': '<<', 'header_close': ':', 'body_close': '>>', 'negation': '~'}
        self.lexical['operators'] = ['=']
        doc = self.parse("<<~P: x = ( y = '&[text]' a = %[fallback]% n = &[1 + %N:2%] ) >>")
        self.assertTrue(doc.items[0].negated)
        self.assertEqual(doc.items[0].items[0].value.items[1].value.parameters[0].name, '[fallback]')

    def test_switches_reject_forms_and_keep_supported_forms(self):
        for flag, bad, good in [('bare_values', 'bare', 'x = 1'),
                                ('anonymous_blocks', '{ x = 1 }', 'x = {}'),
                                ('mixed_blocks', 'x = { bare n = 1 }', 'x = { a b }')]:
            with self.subTest(flag=flag):
                self.constructs = deepcopy(syntax().constructs)
                self.constructs[flag] = False
                self.parse(good)
                with self.assertRaises(BuildError) as error:
                    self.parse(bad)
                self.assertEqual(error.exception.code, 'disabled_form')

    def test_string_and_bom_switches(self):
        self.lexical['allow_initial_bom'] = False
        with self.assertRaises(BuildError) as error:
            self.parse('\ufeffx = 1')
        self.assertEqual(error.exception.code, 'unexpected_bom')
        self.lexical['string']['multiline'] = False
        for text in ('x = "a\nb"', 'x = "a\\\nb"'):
            with self.subTest(text=text), self.assertRaises(BuildError) as error:
                self.parse(text)
            self.assertEqual(error.exception.code, 'multiline_string')
        self.lexical['string']['escape'] = 'xx'
        self.assertEqual(self.parse('v = "xxxx"').items[0].value.text, 'xxxx')
        self.assertEqual(self.parse('v = "xx"tail"').items[0].value.text, 'xx"tail')

    def test_unknown_fields_versions_duplicates_and_empty_markers_fail(self):
        changes = [('unknown', True), ('format_version', 2), ('line_comment', ''),
                   ('operators', ['=', '=']), ('whitespace', [' ', ' '])]
        for key, value in changes:
            with self.subTest(key=key):
                lexical = {**self.lexical, key: value}
                with self.assertRaises(BuildError):
                    make_syntax(lexical, self.constructs, syntax().logical_operators)
        for key, value in [('bare_values', 'yes'), ('unknown', {}), ('tagged_blocks', ['rgb', 'rgb'])]:
            with self.subTest(key=key), self.assertRaises(BuildError):
                make_syntax(self.lexical, {**self.constructs, key: value}, syntax().logical_operators)

    def test_conflicting_markers_are_rejected_not_order_dependent(self):
        for marker in ('=', '==', '{', '[[', '@['):
            with self.subTest(marker=marker), self.assertRaises(BuildError) as error:
                make_syntax({**self.lexical, 'line_comment': marker}, self.constructs, syntax().logical_operators)
            self.assertEqual(error.exception.code, 'syntax_configuration')
        with self.assertRaises(BuildError):
            make_syntax(self.lexical, {**self.constructs, 'formulas':
                                      [{'open': '@[', 'close': ']'}, {'open': '@[', 'close': ')'}]}, syntax().logical_operators)
        for closer in ('#', '"', '$', '@['):
            with self.subTest(closer=closer), self.assertRaises(BuildError):
                make_syntax(self.lexical, {**self.constructs, 'formulas': [{'open': '@[', 'close': closer}]}, syntax().logical_operators)
        with self.assertRaises(BuildError):
            make_syntax({**self.lexical, 'whitespace': [' '], 'line_comment': '\n'}, self.constructs, syntax().logical_operators)
