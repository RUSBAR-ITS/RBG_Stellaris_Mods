"""Priority, quoting, reference expansion, and opaque dynamic tokens."""

from .support import LocalizationFixture


class TextTests(LocalizationFixture):
    def test_priorities_apply_to_each_key_and_nested_reference(self):
        self.write_localization("RU_LOC_TIER_1", {"tech_a": "$middle$", "shared": "High"})
        self.write_localization("RU_LOC_TIER_3", {"middle": "Low $shared$"})
        report = self.run_operation()
        self.assert_success(report)
        self.assertEqual(self.localized()["text"], "Low High")
        self.assertEqual(self.localized()["raw"], "$middle$")
        self.assertEqual(self.localized()["source"]["tier"], "RU_LOC_TIER_1")
        self.assertEqual(self.localized("en")["text"], "Base Shared")

    def test_empty_is_present_and_missing_does_not_use_other_language(self):
        self.write_localization("RU_LOC_TIER_2", {"tech_a": ""})
        self.assert_success(self.run_operation())
        self.assertEqual(self.localized()["text"], "")
        self.assertIsNotNone(self.localized()["source"])
        self.assertIsNone(self.localized(variant=True)["text"])
        self.assertIsNone(self.localized(field="description")["text"])

    def test_identical_duplicates_are_deterministic(self):
        for file in ("a.yml", "z.yml"):
            self.write_localization("RU_LOC_TIER_1", {"tech_a": "same"}, file)
        report = self.run_operation()
        self.assert_success(report)
        self.assertEqual(self.localized()["source"]["file"], "a.yml")
        self.assertFalse(report["duplicates"][0]["conflicting"])

    def test_selected_conflict_fails_without_falling_through(self):
        self.write_localization("RU_LOC_TIER_1", {"tech_a": "first"})
        self.write_localization("RU_LOC_TIER_1", {"tech_a": "second"}, "other.yml")
        self.assert_failure("localization_conflict")

    def test_shadowed_or_unreachable_conflicts_are_reported_only(self):
        self.write_localization("RU_LOC_TIER_3", {"tech_a": "first", "unused": "one"})
        self.write_localization("RU_LOC_TIER_3", {"tech_a": "second", "unused": "two"}, "other.yml")
        report = self.run_operation()
        self.assert_success(report)
        self.assertEqual(len(report["duplicates"]), 2)

    def test_quoting_comments_unicode_and_game_escapes_survive(self):
        path = self.directories["RU_LOC_TIER_1"] / "quotes.yml"
        raw = '  \u0418 # "inside" \\"escaped\\" \\n '
        path.write_text('l_english:\n tech_a: "Wrong"\nl_russian:\n tech_a: "' + raw
                        + '" # comment "quoted"\n', encoding="utf-8")
        self.assert_success(self.run_operation())
        self.assertEqual(self.localized()["raw"], raw)
        self.assertEqual(self.localized()["text"], raw)

    def test_dynamic_formatted_and_icon_tokens_are_preserved(self):
        raw = '[This.Get$shared$] $shared|Y$ £$shared$£ §Y$shared$§! $RUNTIME$'
        self.write_localization("RU_LOC_TIER_1", {"tech_a": raw})
        report = self.run_operation()
        self.assert_success(report)
        self.assertEqual(self.localized()["text"],
                         '[This.Get$shared$] $shared|Y$ £$shared$£ §YShared§! $RUNTIME$')
        self.assertEqual(self.localized()["unresolved_references"], ["$RUNTIME$"])

    def test_cycle_has_a_chain_and_preserves_database(self):
        self.write_localization("RU_LOC_TIER_1", {"tech_a": "$loop$", "loop": "$tech_a$"})
        report = self.assert_failure("localization_cycle")
        error = next(row for row in report["diagnostics"] if row["code"] == "localization_cycle")
        self.assertEqual(error["chain"], ["tech_a", "loop", "tech_a"])
        self.assertEqual(error["node"], "/documents/0/items/0")

    def test_depth_and_size_limits(self):
        self.options["references"]["max_depth"] = 1
        self.assert_failure("localization_depth")
        self.options["references"]["max_depth"] = 64
        self.options["references"]["max_characters"] = 3
        self.assert_failure("localization_size")

    def test_shared_dependency_and_case_sensitive_keys(self):
        self.write_localization("RU_LOC_TIER_1", {"tech_a": "$left$$right$ $SHARED$",
                                                  "left": "$shared$", "right": "$shared$"})
        self.assert_success(self.run_operation())
        self.assertEqual(self.localized()["text"], "SharedShared $SHARED$")

    def test_unknown_tokens_do_not_consume_expansion_depth_and_keep_chains(self):
        for tier in ("RU_LOC_TIER_2", "EN_LOC_TIER_1"):
            self.write_localization(tier, {"tech_a": "$RUNTIME$", "variant_a": "Variant"})
        self.options["references"]["max_depth"] = 1
        report = self.run_operation()
        self.assert_success(report)
        warning = next(row for row in report["diagnostics"] if row["code"] == "unresolved_localization")
        self.assertEqual(warning["chain"], ["tech_a", "RUNTIME"])

    def test_malformed_and_invalid_encoding_are_errors(self):
        path = self.directories["RU_LOC_TIER_1"] / "bad.yml"
        path.write_text('l_russian:\n tech_a: "unterminated', encoding="utf-8")
        self.assert_failure("localization_syntax")
        path.write_bytes(b'\xff\xfe\xff')
        self.assert_failure("localization_read_error")
