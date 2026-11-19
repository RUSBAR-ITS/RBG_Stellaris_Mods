"""Object addressing, description inheritance, and unchanged tree semantics."""

import copy
from collections import Counter

from sttv.common.errors import BuildError
from sttv.common.json_io import json_text, read_json
from sttv.database.storage import read_database
from sttv.database.validation import validate_database
from sttv.enrichment.localization.attachment import remove_previous
from sttv.script.serialization import walk_nodes
from .support import LocalizationFixture


class ObjectTests(LocalizationFixture):
    def test_inheritance_and_no_game_directory_required(self):
        self.assertFalse((self.root / "absent_game").exists())
        report = self.run_operation()
        self.assert_success(report)
        value = self.localized(variant=True, field="description")
        self.assertEqual(value["requested_key"], "variant_a_desc")
        self.assertEqual(value["key"], "tech_a_desc")
        self.assertEqual(value["inherited_from"], {"database": "technologies", "document_id": self.read_db()["documents"][0]["document_id"], "pointer": "/items/0"})
        self.assertEqual(report["counts"]["technologies"], 2)
        self.assertEqual(report["counts"]["variants"], 1)
        self.assertNotIn("enrichments", self.read_db()["documents"][1]["items"][0])

    def test_own_description_at_low_tier_beats_parent_at_high_tier(self):
        self.write_localization("RU_LOC_TIER_1", {"tech_a_desc": "High parent"})
        self.write_localization("RU_LOC_TIER_3", {"variant_a_desc": "Low own"})
        self.assert_success(self.run_operation())
        self.assertEqual(self.localized(variant=True, field="description")["text"], "Low own")
        self.assertIsNone(self.localized(variant=True, field="description")["inherited_from"])
        self.assertIsNotNone(self.localized("en", True, "description")["inherited_from"])

    def test_empty_own_description_and_missing_parent(self):
        self.write_localization("RU_LOC_TIER_1", {"variant_a_desc": ""})
        self.write_localization("EN_LOC_TIER_1", {"variant_a": "Variant"})
        self.assert_success(self.run_operation())
        self.assertEqual(self.localized(variant=True, field="description")["text"], "")
        self.assertIsNone(self.localized(variant=True, field="description")["inherited_from"])
        self.assertIsNone(self.localized("en", True, "description")["key"])
        self.assertIsNone(self.localized("en", True, "description")["inherited_from"])

    def test_repeated_variants_are_distinct_and_nested_names_are_ignored(self):
        self.documents[0] = (self.documents[0][0],
            'tech_a = { technology_swap = { name = variant_a trigger = { name = ignored } } '
            'technology_swap = { name = variant_a } prereqfor_desc = { desc = wrong } }')
        self.write_database()
        report = self.run_operation()
        self.assert_success(report)
        self.assertEqual(report["counts"]["variants"], 2)
        children = self.read_db()["documents"][0]["items"][0]["value"]["items"]
        self.assertEqual(children[0]["enrichments"], children[1]["enrichments"])
        self.assertNotIn("enrichments", children[2])

    def test_bad_variant_names_fail(self):
        for text in ('', 'name = x name = y', 'name = {}', 'name = ""'):
            with self.subTest(text=text):
                self.documents[0] = (self.documents[0][0], 'tech_a = { technology_swap = { ' + text + ' } }')
                self.write_database()
                self.assert_failure("invalid_target")

    def test_refresh_removes_stale_results_and_zero_targets_are_valid(self):
        self.documents.insert(1, ("common/technology/other.txt", 'other = {}'))
        self.write_database()
        self.assert_success(self.run_operation())
        self.target_options["selection"]["pattern"] = "base.txt"
        self.assert_success(self.run_operation())
        self.assertNotIn("enrichments", self.read_db()["documents"][1]["items"][0])
        self.target_options["selection"]["pattern"] = "missing.txt"
        self.assert_success(self.run_operation())
        self.assertEqual(self.read_db(), self.original)

    def test_original_fields_history_and_frequency_are_unchanged(self):
        def frequencies(db):
            return Counter(node["text"] for doc in db["documents"] for _, node in walk_nodes(doc["items"])
                           if node["kind"] == "scalar")
        self.assert_success(self.run_operation())
        enriched = self.read_db()
        self.assertEqual(frequencies(enriched), frequencies(self.original))
        remove_previous(enriched)
        self.assertEqual(enriched, self.original)
        first = self.database_path.read_bytes()
        self.assert_success(self.run_operation())
        self.assertEqual(first, self.database_path.read_bytes())

    def test_inheritance_corruption_and_old_formats_are_rejected(self):
        self.assert_success(self.run_operation())
        db = self.read_db()
        value = db["documents"][0]["items"][0]["value"]["items"][0]["enrichments"]["localization"]["ru"]["description"]
        value["text"] = "Corrupted"
        with self.assertRaises(BuildError):
            validate_database(db["documents"][0])
        db = copy.deepcopy(self.original)
        db["format_version"] = 3
        self.database_path.write_text(json_text(db), encoding="utf-8")
        self.assert_failure("schema_error")
