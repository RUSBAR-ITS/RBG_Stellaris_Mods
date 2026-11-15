"""Evidence edge cases for contextual and parameter recommendations."""

import unittest

from support import registry, syntax
from sttv.analysis.adapters import documentation, script_definitions
from sttv.analysis.walker import Walker
from sttv.analysis.recommendations import recommend
from sttv.common.json_io import read_json
from sttv.common.paths import PRODUCT_ROOT
from support import parse_entries as parse_text
from sttv.script.syntax import make_syntax


class EvidenceTests(unittest.TestCase):
    def test_parameters_follow_selected_delimiters_and_keep_defaults(self):
        selected = make_syntax(syntax().lexical, {**syntax().constructs, 'parameters':
                               {'open': '%', 'close': '%', 'default_separator': ':'}})
        text = '# %COMMENT%\nfactor = %COUNT:1%\nvalue = "pre_%NAME%"'
        walker = Walker(registry(), 'inline', 'fixture.txt', text, 50)
        rows = script_definitions(walker, text, 'inline_scripts', 'fixture.txt', selected)
        self.assertEqual(rows[0]['parameters'], ['COUNT', 'NAME'])

    def test_inline_parameter_mentions_in_comments_are_not_code(self):
        text = "# Example $UNUSED$\nfactor = $COUNT$"
        walker = Walker(registry(), "inline", "fixture.txt", text, 50)
        rows = script_definitions(walker, text, "inline_scripts", "fixture.txt", syntax())
        self.assertEqual(rows[0]["parameters"], ["COUNT"])

    def test_inline_invocation_retains_path_and_new_parameter_name(self):
        text = "tech_a = { weight_modifier = { inline_script = { script = new/path COUNT = 5 } } }"
        walker = Walker(registry(), "TECH_PATH", "fixture.txt", text, 40)
        rows = walker.technologies(parse_text(text), "technologies")
        row = next(item for item in rows if item["command"] == "inline_script")
        self.assertEqual(row["inline_path"], "new/path")
        self.assertEqual(row["parameters"], ["COUNT"])
        profile = read_json(PRODUCT_ROOT / "profiles/stellaris_4_5_4.json")
        result = recommend(rows, profile, registry(), 3)
        self.assertEqual(result[0]["target"]["section"], "inline_scripts")
        self.assertEqual(result[0]["target"]["command"], "new/path")
        self.assertEqual(result[0]["alternatives"][0]["parameters"], ["COUNT"])

    def test_documentation_without_example_does_not_invent_argument_kind(self):
        text = "== TRIGGER DOCUMENTATION ==\ncustom - Unknown signature\nSupported Scopes: all\n"
        walker = Walker(registry(), "docs", "triggers.log", text, 50)
        rows = documentation(walker, text, syntax())
        self.assertEqual(rows[0]["argument_kind"], "unknown")
        self.assertIsNone(rows[0]["operator"])
        self.assertIsNone(rows[0]["scope"])

    def test_scripted_trigger_parameters_are_local_to_definition(self):
        text = "first = { has_technology = $TECH$ } second = { has_ethic = $ETHIC$ }"
        walker = Walker(registry(), "triggers", "fixture.txt", text, 50)
        rows = script_definitions(walker, text, "scripted_triggers", "fixture.txt", syntax())
        definitions = {row["command"]: row for row in rows if row["form"] == "definition"}
        self.assertEqual(definitions["first"]["parameters"], ["TECH"])
        self.assertEqual(definitions["second"]["parameters"], ["ETHIC"])
