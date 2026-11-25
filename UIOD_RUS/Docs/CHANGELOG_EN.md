# UIOD_RUS — changelog

## Contents

- [0.0.4 (2026-11-25)](#004-2026-11-25)
- [Ascension Slots patch proposal](#ascension-slots-patch-proposal)
- [0.0.3 (2026-11-14)](#003-2026-11-14)
- [0.0.2 (2026-11-14)](#002-2026-11-14)
- [0.0.1 (2026-11-14)](#001-2026-11-14)
- [Specification preparation — 2026-11-14](#specification-preparation--2026-11-14)

## 0.0.4 (2026-11-25)

- Updated the supported game version to `v4.6.*`.
- The launcher descriptor `mod/UIOD_RUS.mod` loads version `0.0.4` for `v4.6.*` directly from `D:/Repos/RBG_Stellaris_Mods/UIOD_RUS`. The former `0.0.3` copy and its launcher descriptor are backed up in `TMP/UIOD_RUS/before_repo_connection_0.0.3/`.
- An Instrument of Desire surge raises an eligible planet or arkship by one tier up to the Ascension Slots limit. Restored the vanilla ten-year cooldown per colony and notification routing to the aura owner.
- Removed the obsolete `ai_update_type = all` field from the repeatable Ascension Slots technology. Each completion still grants one ascension perk slot.
- Packaged three scripts with the existing translations. Badges for tiers above 10 are deferred pending a separate decision.

## Ascension Slots patch proposal

Drafted the [Stellaris 4.6 patch specification](TZ_ASCENSION_SLOTS_46_EN.md) for the Instrument of Desire aura and the repeatable technology.
Added exact colony tier badges up to tier 100 and an in-game check of frame selection beyond tier 10 to the proposal.

## 0.0.3 (2026-11-14)

- Adopted `supported_version="v4.5.*"` with the mandatory `v` prefix following the user's clarification; propagated the working manifest correction to the installed copy and launcher descriptor.
- Updated the specification, bilingual documentation, manifest validation, and distribution archive. Added the format rule to `AGENTS.md`.
- Automatically incremented the version to `0.0.3`. Translations and dependencies are unchanged; the playset was not modified.

## 0.0.2 (2026-11-14)

- At the user's request, changed the display name to `UI Overhaul Dynamic - Russian Localization Fix`; retained `UIOD_RUS` as the ID, directory name, and launcher descriptor basename.
- Updated the manifest, installed copy, launcher descriptor, distribution archive, specification, and bilingual documentation.
- Automatically incremented the version to `0.0.2`. Translations and dependencies are unchanged; the playset was not modified.

## 0.0.1 (2026-11-14)

- Received specification approval and marked both language versions as approved.
- Created the UIOD_RUS manifest for Stellaris 4.5.* with dependencies on UI Overhaul Dynamic and Ascension Slots.
- Added 19 approved translations: 12 for UIOD and 7 for Ascension Slots, in separate `localisation/replace/` files.
- Preserved original keys, entry structure, control tokens, escaping, UTF-8 BOM, and LF line endings.
- Created a glossary containing 6 unique terms with 20 supporting source references.
- Added bilingual installation and testing instructions and a separate list of affected vanilla files and functions.
- Prepared a game distribution containing the manifest and two localization files; working materials are excluded.
- Copied the mod to the Stellaris user mod directory and created the `UIOD_RUS.mod` launcher descriptor; installed files were verified against the source files. The user still needs to enable the mod in a launcher playset.
- In-game testing remains the user's responsibility; synthetic validation results are recorded in `TMP/UIOD_RUS/validation_report.json`.

## Specification preparation — 2026-11-14

- Prepared Russian and English draft specifications with 19 proposed translations.
- Defined requirements for preserving source formatting, terminology, the glossary, and validation.
- Inspected installed UIOD and Ascension Slots sources, the game version, and terminology sources.
- During this iteration, the specification was awaiting approval; no game files for the mod had been created and no mod version had been released.
