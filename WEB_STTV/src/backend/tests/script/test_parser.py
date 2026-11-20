"""Parser behavior at syntax boundaries and in nested script contexts."""

import unittest

import support
from sttv.common.errors import BuildError
from stellaris_parser.script.parser import parse_text as parse_document


def parse_text(text):
    return parse_document(text, support.syntax()).items


class ParserTests(unittest.TestCase):
    def test_quotes_comments_operators_and_repetitions(self):
        nodes = parse_text('# ignored\ntech = { key = "a # b \\"c\\"" n >= 2 n = 3 }')
        self.assertEqual(nodes[0].span.line, 2)
        values = nodes[0].value.items
        self.assertEqual(values[0].value.text, 'a # b \\"c\\"')
        self.assertEqual([entry.operator for entry in values[1:]], [">=", "="])
        self.assertEqual(len(values), 3)

    def test_bare_lists_and_empty_values(self):
        nodes = parse_text('a = { first "second word" } b = "" c = {}')
        self.assertEqual([item.text for item in nodes[0].value.items], ["first", "second word"])
        self.assertEqual(nodes[1].value.text, "")
        self.assertEqual(nodes[2].value.items, [])

    def test_rejects_incomplete_or_malformed_syntax(self):
        for text in ('a = {', 'a =', 'a = }', '}', 'a = "open', 'a = "x\\"',
                     'a = "x\\', '= 1'):
            with self.subTest(text=text), self.assertRaises(BuildError):
                parse_text(text)

    def test_game_names_do_not_constrain_syntax(self):
        for text in ('unknown = yes', 'is_ai = 1', 'has_technology > tech_a',
                     'any_owned_planet = yes', 'factor = 1'):
            with self.subTest(text=text):
                self.assertEqual(len(parse_text(text)), 1)

    def test_inline_calls_require_expansion_context(self):
        for text in ('inline_script = unknown/path',
                     'inline_script = { script = ai/weapon_preference_weight EXTRA = x }'):
            with self.subTest(text=text), self.assertRaises(BuildError) as error:
                parse_text(text)
            self.assertEqual(error.exception.code, 'inline_context_required')
