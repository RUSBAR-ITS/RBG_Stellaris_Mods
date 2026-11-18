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
from sttv.database.streaming import write_fragment, merge_fragments, canonical_hash
from sttv.database.validation import database_rules, DatabaseValidator
from sttv.script.serialization import walk_nodes


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
        nodes = {node['kind']: copy.deepcopy(node) for _, node in walk_nodes(db['documents'][0]['items'])}
        base = {key: copy.deepcopy(nodes['scalar'][key]) for key in ('span', 'origin')}
        nodes['script_value'] = dict(base, kind='script_value', scope=None, body=nodes['block'])
        nodes['scripted_trigger_test'] = dict(base, kind='scripted_trigger_test', operator='>',
                                            value=nodes['scalar'], body=nodes['block'])
        self.assertEqual(len(nodes), 9)
        for kind, node in nodes.items():
            candidate = copy.deepcopy(db)
            candidate['documents'][0]['items'] = [node]
            self.agrees(candidate)
            for key in node:
                for replacement in (None, True, 1.5, [], {}, 'invalid'):
                    damaged = copy.deepcopy(candidate)
                    damaged['documents'][0]['items'][0][key] = replacement
                    with self.subTest(kind=kind, field=key, replacement=replacement):
                        self.agrees(damaged)
                damaged = copy.deepcopy(candidate)
                del damaged['documents'][0]['items'][0][key]
                self.agrees(damaged)
            damaged = copy.deepcopy(candidate)
            damaged['documents'][0]['items'][0]['extra'] = 1
            self.agrees(damaged)

    def test_nested_constraints_and_numeric_boolean_distinction(self):
        db, _ = fixture('x=$P|default$')
        for value in (False, 0, 1, 1.0, 1.5, -1, None):
            damaged = copy.deepcopy(db)
            damaged['documents'][0]['items'][0]['span']['line'] = value
            self.agrees(damaged)
        for source in ('../outside.txt', 'C:/outside.txt', '/absolute', 'valid.txt', ''):
            damaged = copy.deepcopy(db)
            damaged['documents'][0]['source']['file'] = source
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
            schema['properties']['documents']['maxItems'] = 1
            updated = prepare()
        container = {'format': 'sttv.parse_database', 'format_version': 6, 'documents': [None, None]}
        original.container(container, '', None)
        with self.assertRaises(BuildError):
            updated.container(container, '', None)

    def test_each_syntax_node_is_visited_once(self):
        db, _ = fixture('box={inline_script=outer}', {'outer.txt': 'x=yes inner={y=no}'})
        document = db['documents'][0]
        self.assertEqual(DatabaseValidator().document(document, 0), sum(1 for _ in walk_nodes(document['items'])))


class StreamingValidationTests(BuildFixture):
    def test_initial_write_failure_cleans_temporary_file(self):
        from sttv.database import streaming
        db, _ = fixture('x=yes')
        fragment = write_fragment(db['documents'][0], self.root / 'fragment.json', 0, performance())
        create = streaming.tempfile.NamedTemporaryFile
        def failing(*args, **kwargs):
            handle = create(*args, **kwargs)
            proxy = Mock(wraps=handle)
            proxy.name = handle.name
            proxy.__enter__ = Mock(return_value=proxy)
            proxy.__exit__ = Mock(side_effect=lambda *args: handle.close())
            proxy.write.side_effect = OSError('Simulated initial write failure')
            return proxy
        with patch.object(streaming.tempfile, 'NamedTemporaryFile', side_effect=failing):
            with self.assertRaises(OSError):
                merge_fragments(self.root / 'written.json', [{'index': 0, 'fragment': fragment}], performance())
        self.assertFalse(list(self.root.glob('written.json.*.tmp')))

    def test_completed_document_is_not_retained(self):
        class Items(list):
            pass
        db, _ = fixture('x=yes')
        document = db['documents'].pop()
        document['items'] = Items(document['items'])
        reference = weakref.ref(document['items'])
        write_fragment(document, self.root / 'fragment.json', 0, performance())
        del document
        self.assertIsNone(reference())

    @schema_operation
    def test_merge_preserves_formatted_bytes_without_reparsing(self):
        db, _ = fixture('x=yes data={name="text"} y={}')
        metrics = performance()
        fragment = write_fragment(db['documents'][0], self.root / 'fragment.json', 0, metrics)
        with patch('sttv.common.json_io.read_json', side_effect=AssertionError('No reread')):
            path, checksum = merge_fragments(self.root / 'written.json',
                [{'index': 0, 'source': 'fixture.txt', 'fragment': fragment}], metrics)
        expected = json.dumps(db, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n'
        self.assertEqual(path.read_bytes(), expected.encode('utf-8'))
        payload = {key: value for key, value in db.items() if key != 'documents'}
        payload.update(identity_algorithm='sttv.document_hashes.v1',
                       documents=[{'index': 0, 'content_hash': canonical_hash(db['documents'][0])}])
        self.assertEqual(checksum, canonical_hash(payload))
        self.assertEqual(metrics['validated_documents'], 1)
        path.unlink()

    def test_corrupt_fragment_and_invalid_document_preserve_destination(self):
        db, _ = fixture('x=yes')
        path = self.root / 'published.json'
        path.write_text('previous', encoding='utf-8')
        fragment = write_fragment(db['documents'][0], self.root / 'fragment.json', 0, performance())
        Path(fragment['path']).write_text('{}', encoding='utf-8')
        with self.assertRaisesRegex(BuildError, 'Damaged fragment'):
            merge_fragments(path, [{'index': 0, 'source': 'fixture.txt', 'fragment': fragment}], performance())
        damaged = copy.deepcopy(db['documents'][0])
        damaged['items'][0]['kind'] = 'unknown'
        with self.assertRaises(BuildError):
            write_fragment(damaged, self.root / 'invalid.json', 1, performance())
        self.assertEqual(path.read_text(encoding='utf-8'), 'previous')
        self.assertFalse(list(self.root.glob('published.json.*.tmp')))
