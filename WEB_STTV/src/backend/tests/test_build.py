"""End-to-end construction, source priorities, and transactional failures."""

import json
from unittest.mock import patch

from support import BuildFixture
from sttv.validation import validate_database


class BuildTests(BuildFixture):
    def test_complete_database_and_repeatability(self):
        before = self.hashes()
        result = self.run_build()
        self.assertEqual(result["status"], "success", result)
        database = self.database()
        a = database["technologies"]["tech_a"]
        b = database["technologies"]["tech_b"]
        self.assertEqual(a["fields"]["cost"], {"variable": "@alias", "resolved": 10})
        self.assertEqual(a["name"]["ru"], "\u0418\u043c\u044f A")
        self.assertEqual(a["name_sources"]["ru"]["tier"], "RU_LOC_TIER_1")
        self.assertEqual(a["fields"]["technology_swap"][0]["name"]["ru"], "")
        self.assertEqual(b["name_sources"]["ru"]["tier"], "RU_LOC_TIER_3")
        self.assertEqual(b["fields"]["prerequisites"], {"all": [{"any": [{"tech": "tech_a"}]}]})
        self.assertEqual(b["fields"]["weight"]["occurrences"][1]["value"]["resolved"], None)
        self.assertNotIn("parent_id", a["fields"]["technology_swap"][0])
        content = self.database_path().read_bytes()
        self.assertEqual(self.run_build()["status"], "success")
        self.assertEqual(content, self.database_path().read_bytes())
        self.assertEqual(before, self.hashes())
        self.assertFalse(list(self.database_path().parent.rglob("*.txt")))
        self.assertFalse(list(self.database_path().parent.rglob("*.yml")))
        self.assertFalse(list(self.database_path().parent.rglob("*.tmp")))

    def test_missing_and_empty_names_remain_distinct(self):
        self.write_locale("ru3", 'tech_b_desc:0 "Ignored description"')
        result = self.run_build()
        self.assertEqual(result["status"], "success")
        record = self.database()["technologies"]["tech_b"]
        self.assertIsNone(record["name"]["ru"])
        self.assertIsNone(record["name_sources"]["ru"])
        self.assertTrue(any(row["code"] == "missing_translation" for row in result["diagnostics"]))

    def test_conflicting_localization_preserves_previous_database(self):
        self.assertEqual(self.run_build()["status"], "success")
        before = self.database_path().read_bytes()
        self.write_locale("ru1", 'tech_a:0 "Conflict"', "duplicate.yml")
        result = self.run_build()
        self.assertIn("localization_conflict", self.errors(result))
        self.assertEqual(before, self.database_path().read_bytes())
        self.assertFalse(result["database_written"])

    def test_identical_duplicate_uses_first_source_position(self):
        self.write_locale("en1", 'tech_a:0 "Name A"', "aaa.yml")
        self.assertEqual(self.run_build()["status"], "success")
        self.assertEqual(self.database()["technologies"]["tech_a"]["name_sources"]["en"]["file"],
                         "aaa.yml")

    def test_source_priority_change_and_removed_records(self):
        self.assertEqual(self.run_build()["status"], "success")
        self.options["localization"]["languages"]["ru"]["sources"] = [
            "RU_LOC_TIER_2", "RU_LOC_TIER_1", "RU_LOC_TIER_3"]
        self.assertEqual(self.run_build()["status"], "success")
        self.assertEqual(self.database()["technologies"]["tech_a"]["name"]["ru"], "Lower priority")
        self.write_script("base.txt", "tech_a = { area = physics }")
        self.assertEqual(self.run_build()["status"], "success")
        self.assertEqual(list(self.database()["technologies"]), ["tech_a"])

    def test_unknown_fields_and_scripts_fail_without_publishing(self):
        for definition in ("tech_a = { unknown = 1 }",
                           "tech_a = { potential = { unknown = yes } }",
                           "tech_a = { potential = { is_ai = 2 } }",
                           "tech_a = { technology_swap = { trigger = {} } }"):
            self.write_script("base.txt", definition)
            result = self.run_build()
            self.assertEqual(result["status"], "failed", definition)
            self.assertFalse(self.database_path().exists())

    def test_serialization_failure_keeps_existing_database(self):
        self.assertEqual(self.run_build()["status"], "success")
        before = self.database_path().read_bytes()
        with patch("sttv.storage.os.replace", side_effect=OSError("Simulated write failure")):
            result = self.run_build()
        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["database_written"])
        self.assertEqual(before, self.database_path().read_bytes())
        self.assertFalse(list(self.database_path().parent.rglob("*.tmp")))

    def test_database_validation_does_not_read_sources(self):
        self.assertEqual(self.run_build()["status"], "success")
        database = self.database()
        with patch("sttv.sources.read_source", side_effect=AssertionError("No source reads")):
            validate_database(database)
        json.dumps(database, allow_nan=False)
