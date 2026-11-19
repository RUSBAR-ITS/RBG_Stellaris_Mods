"""Reproducible schema declarations and shared field-contract behavior."""

from unittest.mock import patch

from jsonschema import Draft202012Validator

from support import BuildFixture, PRODUCT_ROOT
from sttv.common.json_io import read_json
from sttv.common.report import Report
from sttv.schema_generation.generate import declarations, generate_schemas


class GenerationTests(BuildFixture):
    def test_generation_is_repeatable_and_matches_shipped_schemas_without_game_access(self):
        destination = self.root / "schemas"
        with patch("sttv.sources.files.read_source", side_effect=AssertionError("No game reads")):
            first = generate_schemas(destination)
            self.assertEqual(first["status"], "success")
            before = {path.name: path.read_bytes() for path in destination.iterdir()}
            self.assertEqual(generate_schemas(destination)["status"], "success")
            self.assertEqual(before, {path.name: path.read_bytes() for path in destination.iterdir()})
        self.assertEqual(before, {name: (PRODUCT_ROOT / "schemas" / name).read_bytes() for name in before})
        for name in declarations():
            Draft202012Validator.check_schema(read_json(destination / name))

    def test_active_schemas_match_declarations(self):
        self.assertEqual(len(declarations()), 34)
        self.assertEqual(set(declarations()), {path.name for path in (PRODUCT_ROOT / 'schemas').glob('*.json')})

    def test_generation_reports_partial_writes(self):
        destination = self.root / "schemas"
        from sttv.schema_generation.generate import save_json
        calls = []

        def interrupted(path, *args, **kwargs):
            calls.append(path.name)
            if len(calls) == 3:
                raise OSError("Simulated generator failure")
            return save_json(path, *args, **kwargs)

        with patch("sttv.schema_generation.generate.save_json", side_effect=interrupted):
            result = generate_schemas(destination)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["written"], calls[:2])
        self.assertEqual(sorted(path.name for path in destination.iterdir()), sorted(calls[:2]))
