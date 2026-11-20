"""Extended object identities and optional text fields on complete syntax trees."""

from types import SimpleNamespace
import unittest

from support import PRODUCT_ROOT, syntax
from sttv.common.datasets import definition
from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.enrichment.localization.selection import select_targets
from stellaris_parser.script.parser import parse_text
from stellaris_parser.script.serialization import serialize_document


class ExtendedTargetTests(unittest.TestCase):
    def targets(self, kind, text):
        options = read_json(PRODUCT_ROOT / f'config/enrichment/targets/{kind}.json')
        options['kind'] = kind
        directory = definition(kind)['directory']
        db = {'documents': [serialize_document(parse_text(text, syntax(), directory + '/test.txt'))]}
        counts = {'objects': 0, 'targets': 0}
        result = select_targets(db, SimpleNamespace(options=options, selection_directory=directory), counts)
        return result, counts

    def test_name_prefixes_description_suffixes_and_explicit_keys(self):
        cases = [
            ('megastructures', 'ring = {}', {'name': 'ring', 'description': 'ring_DESC'}),
            ('pop_jobs', 'miner = {}', {'name': 'job_miner', 'description': 'job_miner_desc'}),
            ('starbase_modules', 'bay = {}', {'name': 'sm_bay', 'description': 'sm_bay_desc'}),
            ('starbase_buildings', 'bay = {}', {'name': 'sm_bay', 'description': 'sm_bay_desc'}),
            ('starbase_levels', 'level = {ship_size = station}', {'name': 'station'}),
            ('ship_sizes', 'ship = {}', {'name': 'ship'}),
            ('economic_categories', 'ships = {}', {'name': 'ships'}),
            ('deposits', 'd = {}', {'name': 'd', 'description': 'd_desc'}),
        ]
        for kind, script, fields in cases:
            with self.subTest(kind=kind):
                targets, counts = self.targets(kind, script)
                self.assertEqual(targets[0].field_keys, fields)
                self.assertEqual(counts, {'objects': 1, 'targets': 1})

    def test_repeated_transition_pairs_and_handler_fragments_keep_distinct_addresses(self):
        targets, counts = self.targets('terraform', 'terraform_link={from=a to=b} terraform_link={from=a to=b}')
        self.assertEqual(counts, {'objects': 2, 'targets': 4})
        self.assertEqual(len({target.path for target in targets}), 4)
        self.assertEqual(targets[0].field_keys, {'name': 'a', 'description': 'a_desc'})
        targets, counts = self.targets('on_actions', 'on_day={events={event.1}} on_day={events={event.2}}')
        self.assertEqual(targets, [])
        self.assertEqual(counts['objects'], 2)

    def test_events_keep_all_description_variants_but_not_trigger_texts(self):
        targets, counts = self.targets('events', '''namespace=test
country_event={id=test.1 title=heading desc={trigger={text=ignore} text=first}
 desc={random_valid={text=second text=third}}}
country_event={id=test.2 hide_window=yes}
country_event={id=test.3 desc=last}''')
        self.assertEqual(counts, {'objects': 3, 'targets': 5})
        self.assertEqual([t.field_keys for t in targets], [
            {'description': 'first'}, {'description': 'second'}, {'description': 'third'},
            {'name': 'heading'}, {'description': 'last'}])

    def test_duplicate_real_ids_fail_but_type_repetition_is_valid(self):
        for kind, script in [('events', 'country_event={id=x} country_event={id=x}'),
                             ('deposits', 'a={} a={}')]:
            with self.subTest(kind=kind), self.assertRaises(BuildError) as caught:
                self.targets(kind, script)
            self.assertEqual(caught.exception.code, 'duplicate_object')

    def test_actions_with_no_title_or_only_tooltip_are_valid(self):
        targets, counts = self.targets('scripted_actions', 'silent={} shown={tooltip=hint activity_key=progress}')
        self.assertEqual(counts, {'objects': 2, 'targets': 2})
        self.assertEqual([t.field_keys for t in targets], [{'description': 'hint'}, {'name': 'progress'}])
