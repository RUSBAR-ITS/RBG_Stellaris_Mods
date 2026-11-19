"""Small persisted trees and localization sources inside the repository."""

import copy
import tempfile
import unittest
from pathlib import Path

from support import PRODUCT_ROOT, syntax
from sttv.common.json_io import json_text, read_json
from sttv.database.validation import FORMAT, FORMAT_VERSION
from sttv.enrichment.localization import enrich_localization
from sttv.script.parser import parse_text
from sttv.script.serialization import serialize_document


class LocalizationFixture(unittest.TestCase):
    def setUp(self):
        base = PRODUCT_ROOT / "data/tests"
        base.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=base)
        self.root = Path(self.temporary.name).resolve()
        self.work = self.root / "work"
        self.work.mkdir()
        self.variables = {"WORK_DIR": str(self.work), "STELLARIS_ROOT": str(self.root / "absent_game"),
                          "TECH_PATH": "common/technology"}
        self.directories = {}
        for tier in ("RU_LOC_TIER_1", "RU_LOC_TIER_2", "RU_LOC_TIER_3", "EN_LOC_TIER_1"):
            directory = self.root / tier
            directory.mkdir()
            self.variables[tier] = str(directory)
            self.directories[tier] = directory
        self.options = read_json(PRODUCT_ROOT / "config/enrichment/localization.json")
        self.target_options = read_json(PRODUCT_ROOT / self.options['targets']['technologies']['path'])
        self.target_file = self.work / 'targets.json'
        self.options['targets']['technologies'] = {'base': 'product', 'path': self.target_file.relative_to(PRODUCT_ROOT).as_posix()}
        self.variable_file, self.config_file = self.root / "variables.json", self.root / "localization.json"
        self.database_path = self.work / "database_set/manifest.json"
        self.documents = [("common/technology/base.txt", 'tech_a = { technology_swap = { name = variant_a } } null_void_beam = {}'),
                          ("common/technology/category/base.txt", 'biology = { icon = category }'),
                          ("common/technology/tier/base.txt", '1 = { previously_unlocked = 0 }')]
        self.write_database()
        for tier in ("RU_LOC_TIER_2", "EN_LOC_TIER_1"):
            self.write_localization(tier, {
                "tech_a": "Base $shared$", "tech_a_desc": "Base description",
                "variant_a": "$tech_a$", "shared": "Shared",
                "null_void_beam": "Void", "null_void_beam_desc": "Void description"})

    def tearDown(self):
        assert self.root.is_relative_to((PRODUCT_ROOT / "data/tests").resolve())
        self.temporary.cleanup()

    def write_database(self):
        self.original = {"format": FORMAT, "format_version": FORMAT_VERSION,
                         "documents": [serialize_document(parse_text(text, syntax(), path))
                                       for path, text in self.documents]}
        from storage.fixtures import publish
        self.variable_file.write_text(json_text(self.variables), encoding="utf-8")
        publish(self.variable_file, {"technologies": self.original["documents"]}, validate=True)
        self.original = self.read_db()

    def write_localization(self, tier, values, file="base.yml"):
        header = "l_russian" if tier.startswith("RU") else "l_english"
        content = header + ":\n" + "\n".join(f' {key}:0 "{value}"' for key, value in values.items()) + "\n"
        path = self.directories[tier] / file
        path.write_text(content, encoding="utf-8-sig")
        return path

    def run_operation(self):
        self.target_file.write_text(json_text(self.target_options), encoding='utf-8')
        self.variable_file.write_text(json_text(self.variables), encoding="utf-8")
        self.config_file.write_text(json_text(self.options), encoding="utf-8")
        return enrich_localization(self.variable_file, self.config_file)

    def localized(self, language="ru", variant=False, field="name"):
        node = self.read_db()["documents"][0]["items"][0]
        if variant:
            node = node["value"]["items"][0]
        return node["enrichments"]["localization"][language][field]

    def assert_success(self, report):
        self.assertEqual(report["status"], "success", report["diagnostics"])


    def assert_failure(self, code):
        before = self.database_path.read_bytes()
        result = self.run_operation()
        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["database_written"])
        self.assertIn(code, [row["code"] for row in result["diagnostics"]])
        self.assertEqual(self.database_path.read_bytes(), before)
        return result

    def read_db(self):
        from storage.fixtures import documents
        return {'documents': documents(self.database_path)}
