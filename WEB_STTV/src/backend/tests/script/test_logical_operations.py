"""Logical recognition depends on structure and the selected configuration."""

from copy import deepcopy
import unittest

from support import syntax
from script.assertions import check_document
from sttv.common.errors import BuildError
from sttv.script.nodes import Assignment, LogicalOperation, Scalar
from sttv.script.parser import parse_text
from sttv.script.serialization import serialize_document
from sttv.script.syntax import make_syntax


class LogicalOperationTests(unittest.TestCase):
    def setUp(self):
        self.logical = deepcopy(syntax().logical_operators)
        self.constructs = deepcopy(syntax().constructs)

    def parse(self, text):
        selected = make_syntax(syntax().lexical, self.constructs, self.logical)
        document = parse_text(text, selected)
        check_document(document, selected)
        return document

    def test_all_names_preserve_spelling_and_coordinates(self):
        for name in ('AND', 'OR', 'NOT', 'NAND', 'NOR'):
            for spelling in (name, name.lower(), name.title()):
                with self.subTest(spelling=spelling):
                    node = self.parse('\n  ' + spelling + ' = {}').items[0]
                    self.assertIsInstance(node, LogicalOperation)
                    self.assertEqual(node.operator, name)
                    self.assertEqual(node.name.raw, spelling)
                    self.assertEqual(node.assignment_operator, '=')
                    self.assertEqual((node.span.line, node.span.column), (2, 3))

    def test_lists_mixed_repeated_empty_and_multi_child_not(self):
        doc = self.parse('AND = { tech_a OR = { tech_b tech_c } NOT = { x = y x = z } NOR = {} }')
        body = doc.items[0].body.items
        self.assertIsInstance(body[0], Scalar)
        self.assertEqual([n.text for n in body[1].body.items], ['tech_b', 'tech_c'])
        self.assertEqual([n.key.text for n in body[2].body.items], ['x', 'x'])
        self.assertEqual(body[3].body.items, [])

    def test_nonmatches_remain_assignments(self):
        doc = self.parse('NOT = tech_a "AND" = {} or_flag = {} x = AND AND != {} x = "$AND$"')
        self.assertTrue(all(isinstance(n, Assignment) for n in doc.items))
        self.assertEqual(doc.items[3].value.text, 'AND')

    def test_serialization_preserves_logical_and_original_names(self):
        row = serialize_document(self.parse('aNd = { x = Or "or" = {} NOT = tech_a }'))['items'][0]
        self.assertEqual((row['operator'], row['name']['raw']), ('AND', 'aNd'))
        self.assertEqual(row['body']['items'][0]['value']['text'], 'Or')
        self.assertTrue(row['body']['items'][1]['key']['quoted'])
        self.assertEqual(row['body']['items'][2]['kind'], 'assignment')

    def test_configuration_changes_recognition_without_registry(self):
        self.logical['operators'] = ['XoR']
        doc = self.parse('xor = {} AND = {}')
        self.assertEqual(doc.items[0].operator, 'XoR')
        self.assertIsInstance(doc.items[1], Assignment)
        self.logical['case_sensitive'] = True
        self.assertIsInstance(self.parse('xor = {}').items[0], Assignment)
        self.assertIsInstance(self.parse('XoR = {}').items[0], LogicalOperation)
        self.logical['operators'] = []
        self.assertIsInstance(self.parse('XoR = {}').items[0], Assignment)

    def test_assignment_sign_is_configurable(self):
        self.logical['assignment_operator'] = '!='
        doc = self.parse('AND != {} AND = {}')
        self.assertIsInstance(doc.items[0], LogicalOperation)
        self.assertIsInstance(doc.items[1], Assignment)

    def test_invalid_keywords_and_conflicts_fail(self):
        for names in ([''], ['and', 'AND'], ['A B'], ['A=B'], ['$AND$'],
                      ['A{B'], ['"AND"'], ['INLINE_SCRIPT']):
            with self.subTest(names=names), self.assertRaises(BuildError):
                self.logical['operators'] = names
                self.parse('')
        self.logical = {**syntax().logical_operators, 'assignment_operator': '=>'}
        with self.assertRaises(BuildError):
            self.parse('')

    def test_mixed_container_rule_counts_logical_nodes_as_named(self):
        self.constructs['mixed_blocks'] = False
        self.parse('x = { AND = {} y = 1 }')
        with self.assertRaises(BuildError) as error:
            self.parse('x = { AND = {} bare }')
        self.assertEqual(error.exception.code, 'disabled_form')
