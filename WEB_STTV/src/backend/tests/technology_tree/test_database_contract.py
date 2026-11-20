"""Document-local shape checks and global relationship integrity stay distinct."""

from copy import deepcopy
import unittest

from support import syntax
from sttv.common.errors import BuildError
from sttv.database.validation import validate_database
from stellaris_parser.script.parser import parse_text
from stellaris_parser.script.serialization import serialize_document
from sttv.storage.writing import prepare
from sttv.enrichment.technology_tree.integrity import check_results
from sttv.enrichment.technology_tree.representations import prepare as technologies
from .support import catalog


class DatabaseContractTests(unittest.TestCase):
    def fixture(self):
        document = prepare(serialize_document(parse_text(
            'a={ tier=1 area=physics category={ computing } } '
            'b={ tier=2 area=physics category={ computing } prerequisites={ a } }',
            syntax(), 'common/technology/test.txt')), 'technologies')
        rows = {'a': {'parent_tech': None, 'children': ['b'], 'status': 'root'},
                'b': {'parent_tech': 'a', 'children': [], 'status': 'resolved'}}
        for node in document['items']:
            node['enrichments'] = {'technology_tree': {'reference_default': rows[node['key']['text']]}}
        return document, rows

    def test_local_validation_and_global_reciprocity(self):
        document, rows = self.fixture()
        validate_database(document)
        techs = technologies(catalog(document['items']), {})
        check_results(rows, techs)
        damaged = deepcopy(rows)
        damaged['a']['children'] = []
        with self.assertRaises(BuildError):
            check_results(damaged, techs)

    def test_nested_and_nontechnology_records_are_rejected(self):
        document, _ = self.fixture()
        root = document['items'][0]
        root['value']['items'][0]['enrichments'] = root.pop('enrichments')
        with self.assertRaises(BuildError):
            validate_database(document)
        document, _ = self.fixture()
        document['database'] = 'buildings'
        with self.assertRaises(BuildError):
            validate_database(document)
