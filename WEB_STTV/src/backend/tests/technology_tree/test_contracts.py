"""Streaming boundaries, explicit config contracts and revision semantics."""

from copy import deepcopy
import io
import json
import unittest

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.paths import PRODUCT_ROOT
from sttv.storage.stream import Stream
from sttv.enrichment.technology_tree.settings import resolve_rules
from sttv.storage.identity import source_hash
from sttv.storage.writing import prepare
from .support import SetFixture, assignment


class StreamTests(unittest.TestCase):
    def test_strings_delimiters_unicode_and_escape_boundaries(self):
        values=[{'text':'a\\"{}[] \\ end', 'unicode':'\u0420\u0443\u0441\u0441\u043a\u0438\u0439'},
                ['\\\\','\\"','\n',True,False,None,12.5,-10], [], {}, 'string', '"']
        for size in (1,2,3,7,64,100000):
            for value in values:
                raw=json.dumps(value,ensure_ascii=False)
                with self.subTest(size=size,value=value):
                    stream=Stream(io.StringIO(raw),size)
                    self.assertEqual(stream.value(),value)
                    self.assertEqual(stream.peek(),'')
                    stream=Stream(io.StringIO(raw+', 42'),size)
                    stream.raw(retain=False)
                    stream.take(',')
                    self.assertEqual(stream.value(),42)

    def test_malformed_duplicate_and_nonfinite_json_fail(self):
        for raw in ('{"x":', '["a', '{"x":1,"x":2}', '{"x":NaN}'):
            with self.subTest(raw=raw),self.assertRaises(BuildError):
                Stream(io.StringIO(raw),2).value()

    def test_rule_contracts_include_disabled_entries_and_references(self):
        config=read_json(PRODUCT_ROOT/'config/enrichment/technology_tree/rules.json')
        good=deepcopy(config)
        good['definitions']={'empty':{}}
        good['rules'][0]['parameters']={'definition_ref':'empty'}
        self.assertEqual(resolve_rules(good)['rules'][0]['parameters'],{})
        for change in ('unknown','duplicate','parameters','reference'):
            bad=deepcopy(config)
            bad['rules'][0]['enabled']=False
            if change=='unknown': bad['rules'][0]['id']='arbitrary'
            if change=='duplicate': bad['rules'].append(deepcopy(bad['rules'][0]))
            if change=='parameters': bad['rules'][0]['parameters']={'expression':'exec()'}
            if change=='reference': bad['rules'][0]['parameters']={'definition_ref':'absent'}
            with self.subTest(change=change),self.assertRaises(BuildError): resolve_rules(bad)


class RevisionTests(SetFixture):
    def test_source_identity_ignores_only_service_enrichment(self):
        document = prepare(self.db['documents'][0], 'technologies')
        baseline = source_hash(document)
        node = document['items'][0]
        node['enrichments'] = {'technology_tree': {'sample': {}}}
        before = deepcopy(document)
        self.assertEqual(source_hash(document), baseline)
        self.assertEqual(document, before)
        node['value']['items'].append(assignment('technology_tree', 'game_field'))
        self.assertNotEqual(source_hash(document), baseline)
