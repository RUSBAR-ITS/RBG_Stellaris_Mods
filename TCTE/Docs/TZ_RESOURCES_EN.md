# Tass Cheat Tool Extender — resource grant menu specification

## Contents

- [1. Status and request](#1-status-and-request)
- [2. Source baseline](#2-source-baseline)
- [3. Resource categories](#3-resource-categories)
- [4. Grant amounts](#4-grant-amounts)
- [5. Navigation and availability](#5-navigation-and-availability)
- [6. Implementation and localization](#6-implementation-and-localization)
- [7. Validation and acceptance](#7-validation-and-acceptance)

## 1. Status and request

**Approved by the user on 2026-11-15. Implemented in version `0.0.5`. Synthetic checks passed; in-game verification is pending.** This document describes the next stage after the [policy level extension](TZ_LEVELS_EN.md).

The user requested changes to “Planetary decisions → Main cheat menu → Add resources”: introduce categories, individual resources within them, and six amounts for each resource. Granting an amount must reopen the amount menu for **the same resource**. The user specified `1000`, `5000`, `10000`, `50000`, `100000`, `1000000` for the standard scale and requested smaller scales for resources with limited storage.

The user approved the category composition and three smaller scales below.

## 2. Source baseline

The base mod is Tass Cheat Tool, Workshop ID `682851228`, version `20261012`, located at `E:/SteamLibrary/steamapps/workshop/content/281990/682851228/`. The target game version is `v4.5.*`, as specified by the TCTE manifest. Game and Workshop directories are read-only.

Inspected sources:

- `events/tass_cheat_events_1_country.txt`: main menu `tass_cheat.1` opens `tass_cheat.4` through `tass_cheat.1.add_resources`;
- `events/tass_cheat_events_4_resources.txt`: event `tass_cheat.4` contains 26 resource grants and a return to the main menu; each grant calls `add_resource` and reopens the event;
- the installed game's `common/strategic_resources/00_strategic_resources.txt`: resource definitions and storage limits;
- English resource names and the Russian localization baseline in the required priority order, including nested references.

Nine resources have additional `allow` conditions in the original menu. These conditions are preserved. The new section covers exactly the same 26 resources. The source events match the previously researched Tass version by SHA-256.

Findings, source lines, capacity values, terminology sources, and fingerprints are recorded in the [resource menu audit](../../TMP/TCTE/resource_menu_audit.json).

## 3. Resource categories

Approved category and resource order:

| Category | Resources in display order | Resource IDs |
| --- | --- | --- |
| Economy | Energy Credits, Minerals, Food, Consumer Goods, Biomass, Alloys, Trade | `energy`, `minerals`, `food`, `consumer_goods`, `biomass`, `alloys`, `trade` |
| Strategic resources | Volatile Motes, Exotic Gases, Rare Crystals, Living Metal, Zro, Dark Matter, Nanites | `volatile_motes`, `exotic_gases`, `rare_crystals`, `sr_living_metal`, `sr_zro`, `sr_dark_matter`, `nanites` |
| Empire | Influence, Unity | `influence`, `unity` |
| Research | Physics Research, Society Research, Engineering Research | `physics_research`, `society_research`, `engineering_research` |
| Artifacts and astral threads | Minor Artifacts, Astral Threads | `minor_artifacts`, `astral_threads` |
| Special path resources | Menace, Advanced Logic, Feral Insight, Crystallized Entropy, Valor | `menace`, `advanced_logic`, `feral_insight`, `entropy_crystals`, `integrity` |

Totals: **6 categories, 26 resources, 156 grant buttons**. Categories organize this menu only; game resource category definitions are unchanged. Resource names in the interface use existing localization keys.

## 4. Grant amounts

Each resource menu contains six buttons in ascending amount order and a separate Back button.

| Resources | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All resources except the three rows below | 1,000 | 5,000 | 10,000 | 50,000 | 100,000 | 1,000,000 |
| Influence | 50 | 100 | 200 | 300 | 500 | 1,000 |
| Minor Artifacts | 100 | 250 | 500 | 1,000 | 1,500 | 2,000 |
| Astral Threads | 25 | 50 | 100 | 200 | 300 | 500 |

The smaller scales are proposed from vanilla definitions: Influence has `max = 1000` and `fixed_max_amount = yes`; Minor Artifacts have `max = 2000`, and Astral Threads have `max = 500`, both with `special_max_amount = yes`. The latter two are base values: specialized modifiers can increase capacity, and threads also have a dynamic capacity definition.

For threads, the approved highest button grants 500 instead of the previous single grant of 2000; larger amounts are not included in this scale. The other 23 resources use the standard scale, including strategic resources, research, and special path resources.

Amounts specify a single `add_resource` call. Storage capacities and engine resource handling remain unchanged. A large grant button does not guarantee retention beyond the current capacity; behavior at full storage requires in-game verification. Research grants retain the original `add_resource` semantics and do not become technology completion commands.

## 5. Navigation and availability

Window sequence: Add resources → category → resource amount menu. Selecting a resource from its category opens the amount menu directly, with no intermediate window.

- Entering Add resources opens the six-category list.
- Selecting a category opens its resources. Selecting a resource opens its six amounts.
- Clicking an amount grants the selected resource once and then reopens **the same six-amount menu**, allowing an immediate repeat.
- Back returns from amounts to the category, from the category to the category list, and from that list to main menu `tass_cheat.1`.
- Opening windows, navigating, and pressing Back do not grant resources. There are no automatic or monthly grants.
- Preserve player-only access and the existing lifecycle of `tass_cheat_menu_on`: submenus do not independently set or remove that flag.

Categories remain visible. Each original resource condition applies both to entering its menu and to all six grant buttons. As in Tass, `allow` disables an unavailable option instead of hiding it. No restrictions absent from the original menu are added.

| Resource | Preserved condition |
| --- | --- |
| Consumer Goods | `is_wilderness_empire = no` |
| Biomass | `is_wilderness_empire = yes` |
| Minor Artifacts | `has_ancrel = yes` |
| Astral Threads | `has_astral_planes_dlc = yes` |
| Menace | `has_ascension_perk = ap_become_the_crisis` |
| Advanced Logic | `has_ascension_perk = ap_cosmogenesis` |
| Feral Insight | `has_ascension_perk = ap_behemoths` |
| Crystallized Entropy | `has_ascension_perk = ap_galactic_hyperthermia` |
| Valor | `has_ascension_perk = ap_defender_of_the_galaxy_nomads` |

## 6. Implementation and localization

Override `events/tass_cheat_events_4_resources.txt` within TCTE, retaining ID `tass_cheat.4` and making it the category list. This preserves the existing main-menu entry without overriding `tass_cheat.1`. The original Tass file contains only this event. Do not use `replace_path` on the entire event directory.

Add 32 events in a separate `events/tcte_resource_menu_events.txt`: six categories and 26 amount menus. Use namespace `tcte_resources` and unique numeric IDs. Each event is a triggered `country_event` accessible to the player; retain the Tass resource window illustration (`GFX_evt_treasure_pile`).

Each grant option contains one visible `add_resource` with the exact resource and amount, retaining the standard effect tooltip. A `hidden_effect` reopens its own event in the same country scope. Navigation effects are also hidden from tooltips. No resource grants occur in `immediate`; timers, permanent modifiers, additional variables, and interface files are unnecessary for this task.

Place new strings in `localisation/replace/tcte_resource_menu_l_russian.yml` and `localisation/english/tcte_resource_menu_l_english.yml`, with `tcte_` key prefixes. Preserve UTF-8 BOM, language headers, icons, and Stellaris formatting. Titles identify the selected category or resource; grant buttons show an amount and resource icon. A brief description explains amount selection and repeated grants.

Reference existing terminology keys such as `$energy$` and `$minor_artifacts$`; the existing Back label can be reused through `$tass_cheat.4.exit$`. Button amounts must match the corresponding effect constants. Check reference expansion against both the preferred Russian baseline and vanilla, including absence of grammatical metadata. If needed, add sources to existing glossary entries without duplicating terms.

Preserve the existing 94 policy overrides, levels, localization, and other TCTE features. No new vanilla definitions are overridden. Record the resource event in the README, changelog, and separate base-mod change inventory; maintain both documentation languages.

After implementation, increase the version to `0.0.5`, retaining `supported_version="v4.5.*"` and the Tass Cheat Tool dependency. Update the archive and connected local copy, preserving loading after Tass without changing playsets. Distribute runtime files only. At the draft stage the version remains `0.0.4`.

## 7. Validation and acceptance

Synthetic checks after implementation:

1. Compare Tass sources and the vanilla resource definition with research fingerprints; if changed, repeat the relevant source analysis.
2. Check event structure, absence of ID collisions, exactly one effective `tass_cheat.4` when the source file is replaced, and 32 new events.
3. Check the menu graph: all 26 resources occur exactly once under six categories and each has six amounts; every forward and backward transition targets the correct window.
4. Independently of the generator, compare all 156 `add_resource` calls with the amount table; each button grants only the selected resource in a single call, then reopens its own menu. Other options and `immediate` contain no grants.
5. Check preservation of all nine source conditions on resource entries and amount buttons, no added restrictions, player-only access, and no changes to the main-menu flag.
6. Check new RU/EN keys, agreement between amounts/icons and code, references, cycles, grammatical metadata, and encodings; compare existing runtime files with version `0.0.4`.
7. Check documentation, manifest, archive contents, and installed-copy identity. Synthetic checks do not verify actual window rendering or engine resource handling.

The user verifies in-game:

- entry through the planetary decision, category contents, resource names/icons, and button layout;
- all six standard amounts and multiple consecutive grants without leaving the selected resource menu;
- smaller scales, research, and available special path resources, including near-capacity and full-storage cases;
- unavailable resources without the required DLC, empire type, or path;
- Back at every menu level, return to the main cheat menu, and its normal closing behavior;
- no duplicate old resource menu, untranslated keys, or new event-loading errors.

Result: 33 events, six categories, 26 resources, and 156 grants; 224 new keys per language. Preserved all nine availability conditions and 102 previous runtime files; only the version changed in the existing manifest. Report: [resource menu validation](../../TMP/TCTE/resource_menu_validation.json). Evidence: [events and amounts](../../TMP/TCTE/resource_menu_sources.json). Added Biomass and 12 sources to the glossary without duplicate terms: [report](../../TMP/TCTE/resource_glossary_update.json).

[Русская версия ТЗ](TZ_RESOURCES_RU.md).
