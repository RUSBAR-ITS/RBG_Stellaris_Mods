"""Strict database validation and preservation of supported source values."""

import copy
from unittest.mock import patch

from support import BuildFixture, registry
from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.localization.names import parse_names
from support import parse_entries as parse_text
from sttv.common.paths import PRODUCT_ROOT
from sttv.common.schema import validate_schema
from sttv.database.validation import validate_database
from sttv.script.variables import Variables


class ValidationTests(BuildFixture):
    def test_closed_objects_and_invalid_types(self):
        self.assertEqual(self.run_build()["status"], "success")
        original = self.database()
        changes = [
            lambda db: db.update(unrecognized={}),
            lambda db: db["technologies"]["tech_a"].update(unrecognized=1),
            lambda db: db["technologies"]["tech_a"]["fields"].update(unrecognized=True),
            lambda db: db["technologies"]["tech_a"]["fields"].update(area="invalid"),
            lambda db: db["technologies"]["tech_a"]["fields"].update(is_rare="yes"),
            lambda db: db["technologies"]["tech_a"]["source"].update(extra="x"),
            lambda db: db["technologies"]["tech_a"]["fields"]["technology_swap"][0].update(parent_id="x"),
            lambda db: db["technologies"]["tech_a"]["fields"]["potential"]["entries"][0].update(extra=0),
        ]
        for change in changes:
            database = copy.deepcopy(original)
            change(database)
            with self.subTest(change=change), self.assertRaises(BuildError):
                validate_database(database, registry())

    def test_missing_internal_references_and_cycles(self):
        self.assertEqual(self.run_build()["status"], "success")
        original = self.database()
        cases = [
            ("missing_technology", "prerequisites", {"all": [{"tech": "tech_missing"}]}),
            ("missing_category", "category", ["missing"]),
            ("missing_tier", "tier", 55),
            ("prerequisite_cycle", "prerequisites", {"all": [{"tech": "tech_b"}]}),
        ]
        for code, field, value in cases:
            database = copy.deepcopy(original)
            database["technologies"]["tech_a"]["fields"][field] = value
            with self.subTest(code=code), self.assertRaises(BuildError) as error:
                validate_database(database, registry())
            self.assertEqual(error.exception.code, code)

    def test_commands_and_name_provenance_are_checked_offline(self):
        self.assertEqual(self.run_build()["status"], "success")
        database = self.database()
        database["technologies"]["tech_a"]["fields"]["potential"]["entries"][0]["key"] = "unknown"
        with self.assertRaises(BuildError):
            validate_database(database, registry())
        database = self.database()
        database["technologies"]["tech_a"]["name_sources"]["ru"]["key"] = "tech_b"
        with self.assertRaises(BuildError) as error:
            validate_database(database, registry())
        self.assertEqual(error.exception.code, "name_provenance")

    def test_local_variables_chains_cycles_and_ambiguity(self):
        variables = Variables(parse_text(
            "@a = 1 @alias = @a @same = 2 @same = 2 @bad = 1 @bad = 2 "
            "@loop = @other @other = @loop @text = yes"))
        self.assertEqual(variables.resolve("@alias"), (1, None))
        self.assertEqual(variables.resolve("@same"), (2, None))
        self.assertEqual(variables.resolve("@bad"), (None, "ambiguous_local_variable"))
        self.assertEqual(variables.resolve("@loop"), (None, "cyclic_local_variable"))
        self.assertEqual(variables.resolve("@external"), (None, "external_variable"))
        self.assertEqual(variables.resolve("@text"), (None, "unresolved_local_variable"))
        self.assertEqual(len(variables.definitions), 9)

    def test_duplicate_ids_and_bad_integer_are_fatal(self):
        for text in ("tech_a = {} tech_a = {}", "@level = 1.5 tech_a = { tier = @level }"):
            with self.subTest(text=text):
                self.write_script("base.txt", text)
                self.assertEqual(self.run_build()["status"], "failed")
                self.assertFalse(self.database_path().exists())

    def test_name_markup_escapes_comments_and_unrelated_keys(self):
        value = r'Name $OTHER$ \n \"quote\" # text ' + "\u00a7Y[Root.GetName]\u00a7!"
        text = 'l_english:\ntech_a:0 "' + value + '" # comment\nunused:0 broken'
        self.assertEqual(list(parse_names(text, "l_english", {"tech_a"})),
                         [("tech_a", value, 2)])
        for text in ('l_russian:\ntech_a:0 "Name"', 'l_english:\ntech_a:0 "open'):
            with self.subTest(text=text), self.assertRaises(BuildError):
                list(parse_names(text, "l_english", {"tech_a"}))

    def test_invalid_utf8_does_not_publish(self):
        (self.tech / "base.txt").write_bytes(b"tech_a = {\xff}")
        self.assertEqual(self.run_build()["status"], "failed")
        self.assertFalse(self.database_path().exists())

    def test_report_preparation_failure_preserves_old_database(self):
        self.assertEqual(self.run_build()["status"], "success")
        before = self.database_path().read_bytes()
        from sttv.database.storage import prepare_json

        def fail_report(path, value, schema):
            if schema == "report.schema.json":
                raise OSError("Simulated report failure")
            return prepare_json(path, value, schema)

        with patch("sttv.database.storage.prepare_json", side_effect=fail_report):
            result = self.run_build()
        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["database_written"])
        self.assertEqual(before, self.database_path().read_bytes())
        self.assertFalse(list(self.root.rglob("*.tmp")))

    def test_report_and_database_schema_definitions(self):
        result = self.run_build()
        validate_schema(result, "report.schema.json")
        for path in (PRODUCT_ROOT / "schemas").glob("*.schema.json"):
            from jsonschema import Draft202012Validator
            Draft202012Validator.check_schema(read_json(path))
