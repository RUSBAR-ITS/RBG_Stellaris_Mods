"""Analyzer observations, optional formats, and profile-bound review results."""

import copy
from pathlib import Path

from support import BuildFixture, PRODUCT_ROOT
from sttv.analysis.operations import analyze, save_analysis
from sttv.analysis.recommendations import validate_recommendation_profile
from sttv.common.errors import BuildError
from sttv.common.json_io import json_text, read_json
from sttv.sources.settings import load_settings


class AnalysisTests(BuildFixture):
    def setUp(self):
        super().setUp()
        self.assertEqual(self.run_build()["status"], "success")
        self.settings = load_settings(self.variable_file, self.config_file)
        self.analysis_path = self.root / "analysis.json"
        self.options_analysis = read_json(PRODUCT_ROOT / "config/analysis.json")

    def run_analysis(self):
        self.analysis_path.write_text(json_text(self.options_analysis), encoding="utf-8")
        return analyze(self.settings, self.analysis_path)

    def source(self, name, kind, text, filename="sample.txt", version=None):
        directory = self.root / name
        directory.mkdir(exist_ok=True)
        path = directory / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        item = {"id": name, "kind": kind, "path": str(directory), "pattern": "*",
                "recursive": True, "encoding": "utf-8-sig", "enabled": True, "game_version": version}
        self.options_analysis["sources"].append(item)
        return item

    def test_known_sources_are_repeatable_and_never_mutate_database_or_profile(self):
        before = self.hashes()
        profile = self.settings.profile.read_bytes()
        database = self.settings.database.read_bytes()
        result = self.run_analysis()
        self.assertEqual(result["status"], "complete")
        self.assertTrue(result["observations"])
        self.assertEqual(result["recommendations"], [])
        self.assertEqual(result, self.run_analysis())
        self.assertEqual(self.hashes(), before)
        self.assertEqual(self.settings.profile.read_bytes(), profile)
        self.assertEqual(self.settings.database.read_bytes(), database)
        saved = save_analysis(self.settings, self.analysis_path, result)
        self.assertTrue(saved["written"])

    def test_unknown_block_does_not_inherit_country_and_proposals_are_review_only(self):
        self.write_script("base.txt", """tech_a = { potential = {
 is_ai = yes
 future_owner = { has_technology = tech_x }
 future_count >= 3
} }""")
        result = self.run_analysis()
        rows = result["observations"]
        child = next(row for row in rows if row["command"] == "has_technology")
        self.assertIsNone(child["scope"])
        self.assertIsNone(child["context"])
        self.assertIn("future_owner", child["path"])
        self.assertEqual(child["line"], 3)
        self.assertTrue(result["recommendations"])
        count = next(row for row in result["recommendations"] if row["target"]["command"] == "future_count")
        self.assertTrue(count["alternatives"])
        self.assertIn("inference", count["basis"])
        self.assertTrue(count["questions"])
        self.assertEqual(self.run_build()["status"], "failed")

    def test_documentation_extracts_operators_scopes_and_conflicts(self):
        self.source("docs", "engine_documentation", """== TRIGGER DOCUMENTATION ==
is_ai - Fixture documented condition
is_ai != yes
Supported Scopes: planet

has_resource - Fixture amount
has_resource = { type = energy amount = 1 }
Supported Scopes: country planet
""", "triggers.log", "future")
        result = self.run_analysis()
        row = next(row for row in result["observations"] if row["source"] == "docs" and row["command"] == "is_ai")
        self.assertEqual(row["documented_scopes"], ["planet"])
        self.assertEqual(row["documented_operators"], ["!="])
        self.assertEqual(row["basis"], "documentation")
        rec = next(row for row in result["recommendations"] if row["target"]["command"] == "is_ai")
        self.assertTrue(rec["contradictions"])
        self.assertTrue(any(row["code"] == "version_mismatch" for row in result["diagnostics"]))
        self.assertEqual(result["status"], "complete")

    def test_scripted_triggers_and_inline_parameter_definitions(self):
        self.source("triggers", "scripted_triggers",
                    'custom_trigger = { has_technology = $TECH$ } other_trigger = { is_ai = yes }')
        self.source("inlines", "inline_scripts", 'factor = $FACTOR$\nis_ai = yes', "folder/custom.txt")
        result = self.run_analysis()
        definitions = [row for row in result["observations"] if row["form"] == "definition"]
        by_name = {row["command"]: row for row in definitions}
        self.assertEqual(by_name["custom_trigger"]["parameters"], ["TECH"])
        self.assertEqual(by_name["other_trigger"]["parameters"], [])
        self.assertEqual(by_name["folder/custom"]["parameters"], ["FACTOR"])
        self.assertTrue(any(row["target"]["section"] == "inline_scripts" for row in result["recommendations"]))
        self.assertTrue(any(row["code"] == "unknown_version" for row in result["diagnostics"]))

    def test_disabled_missing_and_unsupported_sources_have_honest_status(self):
        item = self.source("disabled", "engine_documentation", "ignored")
        item.update(enabled=False, path="$" "{NOT_DEFINED}/missing")
        missing = self.source("missing", "scripted_triggers", "unused")
        missing["path"] = str(self.root / "absent")
        self.source("bad_docs", "engine_documentation", "Not a documented log", "wrong.log")
        result = self.run_analysis()
        self.assertEqual(result["status"], "partial")
        manifests = {row["id"]: row for row in result["sources"]}
        self.assertEqual(manifests["disabled"]["status"], "disabled")
        self.assertFalse(manifests["disabled"]["files"])
        self.assertEqual(manifests["missing"]["status"], "unavailable")
        codes = {row["code"] for row in result["diagnostics"]}
        self.assertIn("source_unavailable", codes)
        self.assertIn("unsupported_documentation", codes)

    def test_stale_recommendations_and_output_inside_source_are_rejected(self):
        self.write_script("base.txt", "tech_a = { potential = { unknown = yes } }")
        result = self.run_analysis()
        profile = read_json(self.settings.profile)
        validate_recommendation_profile(result, profile)
        changed = copy.deepcopy(profile)
        changed["revision"] += 1
        with self.assertRaises(BuildError) as error:
            validate_recommendation_profile(result, changed)
        self.assertEqual(error.exception.code, "stale_recommendations")
        source = self.settings.work / "analyzer_input"
        source.mkdir()
        (source / "script.txt").write_text("custom = { is_ai = yes }", encoding="utf-8")
        self.options_analysis["sources"] = [{
            "id": "protected", "kind": "scripted_triggers", "path": str(source),
            "pattern": "*.txt", "recursive": False, "encoding": "utf-8-sig",
            "enabled": True, "game_version": None}]
        self.options_analysis["output"] = "analyzer_input/report.json"
        result = self.run_analysis()
        with self.assertRaises(BuildError):
            save_analysis(self.settings, self.analysis_path, result)
        self.assertFalse((source / "report.json").exists())

    def test_arguments_operators_scopes_and_unknown_fields_are_observed(self):
        self.write_script("base.txt", """tech_a = {
 new_field = 3
 potential = { is_ai > 2 any_owned_planet = { has_valid_civic = civic_test } }
}""")
        result = self.run_analysis()
        rows = {row["command"]: row for row in result["observations"]}
        self.assertIn("invalid_operator", rows["is_ai"]["issues"])
        self.assertIn("invalid_argument", rows["is_ai"]["issues"])
        self.assertIn("invalid_scope", rows["has_valid_civic"]["issues"])
        field = next(row for row in result["recommendations"] if row["target"]["section"] == "fields")
        self.assertEqual(field["alternatives"][0]["action"], "review_contract")
