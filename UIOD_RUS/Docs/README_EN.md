# UI Overhaul Dynamic - Russian Localization Fix

## Contents

- [Purpose](#purpose)
- [Distribution contents](#distribution-contents)
- [Installation](#installation)
- [In-game testing](#in-game-testing)
- [File validation](#file-validation)
- [Known limitation](#known-limitation)
- [Documentation](#documentation)

## Purpose

Mod ID: `UIOD_RUS`. Display name: **UI Overhaul Dynamic - Russian Localization Fix**.

Version **0.0.4** targets Stellaris `v4.6.*`. UIOD_RUS patches the Instrument of Desire aura and the Ascension Slots repeatable technology in all interface languages. Selecting Russian also enables 12 UI Overhaul Dynamic translations and 7 Ascension Slots translations.

More Tradition Categories (80), Tiny Options, and Tiny Outliner need no separate translations: their inspected versions contain no localization files of their own. Original mod and service names are preserved as proper names where appropriate; the Steam Workshop label is translated as “Мастерская Steam”.

## Distribution contents

The distribution contains six game files.

- `descriptor.mod`
- `common/scripted_effects/uiod_psionic_auras_scripted_effects.txt`
- `common/script_values/uiod_rus_ascension_values.txt`
- `common/technology/ui_tech_ascension_theory_repeatable.txt`
- `localisation/replace/uiod_rus_ui_overhaul_l_russian.yml`
- `localisation/replace/uiod_rus_ascension_slots_l_russian.yml`

Archive: [UIOD_RUS_0.0.4.zip](../../TMP/UIOD_RUS/UIOD_RUS_0.0.4.zip). It contains a `UIOD_RUS` directory with these files. Documentation, the glossary, and temporary materials are excluded.

## Installation

1. Install and enable UI Overhaul Dynamic and UI Overhaul Dynamic - Ascension Slots.
2. On the development machine, the launcher reads the mod directly from `D:/Repos/RBG_Stellaris_Mods/UIOD_RUS`. For an archive installation, extract the `UIOD_RUS` directory under `Documents/Paradox Interactive/Stellaris/mod/`.
3. Save `UIOD_RUS.mod` in the user’s `mod/` directory with the contents of `descriptor.mod` and a `path` entry pointing to the actual mod directory. The development machine uses `path="D:/Repos/RBG_Stellaris_Mods/UIOD_RUS"`.
4. Restart the launcher. To play, the user manually adds **UI Overhaul Dynamic - Russian Localization Fix** to the desired playset and enables it. Place it below UI Overhaul Dynamic and Ascension Slots; for the five-mod UIOD series, it can be placed after the entire series.
5. Launch the game. Select Russian to check the translated strings.

Do not install UIOD_RUS into the game installation or Steam Workshop directories. Do not copy the working `Docs` directory or shared glossary into the game distribution.

## In-game testing

Set the limit above 10 and verify that the aura raises a planet and an arkship from tier 10 to 11. Read the actual colony tier. Repeat at the configured limit and during the ten-year cooldown. Check that the Ascension Slots option controls technology availability, that research grants one slot, and that `error.log` no longer reports `ai_update_type` for this file. [Full acceptance scenarios](TZ_ASCENSION_SLOTS_46_EN.md#verification-and-acceptance).

Check the following items in Russian.

- the UIOD information window: version, main text, Steam and Discord labels and tooltips;
- the additional technology tree tooltip;
- tooltips for moving windows and moving list entries to the top or bottom;
- the repeatable ascension technology name;
- the Ascension Slots setup dialog: title, description, and technology opt-out;
- the Ascension Slots information dialog: title, counters, and continue button.

Check version and number substitutions, color emphasis, the mouse icon, line breaks, readability at the chosen UI scale, and text clipping. File validation is sufficient for the Open Beta string if the current UIOD version does not display it. There is no need to modify a save just to invoke an unused screen.

## File validation

The 0.0.4 checks cover script syntax, differences from source, tier conditions and distribution contents. [0.0.4 report](../../TMP/UIOD_RUS/validation_0.0.4.json). The original translation checks are documented separately. [0.0.3 report](../../TMP/UIOD_RUS/validation_report.json).

Glossary: [uiod_rus_terms.json](../../Glossary/uiod_rus_terms.json). It contains 6 unique terms with 20 references to English originals and Russian sources. It is a working translation glossary rather than a game file.

In-game testing has not been performed automatically; successful file validation does not replace it.

## Known limitation

The upstream UIOD key `UIO_FAVORS_TITLE` references the missing `TRADE_CATEGORY_FAVORS` key. This is a separate upstream localization defect.

## Documentation

- [Localization specification](TZ_EN.md).
- [Stellaris 4.6 phase-one specification](TZ_ASCENSION_SLOTS_46_EN.md).
- [Changelog](CHANGELOG_EN.md).
- [Affected vanilla files and functions](VANILLA_CHANGES_EN.md).
- [Русская инструкция](README_RU.md).
