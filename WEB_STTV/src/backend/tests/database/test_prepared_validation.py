"""Differential validation, rule lifecycle and streaming persistence tests."""

import copy
import hashlib
import json
import unittest
import weakref
from pathlib import Path
from unittest.mock import Mock, patch

from support import BuildFixture
from database.test_validation import fixture
from sttv.common.errors import BuildError
from sttv.common.schema import schema_operation, schema_validator
from sttv.common.timing import performance
from sttv.database.checks.compiler import Compiler
from sttv.storage.writing import write_document
from sttv.database.validation import database_rules, DatabaseValidator
from stellaris_parser.script.serialization import walk_nodes


class PreparedValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = schema_validator('database.schema.json')
        cls.compiled = Compiler(cls.oracle.schema)

    def agrees(self, value):
        expected = self.oracle.is_valid(value)
        try:
            self.compiled.check(value)
            actual = True
        except BuildError:
            actual = False
        self.assertEqual(actual, expected, repr(value)[:200])

    def test_all_nine_kinds_and_corrupted_fields_match_schema(self):
        db, _ = fixture('bare x=1 f=@[1+2] c=rgb {1 2 3} [[P] AND={a=yes}]')
        nodes = {node['kind']: copy.deepcopy(node) for _, node in walk_nodes(db['items'])}
        base = {key: copy.deepcopy(nodes['scalar'][key]) for key in ('span', 'origin')}
        nodes['script_value'] = dict(base, kind='script_value', scope=None, body=nodes['block'])
        nodes['scripted_trigger_test'] = dict(base, kind='scripted_trigger_test', operator='>',
                                            value=nodes['scalar'], body=nodes['block'])
        self.assertEqual(len(nodes), 9)
        for kind, node in nodes.items():
            candidate = copy.deepcopy(db)
            candidate['items'] = [node]
            self.agrees(candidate)
            for key in node:
                for replacement in (None, True, 1.5, [], {}, 'invalid'):
                    damaged = copy.deepcopy(candidate)
                    damaged['items'][0][key] = replacement
                    with self.subTest(kind=kind, field=key, replacement=replacement):
                        self.agrees(damaged)
                damaged = copy.deepcopy(candidate)
                del damaged['items'][0][key]
                self.agrees(damaged)
            damaged = copy.deepcopy(candidate)
            damaged['items'][0]['extra'] = 1
            self.agrees(damaged)

    def test_nested_constraints_and_numeric_boolean_distinction(self):
        db, _ = fixture('x=$P|default$')
        for value in (False, 0, 1, 1.0, 1.5, -1, None):
            damaged = copy.deepcopy(db)
            damaged['items'][0]['span']['line'] = value
            self.agrees(damaged)
        for source in ('../outside.txt', 'C:/outside.txt', '/absolute', 'valid.txt', ''):
            damaged = copy.deepcopy(db)
            damaged['source']['file'] = source
            self.agrees(damaged)
        for values in ([1, True], [1, 1.0], [{'a': True}, {'a': 1}], ['a', 'a']):
            schema = {'type': 'array', 'uniqueItems': True}
            compiled = Compiler(schema)
            expected = self.oracle.evolve(schema=schema).is_valid(values)
            try:
                compiled.check(values)
                self.assertTrue(expected)
            except BuildError:
                self.assertFalse(expected)

    def test_schema_sessions_refresh_and_unknown_constraints_fail(self):
        @schema_operation
        def operation():
            first = database_rules()
            self.assertIs(first, database_rules())
            return first
        self.assertIsNot(operation(), operation())
        schema = copy.deepcopy(self.oracle.schema)
        schema['$defs']['scalar']['properties']['text']['unsupported'] = True
        with self.assertRaises(BuildError) as failure:
            Compiler(schema)
        self.assertEqual(failure.exception.code, 'unsupported_schema')

    def test_next_operation_observes_changed_container_constraints(self):
        schema = copy.deepcopy(self.oracle.schema)
        @schema_operation
        def prepare():
            return database_rules()
        with patch('sttv.common.schema.read_json', side_effect=lambda path: copy.deepcopy(schema)):
            original = prepare()
            schema['properties']['format_version']['const'] = 2
            updated = prepare()
        document, _ = fixture('x=yes')
        header = {k: v for k, v in document.items() if k not in ('source', 'items', 'metadata')}
        original.container(header, '', None)
        with self.assertRaises(BuildError):
            updated.container(header, '', None)

    def test_each_syntax_node_is_visited_once(self):
        db, _ = fixture('box={inline_script=outer}', {'outer.txt': 'x=yes inner={y=no}'})
        document = db
        self.assertEqual(DatabaseValidator().document(document, 0), sum(1 for _ in walk_nodes(document['items'])))


