"""Profile composition, semantic restrictions, and effective-rule regression."""

import copy
import unittest

from support import PRODUCT_ROOT, registry
from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.rules.compiler import fingerprint, generate_registry
from support import parse_entries as parse_text
from sttv.script.serialization import script_block
from sttv.script.rules import ScriptRules


def profile():
    return read_json(PRODUCT_ROOT / "profiles/stellaris_4_5_4.json")


def boolean_group(value):
    return next(group for group in value["command_groups"] if "is_ai" in group["commands"])


class ProfileTests(unittest.TestCase):
    def test_initial_effective_rules_match_migrated_reference(self):
        value = registry()
        effective = {key: value[key] for key in (
            "value_types", "scopes", "root_scope", "conditions", "contexts", "inline_scripts")}
        expected = (PRODUCT_ROOT / "src/backend/tests/fixtures/initial_rules.sha256").read_text().strip()
        self.assertEqual(fingerprint(effective), expected)

    def test_identical_groups_consolidate_but_conflicts_fail(self):
        value = profile()
        before = generate_registry(value)
        group = copy.deepcopy(boolean_group(value))
        value["command_groups"].append(group)
        after = generate_registry(value)
        self.assertEqual(before["conditions"], after["conditions"])
        value["templates"]["conflict"] = {
            "extends": group["template"], "rule": {"type": "number"}}
        group["template"] = "conflict"
        with self.assertRaises(BuildError) as error:
            generate_registry(value)
        self.assertEqual(error.exception.code, "rule_conflict")

    def test_inheritance_and_individual_override(self):
        value = profile()
        base = boolean_group(value)["template"]
        value["templates"]["custom"] = {"extends": base, "rule": {"operators": ["=", "!="]}}
        value["command_groups"].append({
            "context": "condition", "template": "custom", "commands": ["custom_condition"], "evidence": []})
        value["overrides"].append({
            "context": "condition", "command": "custom_condition",
            "rule": {"many": False}, "reason": "Fixture cardinality", "evidence": []})
        rules = ScriptRules(generate_registry(value))
        rules.validate(script_block(parse_text("custom_condition != yes")), "condition")
        with self.assertRaises(BuildError) as error:
            rules.validate(script_block(parse_text("custom_condition = yes custom_condition = no")), "condition")
        self.assertEqual(error.exception.code, "repeated_argument")
        with self.assertRaises(BuildError):
            ScriptRules(registry()).validate(script_block(parse_text("custom_condition = yes")), "condition")

    def test_profile_changes_scope_inline_parameters_and_numeric_constraints(self):
        value = profile()
        value["scopes"].append("custom_scope")
        value["value_types"]["bounded"] = {"kind": "integer", "minimum": 1, "maximum": 5}
        value["templates"]["number_custom"] = {"rule": {
            "type": "bounded", "scopes": ["custom_scope"], "operators": [">="], "many": True,
            "context": None, "scope": None}}
        value["command_groups"].append({
            "context": "condition", "template": "number_custom", "commands": ["custom_number"], "evidence": []})
        value["inline_scripts"]["custom/path"] = {"scalar": False, "parameters": {"COUNT": "bounded"}}
        rules = ScriptRules(generate_registry(value))
        rules.validate(script_block(parse_text("custom_number >= 3")), "condition", "custom_scope")
        for text, scope in (("custom_number >= 3", "country"), ("custom_number >= 6", "custom_scope"),
                            ("custom_number = 3", "custom_scope")):
            with self.subTest(text=text, scope=scope), self.assertRaises(BuildError):
                rules.validate(script_block(parse_text(text)), "condition", scope)
        rules.inline(script_block(parse_text("script = custom/path COUNT = 2")), "country", "test")
        with self.assertRaises(BuildError):
            rules.inline(script_block(parse_text("script = custom/path COUNT = 9")), "country", "test")

    def test_missing_references_cycles_and_unsupported_forms(self):
        mutations = [
            lambda p: p["templates"].update(loop={"extends": "loop", "rule": {}}),
            lambda p: p["command_groups"][0].update(template="absent"),
            lambda p: p["command_groups"][0].update(context="absent"),
            lambda p: p["command_groups"][0].update(evidence=["absent"]),
            lambda p: p["templates"][boolean_group(p)["template"]]["rule"].update(scopes=["absent"]),
            lambda p: p["templates"][boolean_group(p)["template"]]["rule"].update(operators=["=="]),
            lambda p: p["value_types"].update(unsupported={"kind": "execute_python"}),
            lambda p: p["value_types"]["boolean"].update(minimum=0),
            lambda p: p["value_types"]["identifier"].update(pattern="["),
            lambda p: p["contexts"]["condition"].update(required=["absent"]),
            lambda p: p["inline_scripts"].update(bad={"scalar": False, "parameters": {"X": "block"}}),
            lambda p: p.update(unexpected=True),
        ]
        for mutate in mutations:
            value = profile()
            mutate(value)
            with self.subTest(mutation=mutate), self.assertRaises(BuildError) as error:
                generate_registry(value)
            self.assertTrue(error.exception.field_path)

    def test_required_fields_and_effective_default_behavior(self):
        rules = ScriptRules(registry())
        good = [
            ("has_resource = { type = energy amount >= 1 }", "condition"),
            ("is_ai = yes is_ai = no", "condition"),
            ("factor = @external", "calculation"),
            ("factor = value:example", "calculation"),
            ("inline_script = ai/shield_preference_weight", "calculation"),
        ]
        for text, context in good:
            rules.validate(script_block(parse_text(text)), context)
        bad = [
            ("has_resource = { type = energy }", "condition"),
            ("has_resource = { type = energy amount = 1 amount = 2 }", "condition"),
            ("has_resource = { type = energy amount = text }", "condition"),
            ("is_ai != yes", "condition"),
            ("factor = nan", "calculation"),
            ("inline_script = { script = ai/weapon_preference_weight EXTRA = yes }", "calculation"),
        ]
        for text, context in bad:
            with self.subTest(text=text), self.assertRaises(BuildError):
                rules.validate(script_block(parse_text(text)), context)
