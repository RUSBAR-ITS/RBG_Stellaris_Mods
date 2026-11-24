# Tass Cheat Tool Extender — changelog

## Contents

- [0.0.9 — 2026-11-24](#009--2026-11-24)
- [0.0.8 — 2026-11-15](#008--2026-11-15)
- [Draft specification: envoys — 2026-11-15](#draft-specification-envoys--2026-11-15)
- [0.0.7 — 2026-11-15](#007--2026-11-15)
- [0.0.6 — 2026-11-15](#006--2026-11-15)
- [Draft specification: species modification — 2026-11-15](#draft-specification-species-modification--2026-11-15)
- [0.0.5 — 2026-11-15](#005--2026-11-15)
- [Draft specification: resource menu — 2026-11-14](#draft-specification-resource-menu--2026-11-14)
- [0.0.4 — 2026-11-14](#004--2026-11-14)
- [Draft specification: 10 levels — 2026-11-14](#draft-specification-10-levels--2026-11-14)
- [0.0.3 — 2026-11-14](#003--2026-11-14)
- [0.0.2 — 2026-11-14](#002--2026-11-14)
- [0.0.1 — 2026-11-14](#001--2026-11-14)
- [Specification extension: descriptions and substitutions — 2026-11-14](#specification-extension-descriptions-and-substitutions--2026-11-14)
- [Specification preparation — 2026-11-14](#specification-preparation--2026-11-14)

## 0.0.9 — 2026-11-24

- Updated for Tass Cheat Tool `20261124` and Stellaris `v4.6.*`. Added Willpower to the end of Special path resources with six standard grant amounts and the `ap_force_of_will` requirement.
- All ten active Ambitions levels include Willpower production and accept the Force of Will perk. Added three Russian Tass strings, updated the icon and tooltips, and localized the grant menu in both languages.
- Verified 585 original and 629 extended policy options, 162 grants and Russian translations for all 1669 source keys. Packaged the release and updated the connected copy of all 116 runtime files. In-game verification is pending. [0.0.9 validation](../../TMP/TCTE/compatibility_0.0.9.json).

## 0.0.8 — 2026-11-15

- Under the approved [specification](TZ_ENVOYS_EN.md), Extra Envoys opens a cumulative +5/+10/+25/+50/+100/+500 menu. Every grant returns to the same menu; Back opens the main menu.
- Added service repeatable technology `tcte_tech_extra_envoys`: +5 capacity per level, zero research draw weight, no starting grant or notifications. Buttons award 1/2/5/10/20/100 levels. No separate country modifier is added; the old +20 bonus in saves is neither removed nor allowed to block the menu.
- Added one event, one technology, and 18 keys per language with references and BOM. Added two glossary terms with eight sources without duplicates. Updated bilingual specifications, README files, and definition inventories; no additional vanilla overrides are introduced.
- Checked all six grants, 176 sequences in an arithmetic model, navigation, three localization baselines, 134 original Tass files, and 11 researched sources. Other main-menu blocks and 110 previous runtime files remain byte-identical.
- Increased the version to 0.0.8 and built a 116-file archive. Updated the connected copy without changing playsets. The user tests technology stacking, envoy availability, and save/load in-game; the arithmetic model does not verify engine behavior.

## Draft specification: envoys — 2026-11-15

- Researched the original +20 grant, effect documentation, envoy class, and vanilla examples of bonuses and repeatable technology grants; recorded sources and fingerprints.
- The user agreed to a service repeatable technology instead of a separate country modifier. Prepared a bilingual [draft specification](TZ_ENVOYS_EN.md): cumulative +5/+10/+25/+50/+100/+500, reopening the same menu, and Back.
- The specification awaits separate approval; implementation has not started. The version remains 0.0.7; all 112 runtime files, the archive, and connected copy are preserved.

## 0.0.7 — 2026-11-15

- Under the user's explicit correction, removed the full copy of `common/scripted_triggers/05_scripted_triggers_traits.txt`. Moved only the modified `can_remove_beneficial_genetic_traits` into `common/scripted_triggers/tcte_species_traits_triggers.txt`; the other 49 definitions load from vanilla.
- Preserved the ID and byte-identical trigger block. The standalone filename sorts after the original file; no `replace_path` is used. Bonuses, cheat toggling, and other runtime files remain unchanged.
- Checked one shipped trigger, all 256 condition combinations, filename ordering, a static loading model, 110 unchanged runtime files, and archive contents. Updated bilingual specifications, README files, and override inventories.
- Updated the archive and connected copy to 0.0.7; removed the previous full file from the installed mod. Playsets and original game files are unchanged. Actual engine loading of the standalone override requires user testing in-game.

## 0.0.6 — 2026-11-15

- Implemented the agreed +100 trait points and +30 trait picks for biological species, robots, and machines. Retained `modifier_tass_extra_species_modding`; while present, the main-menu entry becomes Remove Advanced Species Modification. Enabling and removing return to the same menu.
- Under the user's explicit extension, changed `can_remove_beneficial_genetic_traits` to permit the original tradition path OR the conjunction of player country, `tech_gene_expressions`, and the active modifier. Removing the modifier withdraws this additional permission; the technology is not granted automatically.
- Added overrides of the Tass main event and modifier file, plus the vanilla trigger file with only the specified definition changed. Envoys and other menu options are preserved. Added three keys per language referencing existing technology and archetype names.
- Passed checks for 256 condition combinations, six bonuses, button visibility and transitions, references, encoding, and distribution contents. Preserved the other 49 vanilla triggers, 106 previous runtime files, and researched sources. Added four glossary terms and eight sources without duplicates; updated bilingual specifications, README files, and override inventories.
- Updated the version, archive, and connected copy to 0.0.6 with 112 runtime files. Playsets are unchanged. The user must test actual limits, button changes, Quick Learners removal under the combined condition, retained tradition permission, and templates after disabling the cheat in-game.

## Draft specification: species modification — 2026-11-15

- Prepared a bilingual [draft specification](TZ_SPECIES_EN.md) from the user's requirements: +100 trait points and +30 picks for biological species, robots, and machines; the button offers removal while the modifier is active.
- Researched beneficial trait removal checks: general permission depends on traditions, while the separate vocational trait check depends on `tech_gene_expressions`. Recorded definitions, terminology sources, and fingerprints.
- Approval is pending. The version remains 0.0.5; runtime files and the installation are unchanged. Trait removal permission changes and new envoy behavior are excluded from the draft.

## 0.0.5 — 2026-11-15

- Implemented the approved resource menu specification: six categories and 26 amount menus with 156 grant buttons, six amounts per resource. Influence, Minor Artifacts, and Astral Threads use the approved smaller scales.
- Each one-time grant reopens the same amount menu. Back returns one level toward the main cheat menu. Preserved nine Tass availability conditions; storage capacities remain unchanged.
- Overrode resource event `tass_cheat.4`, added 32 new events and 224 keys per language. Preserved 94 policy files and all eight existing localization files; increased the manifest version to 0.0.5.
- Passed checks for every grant, transition, condition, structure, reference, grammatical metadata, and encoding. All 134 researched Tass files retain their fingerprints. Added Biomass and 12 sources to the glossary without duplicate terms; updated bilingual documentation and change inventories.
- Updated the archive and connected local copy to 107 runtime files. Playsets remain unchanged. Window rendering, repeated grants, and actual resource behavior at full storage require user testing in-game.

## Draft specification: resource menu — 2026-11-14

- Inspected the Tass resource event, main-menu entry, conditions of 26 grants, and vanilla resource definitions; recorded fingerprints and terminology sources.
- Prepared a bilingual [draft specification](TZ_RESOURCES_EN.md): six categories, a separate menu for each resource, six amounts, and return to the same menu after granting resources. The standard scale was specified by the user; smaller Influence, Minor Artifact, and Astral Thread scales are proposed for approval.
- The draft preserves nine availability conditions and specifies 156 grant buttons with checks for all transitions. The version remains 0.0.4; runtime files and the connected installation are unchanged.

## 0.0.4 — 2026-11-14

- Extended 94 policies under the approved specification: ten regular levels each and ten monthly levels in 18 resource policies. Added 629 options, bringing the total to 1214 including neutral options.
- Each new level doubles all numeric modifiers of the preceding level in its track, including negative modifiers. Preserved all 585 original options, values, and conditions; new options inherit their own track's restrictions.
- Added 94 Tass file overrides and two localization files with 1258 new keys each, in Russian and English. Preserved all 1667 existing Russian values and precursor fixes. New descriptions follow code; new emergency retreat descriptions distinguish damage risk from waiting time.
- Passed checks for structure, ordering, 1200 numeric components, inherited conditions, original blocks and strings, references and grammatical metadata, encodings, and distribution contents. Updated bilingual specifications, README, changelog, and affected-definition inventories.
- Increased the version to 0.0.4. The archive and connected local copy contain 103 runtime files. Playsets, game files, and Workshop files remain unchanged. The user must check new-level loading and practical effects of extreme modifiers in-game.

## Draft specification: 10 levels — 2026-11-14

- The user confirmed preserving existing levels and extending both regular and monthly tracks to ten levels.
- Rechecked 94 policies and 112 tracks. Prepared a separate [draft specification](TZ_LEVELS_EN.md) proposing doubled modifiers at each new level; identified 20 policies with negative modifiers.
- The draft awaits agreement on progression and approval. The runtime remains 0.0.3; code, localization, and the installed copy are unchanged.

## 0.0.3 — 2026-11-14

- At the user's request, shortened four authored planetary decision descriptions to one sentence of at most 12 words after reference expansion. Detailed tooltips are preserved.
- Updated both specification and README versions, build materials, and description evidence. The set of affected vanilla keys is unchanged.
- Checked description length against both Russian baselines, localization formatting, and preservation of the other 1663 values relative to 0.0.2.
- Increased the version to 0.0.3 and updated the archive and local installation without changing playsets. In-game display remains for the user to verify.

## 0.0.2 — 2026-11-14

- Investigated grammatical metadata exposed on five precursor selection buttons in the user's screenshot. Direct `$..._precursor_civ$` expansion included declension forms supplied by Russian Localization Fix RE.
- Replaced five references with existing screen titles: `precursor.1.name`, `precursor.500.name`, `precursor.1000.name`, `precursor.1500.name`, and `precursor.2000.name`. Translations are not duplicated; event code and global definitions remain unchanged.
- Added recursive detection of `&!` and `|||` outside dynamic expressions. The regression check identifies five defective entries in the previous version and none in the fix, using both vanilla and Russian Localization Fix RE sources.
- Updated the specification, README, and shared-key documentation. Runtime contents remain 1,667 entries in seven files.
- Increased the version to 0.0.2 and updated the archive and local installation without changing playsets. Synthetic checks passed; in-game verification of the startup window remains pending.

## 0.0.1 — 2026-11-14

- Implemented Russian localization of Tass Cheat Tool version `20261012` after approval of the extended specification: 1,667 keys in six files, including translation of 729 original values containing text.
- Authored 704 descriptions from code: 13 categories, 94 policies, 585 options, 4 decisions, 7 edicts, and 1 colony deposit. Retained the two approved empty entries.
- Descriptions account for percentage and flat bonuses, monthly timing, DLC and empire conditions, pause flags, buildings, and traditions. Recorded verifiable sources for constants and references; existing dynamic expressions remain unchanged.
- Preserved key order, entry formatting, control tokens, original numbers, UTF-8 BOM, and line endings. Corrected the `mod_fleet_command_limit_add` reference and added `TASS_CHEAT_WORMHOLE`.
- Created the `0.0.1` manifest with `supported_version="v4.5.*"` and the Tass Cheat Tool dependency. Gameplay logic is unchanged.
- Added 55 terms to the shared glossary in `Glossary/tcte_terms.json` without duplicating existing terms. Updated the specification, the list of 54 shared keys, and both README languages.
- Prepared a seven-file runtime distribution and `TMP/TCTE/TCTE_0.0.1.zip`. Installed the mod through the Stellaris user directory without changing playsets.
- Passed synthetic checks for localization, descriptions, references, glossary, documentation, and installed-file identity. All 134 Workshop source files retained their fingerprints. In-game testing remains the user's responsibility.
- Recorded source label/code discrepancies for the crime policy and infrastructure in the README; their behavior was not corrected as part of localization.

## Specification extension: descriptions and substitutions — 2026-11-14

- At the user's request, extended the draft specification to fill 704 empty descriptions from active code: 13 categories, 94 policies, 585 options, 4 decisions, 7 edicts, and 1 colony deposit.
- Confirmed that `edict_tass_edict_cheat_test_desc` belongs to a commented-out edict and no uses of `NAME_leader_tass` were found; these two entries remain empty.
- Required reuse of terms through localization references and display of variable values through available substitutions. Added the rule to `AGENTS.md` as well.
- Added checks for conditions, magnitudes, timing, and scopes, three sample descriptions, and a preliminary source mapping in `TMP/TCTE/description_sources.json`.
- Kept both specification languages consistent and updated validation criteria. Key count and distribution contents are unchanged; no runtime files have been created. The revised specification awaits approval.

## Specification preparation — 2026-11-14

- Prepared Russian and English draft specifications for localizing Tass Cheat Tool as part of TCTE.
- Inspected version `20261012`, its five English files containing 1,666 keys, and the absence of Russian localization; confirmed 94 policies in 13 categories.
- Included correction of one missing reference and addition of one missing key in the draft scope: 1,667 Russian entries are planned.
- Checked core game terminology against preferred Russian sources and the existing glossary; no new glossary entries have been created yet.
- Created a separate list of 54 planned shared keys, including 32 overlaps with explicit vanilla definitions.
- Saved audit materials and source fingerprints under `TMP/TCTE/`.
- The specification awaits user approval. No runtime files, manifest, translation, or mod installation have been created; version `0.0.1` is planned for the first implementation.
