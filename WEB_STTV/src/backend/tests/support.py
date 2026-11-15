"""Isolated source fixtures and outputs, always inside the project work folder."""

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
def registry():
    from sttv.rules.compiler import generate_registry, load_profile
    return generate_registry(load_profile(PRODUCT_ROOT / "profiles/stellaris_4_5_4.json"))


@lru_cache
def syntax():
    from sttv.script.syntax import load_syntax
    return load_syntax(PRODUCT_ROOT / "config/parser/lexical.json",
                       PRODUCT_ROOT / "config/parser/constructs.json")


def parse_entries(text):
    from sttv.script.parser import parse_text
    from sttv.script.serialization import data_entries
    return data_entries(parse_text(text, syntax()))


class BuildFixture(unittest.TestCase):
    def setUp(self):
        base = (PRODUCT_ROOT / "data" / "tests").resolve()
        base.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=base)
        self.root = Path(self.temporary.name).resolve()
        assert self.root.is_relative_to(base)
        self.game = self.root / "game"
        self.tech = self.game / "common/technology"
        for name in ("", "category", "tier"):
            (self.tech / name).mkdir(parents=True, exist_ok=True)
        self.locales = {name: self.root / name for name in ("ru1", "ru2", "ru3", "en1")}
        for directory in self.locales.values():
            directory.mkdir()
        self.options = copy.deepcopy(read_json(PRODUCT_ROOT / "config/backend.json"))
        self.variables = {
            "WORK_DIR": str(self.root / "work"),
            "STELLARIS_ROOT": str(self.game),
            "WORKSHOP_DIR": str(self.root / "workshop"),
            "TECH_PATH": "common/technology",
            **{f"RU_LOC_TIER_{i}": str(self.locales[f"ru{i}"]) for i in (1, 2, 3)},
            "EN_LOC_TIER_1": str(self.locales["en1"]),
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
        self.write_locale("en1", 'tech_a:0 "Name A"\ntech_a_variant:0 "Variant"\ntech_b:0 "Name B"')
        self.write_locale("ru1", 'tech_a:0 "\u0418\u043c\u044f A"')
        self.write_locale("ru2", 'tech_a:0 "Lower priority"\ntech_a_variant:0 ""')
        self.write_locale("ru3", 'tech_b:0 "\u0418\u043c\u044f B"')

    def tearDown(self):
        assert self.root.is_relative_to((PRODUCT_ROOT / "data/tests").resolve())
        self.temporary.cleanup()

    def write_script(self, name, content):
        (self.tech / name).write_text(content, encoding="utf-8-sig")

    def write_locale(self, source, content, name="names.yml"):
        header = "l_english" if source == "en1" else "l_russian"
        (self.locales[source] / name).write_text(header + ":\n" + content + "\n",
                                                encoding="utf-8-sig")

    def run_build(self):
        for path, value in ((self.variable_file, self.variables),
                            (self.config_file, self.options)):
            path.write_text(json.dumps(value), encoding="utf-8")
        return build(self.variable_file, self.config_file)

    def database_path(self):
        return Path(self.variables["WORK_DIR"]) / self.options["outputs"]["database"]

    def database(self):
        return read_json(self.database_path())

    def errors(self, result):
        return [row["code"] for row in result["diagnostics"] if row["severity"] == "error"]

    def hashes(self):
        sources = [self.game, *self.locales.values()]
        return {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                for root in sources for path in root.rglob("*") if path.is_file()}
