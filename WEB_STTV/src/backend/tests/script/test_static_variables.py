"""Static scopes, literal fidelity, reference limits and syntax boundaries."""
from stellaris_parser.schema import CONFIG


from copy import deepcopy
import unittest

from support import PRODUCT_ROOT, syntax
from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.report import Report
from stellaris_parser.script.parser import parse_text
from stellaris_parser.script.variables.rules import Rules
from stellaris_parser.script.variables.table import Table
from stellaris_parser.script.variables.processor import Processor
from script.corpus_statistics import Statistics


class StaticVariableTests(unittest.TestCase):
    def setUp(self):
        self.options = read_json(CONFIG / 'static_variables.json')

    def process(self, text, shared='', **changes):
        self.rules = Rules(dict(self.options, **changes), syntax())
        table = Table(self.rules)
        for node in parse_text(shared, syntax(), 'globals.txt').items:
            table.add(node)
        self.counts = Report().data['counts']['static_variables']
        document = parse_text(text, syntax(), 'local.txt')
        self.before = deepcopy(document)
        return Processor(self.rules, table.resolve_all(), self.counts).apply(document)

    def test_local_overrides_do_not_capture_shared_alias_dependencies(self):
        doc = self.process('@base=20 @copy=@base x=@alias y=@copy', '@base=5 @alias=@base')
        self.assertEqual([n.value.text for n in doc.items], ['20', '@base', '5', '20'])
        self.assertEqual(self.counts['references'], 2)
        self.assertEqual(self.counts['substituted'], 2)
        self.assertEqual(self.counts['local_definitions'], 2)

    def test_forward_chains_keep_use_sites_and_declarations(self):
        doc = self.process('x=@first\n@first=@second\n@second=0.50')
        self.assertEqual(doc.items[0].value.raw, '0.50')
        self.assertEqual(doc.items[0].value.span, self.before.items[0].value.span)
        self.assertEqual(doc.items[0].value.origin, self.before.items[0].value.origin)
        self.assertEqual(doc.items[1:], self.before.items[1:])
        self.assertEqual(doc.metadata, self.before.metadata)

    def test_scalar_literals_and_nonreference_syntax(self):
        doc = self.process('@n=-0.50 @b=yes @id=alpha @s="@literal" '
                           'x={ @n @b @id @s "@missing" prefix_@n flag@root @name_$P$ } '
                           'formula=@[ n * 2 ] "@field"=unchanged')
        values = doc.items[4].value.items
        self.assertEqual([v.text for v in values],
                         ['-0.50', 'yes', 'alpha', '@literal', '@missing', 'prefix_@n', 'flag@root', '@name_$P$'])
        self.assertTrue(values[3].quoted)
        self.assertEqual(values[3].raw, '"@literal"')
        self.assertEqual(doc.items[5:], self.before.items[5:])
        self.assertEqual(self.counts['substituted'], 4)

    def test_case_modes_and_original_spelling(self):
        doc = self.process('@Name=1 @name=2 x=@Name y=@name')
        self.assertEqual([n.value.text for n in doc.items[-2:]], ['1', '2'])
        doc = self.process('@Name=1 x=@NAME', case_sensitive=False)
        self.assertEqual(doc.items[0].key.text, '@Name')
        self.assertEqual(doc.items[1].value.text, '1')
        with self.assertRaises(BuildError) as raised:
            self.process('@Name=1 @name=2', case_sensitive=False)
        self.assertEqual(raised.exception.code, 'duplicate_static_variable')

    def test_errors_include_location_and_resolution_chain(self):
        cases = [('@a=@b @b=@missing', 'unknown_static_variable'),
                 ('@a=@a', 'static_variable_cycle'), ('@a=@b @b=@a', 'static_variable_cycle'),
                 ('@a=1 @a=1', 'duplicate_static_variable'),
                 ('@a=@[ 1 + 2 ]', 'unsupported_static_declaration'),
                 ('@a={1}', 'unsupported_static_declaration'),
                 ('@a=$P$', 'unsupported_static_declaration'),
                 ('@a_$P$=1', 'invalid_static_declaration'),
                 ('@a>1', 'invalid_static_declaration'),
                 ('box={ @a=1 }', 'nested_static_declaration'),
                 ('x=@missing', 'unknown_static_variable')]
        for text, code in cases:
            with self.subTest(text=text), self.assertRaises(BuildError) as raised:
                self.process(text)
            self.assertEqual(raised.exception.code, code)
            self.assertEqual(raised.exception.provenance['file'], 'local.txt')
        with self.assertRaisesRegex(BuildError, '@a -> @b -> @missing'):
            self.process('@a=@b @b=@missing')

    def test_reference_depth_includes_shared_chain_and_is_order_independent(self):
        self.process('@a=@b @b=1 x=@a', max_reference_depth=1)
        for text, shared in [('@a=@b @b=@c @c=1', ''),
                             ('@c=1 @b=@c @a=@b', ''), ('@a=@b', '@b=@c @c=1')]:
            with self.subTest(text=text), self.assertRaises(BuildError) as raised:
                self.process(text, shared, max_reference_depth=1)
            self.assertEqual(raised.exception.code, 'static_variable_depth')
        doc = self.process('@a=@b x=@a', '@b=@c @c=1', max_reference_depth=2)
        self.assertEqual(doc.items[-1].value.text, '1')

    def test_configurable_prefix_and_invalid_configuration(self):
        self.assertEqual(self.process('%v=7 x=%v', prefix='%').items[1].value.text, '7')
        for change in ({'name_pattern': '['}, {'name_pattern': '.*'}, {'prefix': '$'},
                       {'prefix': '@['}, {'prefix': ''}, {'max_reference_depth': 0}):
            with self.subTest(change=change), self.assertRaises(BuildError):
                self.process('', **change)

    def test_statistics_ignore_declarations_and_use_resolved_values(self):
        doc = self.process('@a=distinct @unused=ignored x=@a y=@a')
        statistics = Statistics(self.rules)
        statistics.consume(doc)
        self.assertEqual(statistics.rows['distinct']['count'], 2)
        self.assertNotIn('ignored', statistics.rows)
        self.assertNotIn('@a', statistics.rows)
        self.assertEqual(statistics.excluded['static_declarations'], 2)
