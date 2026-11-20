"""Isolated source fixtures and outputs, always inside the project work folder."""
from stellaris_parser.schema import CONFIG

from sttv.common.paths import work_directory


import copy
import hashlib
import json
import sys
import tempfile
import unittest
from functools import lru_cache
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sttv.builder import build
from sttv.common.json_io import read_json
from sttv.common.paths import PRODUCT_ROOT


@lru_cache
def syntax():
    from stellaris_parser.script.syntax import load_syntax
    return load_syntax(CONFIG / "lexical.json",
                       CONFIG / "constructs.json",
                       CONFIG / "logical_operators.json")


def syntax_payload(document):
    from stellaris_parser.script.serialization import serialize_document

    def clean(value):
        if isinstance(value, dict):
            return {key: clean(child) for key, child in value.items() if key not in ("origin", "span")}
        if isinstance(value, list):
            return [clean(child) for child in value]
        return value
    return clean(serialize_document(document)["items"])


class BuildFixture(unittest.TestCase):
    def setUp(self):
        base = (work_directory() / "tests").resolve()
        base.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=base)
        self.root = Path(self.temporary.name).resolve()
        assert self.root.is_relative_to(base)
        self.game = self.root / "game"
        self.tech = self.game / "common/technology"
        self.inline = self.game / "common/inline_scripts"
        self.inline.mkdir(parents=True)
        self.static = self.game / 'common/scripted_variables'
        self.static.mkdir(parents=True)
        self.effects = self.game / 'common/scripted_effects'
        self.triggers = self.game / 'common/scripted_triggers'
        self.effects.mkdir(parents=True)
        self.triggers.mkdir(parents=True)
        self.values = self.game / 'common/script_values'
        self.values.mkdir(parents=True)
        (self.static / 'base.txt').write_text('@external = 2', encoding='utf-8')
        for name in ("", "category", "tier"):
            (self.tech / name).mkdir(parents=True, exist_ok=True)
        from sttv.database_sets.configuration import build_options
        self.options = copy.deepcopy(build_options(read_json(PRODUCT_ROOT / "config/backend.json"), "technologies"))
        self.options["outputs"] = {"report": "build_report.json"}
        self.variables = {
            "WORK_DIR": str(self.root / "work"),
            "STELLARIS_ROOT": str(self.game),
            "TECH_PATH": "common/technology",
            "INLINE_SCRIPTS_DIR": "common/inline_scripts",
            "SCRIPTED_EFFECTS_DIR": "common/scripted_effects",
            "SCRIPTED_TRIGGERS_DIR": "common/scripted_triggers",
            "SCRIPTED_VARIABLES_DIR": "common/scripted_variables",
            "SCRIPT_VALUES_DIR": "common/script_values",
        }
        self.variable_file = self.root / "variables.json"
        self.config_file = self.root / "backend.json"
        self.write_script("category/base.txt", "computing = { icon = computing }")
        self.write_script("tier/base.txt", "0 = {} 1 = { previously_unlocked = 0 }")
        self.write_script("base.txt", """
@base = 10
@alias = @base
tech_a = {
 area = physics tier = 1 category = { computing } cost = @alias
 potential = { OR = { is_nomadic = yes NOT = { is_ai = yes } } }
 technology_swap = { name = tech_a_variant trigger = { is_nomadic = yes } }
}
tech_b = {
 area = physics tier = 1 category = { computing }
 prerequisites = { OR = { tech_a } }
 weight = 0 weight = @external
 weight_modifier = { modifier = { factor = 0 has_technology = tech_b } }
}
""")

    def tearDown(self):
        assert self.root.is_relative_to((work_directory() / 'tests').resolve())
        self.temporary.cleanup()

    def write_script(self, name, content):
        (self.tech / name).write_text(content, encoding="utf-8-sig")

    def run_build(self):
        for path, value in ((self.variable_file, self.variables),
                            (self.config_file, self.options)):
            path.write_text(json.dumps(value), encoding="utf-8")
        return build(self.variable_file, self.config_file, library_mode='rebuild')

    def database_path(self):
        return Path(self.variables["WORK_DIR"]) / 'database_set/manifest.json'

    def database(self):
        from storage.fixtures import documents
        return {'documents': documents(self.database_path())}

    def errors(self, result):
        return [row["code"] for row in result["diagnostics"] if row["severity"] == "error"]

    def hashes(self):
        sources = [self.game]
        return {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                for root in sources for path in root.rglob("*") if path.is_file()}
