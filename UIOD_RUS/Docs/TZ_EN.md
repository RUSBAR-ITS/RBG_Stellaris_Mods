# UIOD_RUS — technical specification

Status: approved by the user on 2026-11-14. Implementation is authorized within this specification.

## Contents

- [1. Purpose](#1-purpose)
- [2. Scope](#2-scope)
- [3. Implementation](#3-implementation)
- [4. Preserve string formatting](#4-preserve-string-formatting)
- [5. Terminology and glossary](#5-terminology-and-glossary)
- [6. Approved translations](#6-approved-translations)
- [7. Deliverables](#7-deliverables)
- [8. Validation and acceptance](#8-validation-and-acceptance)
- [9. Sources](#9-sources)

## 1. Purpose

Create a separate mod with the ID `UIOD_RUS` and the display name `UI Overhaul Dynamic - Russian Localization Fix` to translate the remaining English strings in UI Overhaul Dynamic and UI Overhaul Dynamic - Ascension Slots when the game language is Russian. The name was updated at the user's explicit request; the ID, directory name, and launcher descriptor filename remain unchanged.

Installed game: Stellaris Cygnus v4.5.4 (1b4f), as recorded in `launcher-settings.json`. Set `supported_version="v4.5.*"` in the manifest and launcher descriptor: the `v` prefix is required by the user's clarification. Initial mod version: `0.0.1`; version after the name change: `0.0.2`; version after correcting the `supported_version` format: `0.0.3`.

## 2. Scope

Translate 19 existing keys: 12 from the main UIOD mod and 7 from Ascension Slots. These comprise the 18 untranslated strings identified by the audit plus the `Steam Workshop` label, translated as “Мастерская Steam”.

More Tradition Categories (80), Tiny Options, and Tiny Outliner do not provide their own localization files. Their vanilla keys and original GUI placeholders remain unchanged.

Preserve UI Overhaul Dynamic, UI Overhaul Dynamic - Ascension Slots, Gigastructural Engineering, Stellaris, Discord, Steam, Paradox Interactive, GitHub, Xelnath, and EHOF as proper names. Do not rewrite existing Russian translations, numeric options, or strings containing only substitutions.

The audit identified the broken reference `UIO_FAVORS_TITLE` → `$TRADE_CATEGORY_FAVORS$`. Fixing it changes an original control token and requires separate approval; it is outside this translation task.

## 3. Implementation

Place the mod in `UIOD_RUS/`. Use separate Russian key override files under `localisation/replace/`:

- `uiod_rus_ui_overhaul_l_russian.yml` — 12 main UIOD keys;
- `uiod_rus_ascension_slots_l_russian.yml` — 7 Ascension Slots keys.

File names use the new mod prefix `uiod_rus_`. Keys inside the files retain their original names because they override existing strings rather than introduce new identifiers.

Create `descriptor.mod` with the name `UI Overhaul Dynamic - Russian Localization Fix`, version `0.0.3`, the target game version, and dependencies on UI Overhaul Dynamic and UI Overhaul Dynamic - Ascension Slots. Load UIOD_RUS after those mods. Dependencies on the other three UIOD mods are unnecessary.

The mod contains localization and metadata only. Game and Workshop source files are read-only; GUI definitions, events, technologies, and balance are unchanged.

## 4. Preserve string formatting

Change only the translatable text inside each value. For each entry preserve:

- the original key, capitalization, colon, presence or absence of a numeric index after the colon, indentation, and quotation marks;
- the exact content, count, and order of control tokens: `$...$`, `[...]`, `§H`, `§G`, `§!`, `£...£`, and any other codes present;
- literal `\n` sequences, their count, and the allocation of content to the original UI lines;
- `$UI_OVERHAUL_VERSION$`, `$tech_ascension_theory$`, and all expressions involving `global_event_country` and `This`;
- numbers in prose, including the limit of 100, and the meaning of color emphasis.

Do not expand substitutions manually. Do not replace `\n` with physical line breaks inside a value or convert it to `\\n`. Each localization entry occupies one physical line.

Save the files as UTF-8 with BOM, with the `l_russian:` header and the `_l_russian.yml` filename suffix. Use LF line endings, matching the inspected UIOD sources. Validate the structure around each value separately from its translated content.

## 5. Terminology and glossary

Find English terms in the installed game's localization, then match Russian entries by key. Source priority: `Localisation_Base/1-Prio_Russian_Localization_Fix_RE/replace/`, the other Russian Localization Fix RE texts, then `Localisation_Base/2-Prio_Vanilla/`.

Verified terminology for this task:

| English term | Russian equivalent | Source keys |
| --- | --- | --- |
| Ascension Theory | Теория вознесения | `tech_ascension_theory` |
| Ascension Perks | Бонусы за стремление | `ASCENSION_PERKS`, `TUTORIAL_ASCENSION_PERKS_DESC` |
| Ascension Perk Slot | Ячейка бонусов за стремление | `TUTORIAL_ASCENSION_PERKS_DESC`, `NUM_ASCENSION_PERK_SLOTS_TRIGGER` |
| Traditions | Традиции | `TRADITIONS` |
| Tradition Categories | Категории традиций | `TRADITION_COST_MULT_NUM_GROUPS`, `NUM_TRADITION_CATEGORIES` |
| Repeatable Technology | Повторяющаяся технология | `exploration.400.hint`, `NUM_REPEATABLE_TECHS_TRIGGER` |

No definitions of these keys were found under `replace`; the next-priority Russian Localization Fix RE texts were used and corroborated against vanilla localization.

During implementation, add these terms to `Glossary/uiod_rus_terms.json` or extend existing entries in the shared glossary. Check term uniqueness across the entire `Glossary` directory rather than within a single file.

Each entry contains `english`, `russian`, `sources`. The `sources` array records keys and paths for supporting English and Russian strings, including the priority of the Russian source. One term has one entry; different sources and grammatical forms do not create duplicate terms.

## 6. Approved translations

The table contains the approved Russian values. A backslash followed by n represents the original `\n` sequence, not a physical line break.

| Original key | Approved Russian value |
| --- | --- |
| `UI_OVERHAUL_BETA` | `$UI_OVERHAUL_VERSION$ Открытая бета-версия` |
| `UI_OVERHAUL_INFO` | `Открывает окно информации о моде` |
| `UI_OVERHAUL_STEAM` | `Мастерская Steam` |
| `UI_OVERHAUL_DISCORD` | `Сервер Discord` |
| `UI_OVERHAUL_DISCORD_TOOLTIP` | `Открывает сервер мода в Discord` |
| `UI_OVERHAUL_TEXT_TOP` | `Этот мод обновлён для версии §H$UI_OVERHAUL_VERSION$§! Stellaris. Он должен работать с последующими исправлениями этой версии, если не указано иное.` |
| `UI_OVERHAUL_TEXT_CENTER` | `Об ошибках, замечаниях и вопросах можно сообщить на моём сервере Discord. Я открыт для предложений по изменению пользовательского интерфейса.` |
| `UI_OVERHAUL_TEXT_BOTTOM` | `Если вы используете §HGigastructural Engineering§!, обязательно установите патч совместимости, иначе вы не сможете использовать EHOF.\nПатч можно найти на странице мода в Мастерской Steam.` |
| `UI_OVERHAUL_TECHTREE_TOOLTIP_DELAYED` | `Это дерево технологий не связано с §HParadox Interactive§!, не одобрено компанией и не является её официальным проектом.\nЭто любительский проект, который поддерживает §HXelnath§! на GitHub.` |
| `UIO_MOVE_TO_TOP` | `§HВ начало§!\nПереместить в самое начало списка` |
| `UIO_MOVE_TO_BOTTOM` | `§HВ конец§!\nПереместить в самый конец списка` |
| `UIO_MOVEABLE_WINDOW` | `§HЭто окно можно перемещать§!\nНажмите и удерживайте левую кнопку мыши £mouse1£, чтобы переместить его.` |
| `ui_tech_ascension_theory_repeatable` | `$tech_ascension_theory$ (повторяющаяся)` |
| `ui_overhaul_qhd_ascension.10.name` | `UI Overhaul Dynamic - Повторяющаяся технология вознесения` |
| `ui_overhaul_qhd_ascension.10.desc` | `Хотите включить повторяющуюся технологию, открывающую ячейки бонусов за стремление, из мода §HUI Overhaul Dynamic - Ascension Slots§!? Если да, выберите желаемое количество. Это изменение затронет всех игроков, включая ИИ. В указанное число входит ячейка, открываемая технологией вознесения в оригинальной Stellaris.\nСейчас для технологии установлено значение §H[global_event_country.uiod_max_ascension_perk_slots]§!.\nКоличество категорий традиций из дополнительного мода UIOD: §H[global_event_country.uiod_max_tradition_categories]§!.\nЕсли вы увеличиваете количество категорий традиций, некоторые варианты будут недоступны, чтобы общее количество не превысило 100.` |
| `ui_overhaul_qhd_ascension.10.no` | `Я не хочу использовать эту технологию` |
| `ui_overhaul_qhd_ascension.50.name` | `UI Overhaul Dynamic - Информация о бонусах за стремление` |
| `ui_overhaul_qhd_ascension.50.desc` | `Текущее количество: [This.uiod_current_ascension_perk_slots]\nОбщее количество (для всей игры): [global_event_country.uiod_max_ascension_perk_slots]\nКатегории традиций: [global_event_country.uiod_max_tradition_categories]` |
| `ui_overhaul_qhd_ascension.50.a` | `Играем!` |

## 7. Deliverables

Game distribution:

- `UIOD_RUS/descriptor.mod`;
- the two files under `UIOD_RUS/localisation/replace/` listed in section 3.

Working documentation and data:

- this specification: `UIOD_RUS/Docs/TZ_RU.md` and `TZ_EN.md`;
- installation and testing instructions: `UIOD_RUS/Docs/README_RU.md` and `README_EN.md`;
- changelog: `UIOD_RUS/Docs/CHANGELOG_RU.md` and `CHANGELOG_EN.md`, updated after each iteration;
- a separate list of affected vanilla files and functions: `UIOD_RUS/Docs/VANILLA_CHANGES_RU.md` and `VANILLA_CHANGES_EN.md`; explicitly record that this mod's list is empty;
- the JSON glossary in the shared `Glossary/` directory.

Exclude working documentation, the glossary, and validation results from the game distribution. Use `TMP/UIOD_RUS/` for temporary validation work. Connect the mod through Stellaris's user mod directory; do not modify the installed game or Workshop directories.

## 8. Validation and acceptance

Synthetic checks after implementation:

1. The two files contain exactly the 19 unique keys in section 6, split into 12 and 7.
2. Each key has a corresponding source entry in the relevant installed UIOD mod.
3. BOM, language header, filenames, LF endings, quotation marks, and entry structure satisfy section 4.
4. The sequences of substitutions, color codes, icons, and escapes match the original strings exactly.
5. All 19 values contain a Russian translation; retained English proper names do not count as untranslated content.
6. The JSON glossary parses, contains no duplicate terms or source references, and points to existing source files and keys.
7. The manifest matches the specification; the distribution contains only the specified files.
8. Documentation is bilingual and tables of contents match their sections.

The user tests in the game: the UIOD information window, Discord and Steam labels and tooltips, technology tree and window/list movement tooltips, and the Ascension Slots setup and information dialogs. Check version and number substitutions, colors, icons, line breaks, text clipping, and exposed unresolved keys. If the Open Beta string is not currently used by the interface, file validation is sufficient until the relevant screen is available.

Synthetic checks do not imply that in-game testing has been performed. Fixes outside this specification require separate user approval.

## 9. Sources

- Installed UIOD: `E:/SteamLibrary/steamapps/workshop/content/281990/1623423360/`, files `localisation/ui_overhaul_qhd_l_english.yml` and `ui_overhaul_qhd_l_russian.yml`.
- Installed Ascension Slots: `E:/SteamLibrary/steamapps/workshop/content/281990/1890399946/`, files `localisation/ui_overhaul_qhd-technology_l_english.yml` and `ui_overhaul_qhd-technology_l_russian.yml`.
- Original English terms: `E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/`, files `technology_l_english.yml`, `utopia_l_english.yml`, `tutorial_l_english.yml`, `traditions_l_english.yml`, `focus_l_english.yml`, `triggers_effects_l_english.yml`.
- Russian equivalents: corresponding Russian files under `Localisation_Base/1-Prio_Russian_Localization_Fix_RE/russian/` and `Localisation_Base/2-Prio_Vanilla/russian/`.
- The BOM requirement is also documented by the community tool [Intemplator, File formats](https://github.com/TNG-Modding/paradox-gamefiles-templatemaker#file-formats). No dependency on that tool is introduced.
