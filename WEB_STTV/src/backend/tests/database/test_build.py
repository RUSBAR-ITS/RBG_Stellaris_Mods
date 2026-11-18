"""End-to-end structural builds and independent file publication failures."""

import json
from unittest.mock import patch

from support import BuildFixture
from sttv.database.storage import read_database


class BuildTests(BuildFixture):
    def test_complete_database_repeatability_and_read_only_sources(self):
        before = self.hashes()
        result = self.run_build()
        self.assertEqual(result["status"], "success", result)
        self.assertEqual(result["counts"]["selected_files"], 3)
        self.assertEqual(result["counts"]["parsed_files"], 3)
        self.assertEqual(result["counts"]["warnings"], 0)
        self.assertEqual(len(result["sources"]), 3)
        persisted = json.loads((self.database_path().parent / 'build_report.json').read_text(encoding='utf-8'))
        self.assertEqual(persisted['performance'], result['performance'])
        self.assertIn('publish', persisted['performance']['timings'])
        database = self.database()
        self.assertEqual(database["format"], "sttv.parse_database")
        self.assertEqual(set(database), {"format", "format_version", "documents"})
        document = database["documents"][0]
        self.assertEqual(document["source"]["file"], "common/technology/base.txt")
        self.assertEqual(document["items"][1]["value"]["text"], "@base")
        content = self.database_path().read_bytes()
        self.assertEqual(self.run_build()["status"], "success")
        self.assertEqual(content, self.database_path().read_bytes())
        self.assertEqual(before, self.hashes())
        self.assertFalse(list(self.database_path().parent.rglob("*.txt")))
        self.assertFalse(list(self.database_path().parent.rglob("*.tmp")))

    def test_unknown_names_repeats_and_literal_references_are_saved(self):
        self.write_script("base.txt", 'future={x=yes x=42 x="@unknown" arbitrary > nonexistent} future={}')
        self.variables.update(WORKSHOP_DIR=str(self.root / "missing_workshop"),
                              RU_LOC_TIER_1=str(self.root / "missing_ru"))
        result = self.run_build()
        self.assertEqual(result["status"], "success", result)
        self.assertEqual(result["counts"]["warnings"], 0)
        items = self.database()["documents"][0]["items"]
        self.assertEqual([n["key"]["text"] for n in items], ["future", "future"])
        self.assertEqual([n["value"]["text"] for n in items[0]["value"]["items"]],
                         ["yes", "42", "@unknown", "nonexistent"])

    def test_loading_requires_neither_game_nor_parser_settings(self):
        self.assertEqual(self.run_build()["status"], "success")
        expected = self.database()
        self.game.rename(self.root / "unavailable_game")
        with patch("sttv.sources.settings.load_settings", side_effect=AssertionError("No settings")):
            self.assertEqual(read_database(self.database_path()), expected)
        json.dumps(expected, allow_nan=False)

    def test_syntax_and_encoding_failure_preserve_previous_database(self):
        self.assertEqual(self.run_build()["status"], "success")
        before = self.database_path().read_bytes()
        for data in (b"x={", b"x=\xff"):
            (self.tech / "base.txt").write_bytes(data)
            result = self.run_build()
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["counts"]["failed_files"], 1)
            self.assertFalse(result["database_written"])
            self.assertEqual(before, self.database_path().read_bytes())

    def test_database_write_failure_preserves_existing_database(self):
        self.assertEqual(self.run_build()["status"], "success")
        before = self.database_path().read_bytes()
        with patch("sttv.database.storage.os.replace", side_effect=OSError("Simulated write failure")):
            result = self.run_build()
        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["database_written"])
        self.assertEqual(before, self.database_path().read_bytes())
        self.assertFalse(list(self.database_path().parent.rglob("*.tmp")))

    def test_report_failure_after_database_replacement_is_truthful(self):
        from os import replace
        self.assertEqual(self.run_build()["status"], "success")
        self.write_script("base.txt", "new_data=yes")

        def fail_report(source, target):
            if target.name == "build_report.json":
                raise OSError("Report destination unavailable")
            return replace(source, target)

        with patch("sttv.database.storage.os.replace", side_effect=fail_report):
            result = self.run_build()
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["database_written"])
        self.assertEqual(self.database()["documents"][0]["items"][0]["key"]["text"], "new_data")
        self.assertFalse(list(self.database_path().parent.rglob("*.tmp")))
