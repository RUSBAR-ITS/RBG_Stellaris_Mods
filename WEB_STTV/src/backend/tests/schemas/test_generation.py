"""Reproducible schema declarations and shared field-contract behavior."""

from unittest.mock import patch

from jsonschema import Draft202012Validator

from support import BuildFixture, PRODUCT_ROOT, registry
from sttv.common.json_io import read_json
from sttv.common.report import Report
from sttv.schema_generation.generate import declarations, generate_schemas
from sttv.schema_generation.database import fields
from support import parse_entries as parse_text
from sttv.script.rules import ScriptRules
from sttv.script.variables import Variables
from sttv.technologies.contracts import CONTRACTS, Field
from sttv.technologies.conversion import Converter


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

    def test_converter_and_schema_share_cardinality_without_an_independent_field_list(self):
        nodes = parse_text("fixture_flag = yes fixture_flag = no")
        converter = Converter(Variables([]), ScriptRules(registry()), Report(), "fixture.txt", "tech_fixture")
        with patch.dict(CONTRACTS["technologies"], {"fixture_flag": Field("boolean", multiple=True)}):
            converted = converter.fields(nodes, "technologies")
            self.assertEqual(converted["fixture_flag"], [True, False])
            validator = Draft202012Validator(fields("technologies"))
            validator.validate(converted)
            self.assertFalse(validator.is_valid({"fixture_flag": True}))
        self.assertNotIn("fixture_flag", fields("technologies")["properties"])

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
