"""Parser behavior at syntax boundaries and in nested script contexts."""

import unittest

import support
from sttv.common.errors import BuildError
from support import parse_entries as parse_text
from sttv.script.serialization import script_block
from sttv.script.rules import ScriptRules


class ParserTests(unittest.TestCase):
    def test_quotes_comments_operators_and_repetitions(self):
        nodes = parse_text('# ignored\ntech = { key = "a # b \\"c\\"" n >= 2 n = 3 }')
        self.assertEqual(nodes[0].line, 2)
        values = nodes[0].value
        self.assertEqual(values[0].value, 'a # b \\"c\\"')
        self.assertEqual([entry.operator for entry in values[1:]], [">=", "="])
        self.assertEqual(len(values), 3)

    def test_bare_lists_and_empty_values(self):
        nodes = parse_text('a = { first "second word" } b = "" c = {}')
        self.assertEqual([item.value for item in nodes[0].value], ["first", "second word"])
        self.assertIsNone(nodes[0].value[0].key)
        self.assertEqual(nodes[1].value, "")
        self.assertEqual(nodes[2].value, [])

    def test_rejects_incomplete_or_malformed_syntax(self):
        for text in ('a = {', 'a =', 'a = }', '}', 'a = "open', 'a = "x\\"',
                     'a = "x\\', '= 1'):
            with self.subTest(text=text), self.assertRaises(BuildError):
                parse_text(text)

    def test_unknown_command_and_wrong_arguments(self):
        for text in ('unknown = yes', 'is_ai = 1', 'has_technology > tech_a',
                     'any_owned_planet = yes', 'factor = 1'):
            with self.subTest(text=text), self.assertRaises(BuildError):
                ScriptRules(support.registry()).validate(script_block(parse_text(text)), "condition")

    def test_scope_changes_are_validated(self):
        valid = 'any_owned_planet = { has_deposit = d_test }'
        ScriptRules(support.registry()).validate(script_block(parse_text(valid)), "condition")
        invalid = 'any_owned_planet = { has_valid_civic = civic_test }'
        with self.assertRaises(BuildError) as error:
            ScriptRules(support.registry()).validate(script_block(parse_text(invalid)), "condition")
        self.assertEqual(error.exception.code, "invalid_scope")

    def test_inline_calls_require_expansion_context(self):
        for text in ('inline_script = unknown/path',
                     'inline_script = { script = ai/weapon_preference_weight EXTRA = x }'):
            with self.subTest(text=text), self.assertRaises(BuildError) as error:
                parse_text(text)
            self.assertEqual(error.exception.code, 'inline_context_required')
