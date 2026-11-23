# PDE 2.0.4 directory and file layout

## Contents

- [Mod root](#mod-root)
- [Game files](#game-files)
- [How one deposit appears in both menus](#how-one-deposit-appears-in-both-menus)
- [Parts of a deposit button](#parts-of-a-deposit-button)
- [Action rules](#action-rules)

## Mod root

The mod root is `PDE/`. It contains the descriptor, thumbnail and decision icon. The release fields are `version="2.0.4"` and `supported_version="v4.6.*"`. The verification baseline is Stellaris 4.6.0. New game keys use the existing `cdpd_` prefix and events use the `CDPD` namespace. [Current descriptor](../../PDE/descriptor.mod) · [PDE events](../../PDE/events/cdpd_menu_events.txt)

Project documents live in `docs/PDE/`, including requirements, classification, the warning register and the changelog. This directory also contains the [2.0.0 specification](TZ_EN.md) and the [vanilla files and functions register](VANILLA_CHANGES_EN.md). Research data and individual run outputs live in `TMP/PDE/<game version>/`. PDE embeds the RB_SDM menu under its own identifiers. Players install PDE as a standalone mod. [Requirements](REQUIREMENTS_EN.md) · [RB_SDM guide](../../RB_SDM/README_EN.md#copy-a-section-into-your-mod)

## Game files

The tree shows the release contents. The `catalog/` subtree includes one leaf section as an example. The menu structure defines the screen and folder order. A single action list can include multiple catalog files. [PDE menu structure](MENU_STRUCTURE_EN.md)

```text
PDE/
├── descriptor.mod
├── thumbnail.png
├── common/
│   ├── decisions/
│   │   └── cdpd_decisions.txt
│   ├── scripted_triggers/
│   │   ├── cdpd_access_triggers.txt
│   │   ├── cdpd_placement_triggers.txt
│   │   └── cdpd_menu_triggers.txt
│   ├── scripted_effects/
│   │   ├── cdpd_menu_effects.txt
│   │   └── cdpd_deposit_effects.txt
│   └── inline_scripts/cdpd/
│       ├── menu/
│       │   ├── cdpd_rank.txt
│       │   ├── cdpd_option.txt
│       │   ├── cdpd_option_preview.txt
│       │   ├── cdpd_deposit_button.txt
│       │   ├── cdpd_section_option.txt
│       │   ├── cdpd_navigation.txt
│       │   ├── cdpd_root_navigation.txt
│       │   ├── cdpd_close.txt
│       │   └── cdpd_clear_rank.txt
│       └── catalog/
│           ├── cdpd_all.txt
│           ├── cdpd_remove_only.txt
│           └── orbital/cdpd_energy.txt
├── events/
│   ├── cdpd_menu_events.txt
│   ├── cdpd_add_events.txt
│   └── cdpd_remove_events.txt
├── gfx/interface/icons/decisions/
│   └── decision_cdpd_editor.dds
└── localisation/
    ├── russian/
    │   ├── cdpd_menu_l_russian.yml
    │   └── cdpd_deposits_l_russian.yml
    └── english/
        ├── cdpd_menu_l_english.yml
        └── cdpd_deposits_l_english.yml
```

| Files | Responsibility |
| --- | --- |
| `cdpd_decisions.txt`, `cdpd_access_triggers.txt` | Planetary decision, access within borders and a player-only initiator check. The decision saves the selected body and hands control to an event for the acting country, `from`. An owned colony and an uncolonized body in owned space use the standard interface. Vanilla restricts access to foreign colonies, including pre-FTL colonies in owned space. [PDE decision](../../PDE/common/decisions/cdpd_decisions.txt) · [Game rule](E:/SteamLibrary/steamapps/common/Stellaris/common/game_rules/00_rules.txt:4698) |
| `cdpd_placement_triggers.txt`, `cdpd_menu_triggers.txt` | The former defines valid placement targets, including body type, class and climate. The latter shows a section when at least one descendant is available. A removal entry requires only the presence of its ID on the selected body. |
| `cdpd_menu_events.txt`, `cdpd_add_events.txt`, `cdpd_remove_events.txt` | Entry, session and main menu, placement section screens, and one flat screen for the top-level “Remove deposits” entry. Next and previous pages reuse the current list event. |
| `cdpd_menu_effects.txt`, `inline_scripts/cdpd/menu/` | Count available entries in catalog order, assign positions, display pages, navigate and clean up the session. A section button opens the child screen on its first page. A deposit button applies the operation and refreshes the list. After an action, recheck the availability of the current section and its parents. |
| `cdpd_deposit_effects.txt` | Place and directly remove the selected instance and maintain required modifiers and counters. This file handles ID-specific behavior, including the `d_titanic_life_blocker` and `titanic_life` pair. |
| `cdpd_menu_l_*.yml`, `cdpd_deposits_l_*.yml` | The first file in each language covers the decision, sections and navigation. The second covers action labels and tooltips referencing game localization keys for names and descriptions. A flagged action starts with a red warning, followed by a blank line, the name and the full description. [Warning register](QUEST_TOOLTIP_WARNINGS_EN.md) |

## How one deposit appears in both menus

For example, `d_energy_3` has one entry in `orbital/cdpd_energy.txt`. It specifies the ID, placement rule, tooltip for each action and any special handling. Its position determines its order under “Orbital deposits → Energy Credits”. The section uses the same list to count available entries and to display them. If no energy deposit is eligible on this body, the Energy Credits entry is hidden.

For removal, `cdpd_all.txt` includes the same leaf catalogs in sequence, followed by `cdpd_remove_only.txt`. The player sees only IDs already present on the selected body. This makes `d_energy_3` removable even on a colonizable world, and the excluded `d_arc_furnace_1` available for removal only. Each ID has one entry across the source lists. Coverage is 529 IDs for placement and 592 for removal. The 63 IDs in `cdpd_remove_only.txt` include `d_astral_threads_deposit_2` and `d_crystal_rift`. The internal `d_null_deposit` is counted separately. [Classification and exclusions](DEPOSIT_CLASSIFICATION_EN.md)

## Parts of a deposit button

For `d_energy_3`, the binding belongs in `PDE/common/inline_scripts/cdpd/catalog/orbital/cdpd_energy.txt`. One deposit ID has two actions. The catalog entry supplies the appropriate `LABEL`, `TIP`, `VISIBLE` and `ACTION` to the template for the placement or removal screen. The keys below are present in 2.0.0. [PDE energy catalog](../../PDE/common/inline_scripts/cdpd/catalog/orbital/cdpd_energy.txt) · [RB_SDM option template](../../RB_SDM/mod/common/inline_scripts/rb_sdm/rb_sdm_option.txt)

| Button field | Place `d_energy_3` | Remove `d_energy_3` |
| --- | --- | --- |
| `LABEL` — button text | `cdpd_add_energy_3_label` | `cdpd_remove_energy_3_label` |
| `TIP` — text on hover | `cdpd_add_energy_3_tip` | `cdpd_remove_energy_3_tip` |
| `VISIBLE` — when to show it | The selected body is eligible for this orbital deposit | The selected body has `d_energy_3` |
| `ACTION` — what a click does | Add one instance of `d_energy_3` to the selected body | Remove one instance of `d_energy_3` from the selected body |

**Player-facing text.** English button labels and full tooltips for both actions belong in `PDE/localisation/english/cdpd_deposits_l_english.yml`. The Russian values for the same keys belong in `PDE/localisation/russian/cdpd_deposits_l_russian.yml`. Each language file contains two shared warning keys, one per operation. Seven IDs have no game description in either language. For those IDs, PDE displays the monthly station output from the deposit definition. A tooltip references the appropriate warning when the register flags that action. Section names and navigation labels belong in the corresponding `cdpd_menu_l_english.yml` and `cdpd_menu_l_russian.yml` files.

In the English example below, `$d_energy_3$` supplies the game’s deposit name and `$d_energy_3_desc$` supplies its description. The register flags only removal for this ID. [Game keys](E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/megacorp_l_english.yml:2799) · [Reason for the warning](QUEST_TOOLTIP_WARNINGS_EN.md#removal-button)

```yaml
l_english:
 cdpd_add_energy_3_label: "Add $d_energy_3$"
 cdpd_remove_energy_3_label: "Remove $d_energy_3$"
 cdpd_remove_quest_warning: "§RWARNING!!! Removing this deposit may disrupt a quest already in progress!§!"
 cdpd_add_energy_3_tip: "$d_energy_3$\n$d_energy_3_desc$"
 cdpd_remove_energy_3_tip: "$cdpd_remove_quest_warning$\n\n$d_energy_3$\n$d_energy_3_desc$"
```

The 529 placement options use the preview in `cdpd_option_preview.txt`. The 592 removal options use property lines from the deposit localization. Both share the click handler in `cdpd_deposit_button.txt`. [Tooltip specification](TZ_TOOLTIP_EFFECTS_EN.md)

**Executing the action.** The shared `common/inline_scripts/cdpd/menu/cdpd_option.txt` template displays the label and tooltip. On a click, it rechecks availability and invokes the action on the saved body. Placement conditions belong in `common/scripted_triggers/cdpd_placement_triggers.txt`. Placement, direct removal and required modifier handling belong in `common/scripted_effects/cdpd_deposit_effects.txt`.

## Action rules

Only a player can take the decision. Placement checks the selected body. Empire type and the existing instance count do not restrict placement. Each click adds or removes one instance. The deposit effect maintains shared modifiers and counters. [2.0.0 specification](TZ_EN.md#instances-and-planet-state)
