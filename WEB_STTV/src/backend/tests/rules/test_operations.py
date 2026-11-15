"""Explicit selection, stale registry refusal, and safe partial persistence."""

import copy
from pathlib import Path
from unittest.mock import patch

from support import BuildFixture, PRODUCT_ROOT
from sttv.common.errors import BuildError
from sttv.common.json_io import json_text, read_json
from sttv.rules.compiler import generate_registry
from sttv.rules.operations import save_profile, save_registry
from sttv.sources.settings import load_settings


class RuleOperationTests(BuildFixture):
    def settings(self):
        return load_settings(self.variable_file, self.config_file)

    def test_user_selection_and_invalid_profile_do_not_reuse_old_registry(self):
        self.assertEqual(self.run_build()["status"], "success")
        settings = self.settings()
        original_db, original_registry = settings.database.read_bytes(), settings.registry.read_bytes()
        value = read_json(settings.profile)
        value["profile_id"] = "user_fixture"
        save_profile(settings, value, "profiles/user.json")
        self.options["rules"]["profile"] = {"base": "work", "path": "profiles/user.json"}
        self.assertEqual(self.run_build()["status"], "success")
        self.assertEqual(read_json(settings.registry)["profile_id"], "user_fixture")
        current = settings.registry.read_bytes()
        value["unknown"] = True
        (settings.work / "profiles/user.json").write_text(json_text(value), encoding="utf-8")
        result = self.run_build()
        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["registry_written"])
        self.assertEqual(settings.registry.read_bytes(), current)
        self.assertEqual(settings.database.read_bytes(), original_db)
        self.assertNotEqual(original_registry, current)
        self.options["rules"]["profile"] = {"base": "product", "path": "profiles/user.json"}
        self.assertEqual(self.run_build()["status"], "failed")

    def test_invalid_saved_profile_and_registry_preserve_existing_files(self):
        self.run_build()
        settings = self.settings()
        value = read_json(settings.profile)
        save_profile(settings, value, "profiles/user.json")
        before = (settings.work / "profiles/user.json").read_bytes()
        invalid = copy.deepcopy(value)
        invalid["value_types"]["unknown"] = {"kind": "unimplemented"}
        with self.assertRaises(BuildError):
            save_profile(settings, invalid, "profiles/user.json")
        self.assertEqual((settings.work / "profiles/user.json").read_bytes(), before)
        old = settings.registry.read_bytes()
        registry = generate_registry(value)
        registry["contexts"]["condition"]["rules"]["unknown"] = {}
        with self.assertRaises(BuildError):
            save_registry(settings, registry)
        self.assertEqual(settings.registry.read_bytes(), old)

    def test_protected_paths_and_colliding_outputs(self):
        self.run_build()
        settings = self.settings()
        value = read_json(settings.profile)
        for path in ("../outside.json", "rules/user.json", str(PRODUCT_ROOT / "profiles/x.json")):
            with self.subTest(path=path), self.assertRaises(BuildError):
                save_profile(settings, value, path)
        self.options["rules"]["registry"] = self.options["outputs"]["database"]
        self.assertIn("output_collision", self.errors(self.run_build()))
        self.options["rules"]["registry"] = "rules/script_rules.json"
        self.variables["WORK_DIR"] = str(PRODUCT_ROOT)
        self.options["rules"]["registry"] = "profiles/overwrite.json"
        self.assertIn("unsafe_output", self.errors(self.run_build()))
        self.options["rules"]["registry"] = "README_EN.md"
        self.assertIn("unsafe_output", self.errors(self.run_build()))

    def test_generation_report_failure_reports_actual_registry_write(self):
        self.run_build()
        from sttv.rules.operations import save_json

        def fail_report(path, value, *args, **kwargs):
            if path.name == "generation_report.json":
                raise OSError("Simulated report failure")
            return save_json(path, value, *args, **kwargs)

        with patch("sttv.rules.operations.save_json", side_effect=fail_report):
            result = self.run_build()
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["registry_written"])
        self.assertFalse(result["generation_report_written"])
        self.assertFalse(result["database_written"])

    def test_build_never_runs_analysis_and_reports_version_mismatch(self):
        self.options["rules"]["game_version"] = "future"
        with patch("sttv.analysis.operations.analyze", side_effect=AssertionError("No analysis")):
            result = self.run_build()
        self.assertEqual(result["status"], "success")
        self.assertTrue(any(row["code"] == "version_mismatch" for row in result["diagnostics"]))
