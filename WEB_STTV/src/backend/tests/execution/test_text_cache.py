"""Cached localization preserves per-job sources and reference diagnostics."""

import unittest
from unittest.mock import patch

from stellaris_parser.localization.index import LocalizationIndex
from sttv.enrichment.localization.references import Resolver
from sttv.parallel.text_cache import CachedResolver


class TextCacheTests(unittest.TestCase):
    def setUp(self):
        self.index = LocalizationIndex.__new__(LocalizationIndex)
        entry = lambda text, line: {'raw': text, 'source': {'tier': 'one', 'file': 'a.yml', 'line': line}}
        self.index.tables = {'en': [{'a': [entry('$b$ $absent$ [Root.GetName]', 1)],
                                    'b': [entry('Resolved', 2)], 'other': [entry('Other', 3)]}]}
        self.index.selected = {}
        self.options = {'delimiter': '$', 'key_pattern': '[A-Za-z_]+', 'max_depth': 10, 'max_characters': 1000}

    def test_cached_result_replays_exact_sources_without_reusing_job_selection(self):
        cache = {}
        resolver = CachedResolver(self.index, self.options, cache)
        expected = Resolver(self.index, self.options).resolve('en', 'a')
        self.index.selected.clear()
        self.assertEqual(expected, resolver.resolve('en', 'a'))
        self.index.selected.clear()
        with patch.object(Resolver, 'resolve', side_effect=AssertionError('Already resolved')):
            self.assertEqual(expected, resolver.resolve('en', 'a'))
        self.assertEqual(set(self.index.selected), {('en', 'a'), ('en', 'b')})
        self.index.selected.clear()
        resolver.resolve('en', 'other')
        self.assertEqual(set(self.index.selected), {('en', 'other')})
        self.assertEqual(expected['unresolved_chains'], [('a', 'absent')])

    def test_missing_keys_are_cached_without_sources(self):
        resolver = CachedResolver(self.index, self.options, {})
        self.assertIsNone(resolver.resolve('en', 'missing'))
        with patch.object(Resolver, 'resolve', side_effect=AssertionError('Already resolved')):
            self.assertIsNone(resolver.resolve('en', 'missing'))
        self.assertEqual(self.index.selected, {})
