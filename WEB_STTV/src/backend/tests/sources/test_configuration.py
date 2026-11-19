"""Configuration boundaries and command-line behavior."""

import json
import subprocess
import sys
from pathlib import Path

from support import BuildFixture
from sttv.builder import build
from sttv.common.errors import BuildError
from sttv.common.paths import PRODUCT_ROOT
from sttv.sources.settings import expand_variables


class ConfigurationTests(BuildFixture):
    def test_substitutions_and_invalid_variables(self):
        self.assertEqual(expand_variables({"A": "root", "B": "$" "{A}/child"})["B"],
                         "root/child")
        for values in ({"A": "$" "{missing}"}, {"A": "$" "{B}", "B": "$" "{A}"},
                       {"A": 2}, {"A": ""}, {"bad": "x"}, {"A": "$" "{A"}):
            with self.subTest(values=values), self.assertRaises(BuildError):
                expand_variables(values)

    def test_relative_work_directory_and_cli_from_other_directory(self):
        self.variables["WORK_DIR"] = self.root.relative_to(PRODUCT_ROOT).as_posix() + "/work"
        self.assertEqual(self.run_build()["status"], "success")
        result = subprocess.run(
            [sys.executable, "-B", str(PRODUCT_ROOT / "src/backend/main.py"),
             "--reuse-libraries", "--variables", str(self.variable_file), "--config", str(self.config_file)],
            cwd=self.root, capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "success")
        self.assertTrue((PRODUCT_ROOT / self.variables["WORK_DIR"] / "database_set/manifest.json").is_file())

    def test_cli_failure_returns_report_and_nonzero_exit(self):
        self.write_script("base.txt", "tech_a = { unclosed = yes")
        self.run_build()
        result = subprocess.run(
            [sys.executable, "-B", str(PRODUCT_ROOT / "src/backend/main.py"),
             "--reuse-libraries", "--variables", str(self.variable_file), "--config", str(self.config_file)],
            cwd=self.root, capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(json.loads(result.stderr)["status"], "failed")

    def test_outputs_cannot_escape_work_or_write_to_sources(self):
        before = self.hashes()
        for filename in ("../escaped.json", str(self.tech / "result.json")):
            self.options["outputs"]["report"] = filename
            result = self.run_build()
            self.assertTrue({"unsafe_output", "schema_error"}.intersection(self.errors(result)))
            self.assertFalse(result["database_written"])
        self.options["outputs"]["report"] = "database_set/manifest.json"
        self.variables["WORK_DIR"] = str(self.game / "work")
        self.assertIn("unsafe_output", self.errors(self.run_build()))
        self.assertEqual(self.hashes(), before)
        self.assertFalse((self.game / "work").exists())

    def test_colliding_outputs_and_unavailable_sources(self):
        self.options["outputs"]["report"] = "database_set/manifest.json"
        self.assertIn("output_collision", self.errors(self.run_build()))
        self.options["outputs"]["report"] = "reports/build_report.json"
        self.variables["TECH_PATH"] = "common/missing"
        result = self.run_build()
        self.assertIn("source_unavailable", self.errors(result))
        self.assertFalse(self.database_path().exists())
        self.assertTrue((self.root / "work/reports/build_report.json").is_file())

    def test_unknown_config_fields_and_duplicate_json_keys(self):
        self.options["unexpected"] = True
        self.assertIn("schema_error", self.errors(self.run_build()))
        self.variable_file.write_text('{"WORK_DIR":"one","WORK_DIR":"two"}', encoding="utf-8")
        result = build(self.variable_file, self.config_file, library_mode='rebuild')
        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["database_written"])
