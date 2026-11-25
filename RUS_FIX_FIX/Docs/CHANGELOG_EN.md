# RUS_FIX_FIX — changelog

## Contents

- [4.5.14 — Stellaris 4.6 compatibility](#4514--stellaris-46-compatibility)
- [4.5.13 — inflections and labels](#4513--inflections-and-labels)
- [Name list review for Stellaris 4.6.0](#name-list-review-for-stellaris-460)
- [4.5.12 — remaining new Stellaris 4.6 entries](#4512--remaining-new-stellaris-46-entries)
- [4.5.11 — leaders and assignments](#4511--leaders-and-assignments)
- [4.5.10 — ethics and population ideology](#4510--ethics-and-population-ideology)
- [4.5.9 — astral rifts](#459--astral-rifts)
- [4.5.8 — economic modifiers](#458--economic-modifiers)
- [4.5.7 — three earlier omissions](#457--three-earlier-omissions)
- [4.5.6 — references to existing translations](#456--references-to-existing-translations)
- [4.5.5 — opinion modifier names](#455--opinion-modifier-names)
- [2026-11-25 — Stellaris 4.6.0 audit](#2026-11-25--stellaris-460-audit)

## 4.5.14 — Stellaris 4.6 compatibility

The project and launcher descriptors now declare support for Stellaris `v4.6.*`.

## 4.5.13 — inflections and labels

Registered the local build with the Stellaris launcher using `mod/RUS_FIX_FIX.mod`. The descriptor points directly to the project directory at `D:/Repos/RBG_Stellaris_Mods/RUS_FIX_FIX`.

Updated the local build plan to skip porting the 19 window layouts. Loading UI Overhaul Dynamic after the localisation mod selects UIOD's layouts for all 19. In-game checks cover Cyrillic rendering in this configuration.

Added 31 entries. Events can use the author's inflections for five types of celestial body, and five growth tooltips can use the genitive form of organic pop growth. Added references to the icons for 20 subject agreement presets, descriptions for the Celestial Tear and two planetary modifiers, the station return restriction and the plural of presapient herds. The sabotage message now uses the author's Russian name for the Orbital Garden. Reviewed all 794 remaining earlier omissions. [Verification results](../../TMP/RUS_FIX_FIX/older_forms_review.json).

## Name list review for Stellaris 4.6.0

Reviewed 869 retired numbering templates across 61 name lists. Verified the author's translations of their modern keys, including 25 differences from Russian vanilla. No runtime changes were needed for version `4.5.12`. [Results by key](../../TMP/RUS_FIX_FIX/name_lists_46.json).

## 4.5.12 — remaining new Stellaris 4.6 entries

Added 235 entries, restoring 220 masked Stellaris 4.6 strings and translating 15 English-only keys. Updated 34 of the 36 existing entries reviewed. Job tooltips now use the stratum names selected by the Warmongers civics. Added inflected faction name parts and restored alternate precursor, revolt and leader memorial texts. Repair descriptions distinguish regeneration speed, rating and flat daily recovery. Added five terms to the [glossary](../../Glossary/rus_fix_fix_terms.json). [Verification by entry](../../TMP/RUS_FIX_FIX/remaining_46_result.json).

## 4.5.11 — leaders and assignments

Restored leader background, assignment, council position, effective level and experience progress in leader details, along with recruitment, starting age, heir and governor effect labels. Gifted now selects the upstream regular, hive or machine text. The Delegate subtitle follows the Willpower DLC check. Added 53 entries and updated three existing entries across six files. The [shared glossary](../../Glossary/rus_fix_fix_terms.json) records six terms for leader classes, the heir and the science ship. [Translations and verification results](../../TMP/RUS_FIX_FIX/leaders_46.json).

## 4.5.10 — ethics and population ideology

Restored 38 ethic requirements, 13 attraction labels and 16 population ideology conditions. Tooltips include absolute ethics wherever the corresponding checks accept them. For Fanatic Purifiers, the tooltip lists all three alternatives in one of the civic's requirements. The parser confirmed one definition per key and checked substitutions with sample values. [Verification by key](../../TMP/RUS_FIX_FIX/ethics_ideology_46.json).

## 4.5.9 — astral rifts

Restored 72 entries for the ordinary and Lost Makers branches of the Baol and Zroni rifts. Of 15 upstream entries reviewed, 13 were updated. Corrected obsolete references in four ordinary Baol encounter descriptions and translated the Grunur address to the flamestorm unit. Inflected names and technology references are preserved. Static checks covered 85 assembled event texts, including both branches for each of 19 technologies. One entry with a repeated ending remains a documented exception. [Verification results](../../TMP/RUS_FIX_FIX/astral_rifts_4.5.9.json).

## 4.5.8 — economic modifiers

Added 102 labels for Purge jobs, 102 for cultural envoy ships and one shared job name with its icon. The 25 flat ship upkeep labels use existing Russian upkeep references. Ship names follow the owner’s ideology. The parser verified all 205 entries and all four ship names. [Specification and verification results](TZ_COMPAT_46_EN.md#economic-modifier-batch).

## 4.5.7 — three earlier omissions

Restored references for the Interlink faction name, the Orchard Forest district cap and monthly Energy Credits from officials. Each entry matches both vanilla languages in Stellaris 4.6.0. The parser verified all 31 references in the original batch. [Verification results](../../TMP/RUS_FIX_FIX/aliases_4.5.7.json).

## 4.5.6 — references to existing translations

Restored 26 references across seven localization files for keys added since the earlier Russian snapshot. They include ten resolution names, modifier labels and the ideology outliner section. Verified both vanilla languages, Russian text resolution and byte preservation of every prior line. The baseline log mentioned 22 of these keys. [Per-key verification](../../TMP/RUS_FIX_FIX/aliases_4.5.6.json).

## 4.5.5 — opinion modifier names

- Added the two Stellaris 4.6.0 references in `utopia_ascension_l_russian.yml` that resolve to the author’s Russian names for Wicked Cyborgs and Soulless Machines. Bumped the local build to `4.5.5`.

## 2026-11-25 — Stellaris 4.6.0 audit

- Compared the working copy, Workshop and vanilla, inventoried files and localization gaps, and checked scripts and window structure.
- Prepared a [draft specification](TZ_COMPAT_46_EN.md), [affected file inventory](VANILLA_CHANGES_EN.md) and 18 translation proposals. The local build remains at 4.5.4 pending specification approval and implementation.
- Proposed two references to existing opinion modifier translations for separate approval. The startup log confirms both missing keys.
