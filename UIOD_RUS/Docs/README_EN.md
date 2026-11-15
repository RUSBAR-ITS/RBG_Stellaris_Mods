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

Version **0.0.3** for Stellaris **4.5.***. The mod completes the Russian localization of UI Overhaul Dynamic and UI Overhaul Dynamic - Ascension Slots with 12 and 7 strings respectively. Select Russian as the game language.

More Tradition Categories (80), Tiny Options, and Tiny Outliner need no separate translations: their inspected versions contain no localization files of their own. Original mod and service names are preserved as proper names where appropriate; the Steam Workshop label is translated as “Мастерская Steam”.

## Distribution contents

The game distribution contains only three files:

- `descriptor.mod`;
- `localisation/replace/uiod_rus_ui_overhaul_l_russian.yml`;
- `localisation/replace/uiod_rus_ascension_slots_l_russian.yml`.

Archive: [UIOD_RUS_0.0.3.zip](../../TMP/UIOD_RUS/UIOD_RUS_0.0.3.zip). It contains a `UIOD_RUS` directory with these files. Documentation, the glossary, and temporary materials are excluded.

## Installation

1. Install and enable UI Overhaul Dynamic and UI Overhaul Dynamic - Ascension Slots.
2. Place the distributed `UIOD_RUS` directory under `Documents/Paradox Interactive/Stellaris/mod/`. On this computer the destination is `C:/Users/RUSBAR/Documents/Paradox Interactive/Stellaris/mod/UIOD_RUS/`.
3. In the parent `mod/` directory, create `UIOD_RUS.mod` containing the contents of `descriptor.mod` plus `path="C:/Users/RUSBAR/Documents/Paradox Interactive/Stellaris/mod/UIOD_RUS"`. On another computer, use its actual absolute path with forward slashes.
4. Restart the launcher. To play, the user manually adds **UI Overhaul Dynamic - Russian Localization Fix** to the desired playset and enables it. Place it below UI Overhaul Dynamic and Ascension Slots; for the five-mod UIOD series, it can be placed after the entire series.
5. Select Russian and start the game with that playset.

Do not install UIOD_RUS into the game installation or Steam Workshop directories. Do not copy the working `Docs` directory or shared glossary into the game distribution.

## In-game testing

The user checks:

- the UIOD information window: version, main text, Steam and Discord labels and tooltips;
- the additional technology tree tooltip;
- tooltips for moving windows and moving list entries to the top or bottom;
- the repeatable ascension technology name;
- the Ascension Slots setup dialog: title, description, and technology opt-out;
- the Ascension Slots information dialog: title, counters, and continue button.

Check version and number substitutions, color emphasis, the mouse icon, line breaks, readability at the chosen UI scale, and text clipping. File validation is sufficient for the Open Beta string if the current UIOD version does not display it. There is no need to modify a save just to invoke an unused screen.

## File validation

Synthetic validation results: [validation_report.json](../../TMP/UIOD_RUS/validation_report.json). Validation compares all 19 entries against their source strings and the approved specification: keys, entry structure, control tokens, numbers, encoding, line endings, the glossary, and archive contents.

Glossary: [uiod_rus_terms.json](../../Glossary/uiod_rus_terms.json). It contains 6 unique terms with 20 references to English originals and Russian sources. It is a working translation glossary rather than a game file.

In-game testing has not been performed automatically; successful file validation does not replace it.

## Known limitation

The upstream UIOD key `UIO_FAVORS_TITLE` references the missing `TRADE_CATEGORY_FAVORS` key. This is a separate upstream localization defect. Version 0.0.3 leaves it unchanged as specified in the approved scope.

## Documentation

- [Approved specification](TZ_EN.md).
- [Changelog](CHANGELOG_EN.md).
- [Affected vanilla files and functions](VANILLA_CHANGES_EN.md).
- [Русская инструкция](README_RU.md).
