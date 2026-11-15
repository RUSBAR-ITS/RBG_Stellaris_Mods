"""Default and conditional text processing independently of game commands."""

from support import PRODUCT_ROOT, syntax, syntax_payload
from sttv.common.json_io import read_json
from sttv.script.inline import Expansion, MemoryTemplates
from sttv.script.parser import parse_text
import unittest


class ParameterFragmentTests(unittest.TestCase):
    def expand(self, payload, template):
        options = read_json(PRODUCT_ROOT / 'config/parser/inline_scripts.json')
        context = Expansion(MemoryTemplates({'p.txt': template}, options), options)
        self.context = context
        return parse_text('inline_script=' + payload, syntax(), 'caller.txt', expansion=context)

    def test_nested_conditions_defaults_and_empty_arguments(self):
        doc = self.expand('{script=p OUTER=yes INNER=no EMPTY=""}',
                          '[[OUTER] [[INNER] missing=$UNPASSED$] [[!INNER] value="$EMPTY|fallback$"]] '
                          '[[ABSENT] inline_script=missing] default=$ABSENT|7$ [[!ABSENT] other=yes]')
        self.assertEqual([n.value.text for n in doc.items], ['', '7', 'yes'])
        self.assertEqual(self.context.parameter_counts['defaults'], 1)

    def test_default_does_not_create_binding_and_is_not_an_alias(self):
        doc = self.expand('{script=p OTHER=5}', 'x=$MISSING|OTHER$ [[MISSING] bad=yes] [[!MISSING] good=yes]')
        self.assertEqual([n.value.text for n in doc.items], ['OTHER', 'yes'])

    def test_comments_and_conditional_looking_strings_are_preserved(self):
        doc = self.expand('p', '# [[UNSET] $MISSING$\n text="[[LITERAL] body ]" x="$EMPTY|$"')
        self.assertEqual(doc.items[0].value.text, '[[LITERAL] body ]')
        self.assertEqual(doc.items[1].value.text, '')

    def test_statistics_ignore_new_history_and_count_test_body_and_value(self):
        from script.corpus_statistics import Statistics
        from sttv.script.nodes import Block, ScriptedTriggerTest
        doc = parse_text('count=2', syntax(), 'source.txt')
        item = doc.items[0]
        doc.items[:] = [ScriptedTriggerTest('>', item.value, Block([item], item.span, origin=item.origin),
                                            item.span, origin=item.origin)]
        first = Statistics()
        first.consume(doc)
        doc.metadata['expansions'].append({'ignored': 'extra'})
        second = Statistics()
        second.consume(doc)
        self.assertEqual(first.rows, second.rows)
        self.assertEqual(first.rows['2']['count'], 2)
