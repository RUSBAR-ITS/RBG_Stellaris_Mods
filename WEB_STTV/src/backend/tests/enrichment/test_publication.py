"""Failure safety, input consistency, and independent database reads."""

from unittest.mock import patch

from sttv.common.schema import validate_schema
from sttv.database.storage import read_database
from sttv.enrichment.localization.snapshot import Snapshot
from .support import LocalizationFixture


class PublicationTests(LocalizationFixture):
    def test_completed_database_reads_without_sources(self):
        self.assert_success(self.run_operation())
        with patch("sttv.enrichment.localization.reader.read_entries", side_effect=AssertionError("Source access")), \
             patch("sttv.sources.settings.load_settings", side_effect=AssertionError("Parser access")):
            database = self.read_db()["documents"][0]
        self.assertEqual(database["format_version"], 1)

    def test_missing_directory_does_not_fall_through(self):
        self.variables["RU_LOC_TIER_1"] = str(self.root / "missing")
        self.assert_failure("source_unavailable")

    def test_output_and_input_collisions_are_rejected(self):
        self.options["report"] = "database_set/manifest.json"
        self.assert_failure("output_collision")
        self.options["report"] = "../outside.json"
        self.assert_failure("schema_error")
        self.options["report"] = "reports/report.json"
        self.variables["WORK_DIR"] = str(self.directories["RU_LOC_TIER_1"])
        self.assert_failure("unsafe_output")

    def test_database_config_alias_is_protected(self):
        self.config_file = self.database_path
        result = self.run_operation()
        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["database_written"])

    def test_input_mutation_prevents_database_replacement(self):
        original = Snapshot.verify
        def mutate(snapshot):
            self.write_localization("RU_LOC_TIER_2", {"tech_a": "Changed during run"})
            original(snapshot)
        with patch.object(Snapshot, "verify", mutate):
            self.assert_failure("input_changed")
        self.assertEqual(list(self.work.glob("*.tmp")), [])

    def test_new_source_file_is_detected(self):
        original = Snapshot.verify
        def mutate(snapshot):
            original(snapshot)
            self.write_localization("RU_LOC_TIER_1", {"tech_a": "New override"}, "new.yml")
        with patch.object(Snapshot, "verify", mutate):
            self.assert_failure("input_changed")

    def test_failure_before_replacement_preserves_database(self):
        with patch("sttv.enrichment.localization.operation.write_document", side_effect=OSError("Disk full")):
            report = self.assert_failure("localization_error")
        validate_schema(report, "localization_report.schema.json")

    def test_report_failure_after_replacement_is_truthful(self):
        with patch("sttv.enrichment.localization.operation.save_json", side_effect=OSError("Report locked")):
            report = self.run_operation()
        self.assertEqual(report["status"], "failed")
        self.assertTrue(report["database_written"])
        self.assertIsNotNone(report["database_after"])
        self.assertEqual(self.localized()["text"], "Base Shared")
        validate_schema(report, "localization_report.schema.json")

    def test_configurable_variables_and_no_definition_reads(self):
        self.variables["LOCAL_ROOT"] = str(self.root)
        self.variables["RU_LOC_TIER_1"] = "${LOCAL_ROOT}/RU_LOC_TIER_1"
        with patch("sttv.sources.settings.load_settings", side_effect=AssertionError("Parser load")):
            report = self.run_operation()
        self.assert_success(report)
        validate_schema(report, "localization_report.schema.json")

    def test_invalid_configuration_is_a_structured_failure(self):
        self.options["references"]["key_pattern"] = "["
        result = self.assert_failure("invalid_localization_config")
        validate_schema(result, "localization_report.schema.json")
