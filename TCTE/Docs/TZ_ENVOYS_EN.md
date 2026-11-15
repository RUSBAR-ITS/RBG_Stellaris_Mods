# TCTE — cumulative envoy grants specification

## Contents

- [1. Status and scope](#1-status-and-scope)
- [2. Researched baseline](#2-researched-baseline)
- [3. Menu and accumulation](#3-menu-and-accumulation)
- [4. Repeatable technology](#4-repeatable-technology)
- [5. Files and localization](#5-files-and-localization)
- [6. Validation and acceptance](#6-validation-and-acceptance)

## 1. Status and scope

**Approved by the user on 2026-11-15. Implemented in version `0.0.8`; synthetic checks passed. In-game testing remains with the user.**

The baseline TCTE release is `0.0.7`; the resulting release is `0.0.8`. Baseline: Tass Cheat Tool `20261012`, Workshop ID `682851228`, Stellaris `v4.5.*`.

Replace the one-time +20 grant through `modifier_tass_extra_envoy` with a menu of cumulative grants through a service repeatable technology. The existing Extra Envoys option in the main cheat menu opens the new submenu; no separate planetary decision is needed. Species modification, policies, resources, and other cheats are outside scope.

## 2. Researched baseline

The original `tass_cheat.1.extra_envoy` option in `tass_cheat.1` grants permanent `modifier_tass_extra_envoy`, is disabled while it is present, and returns to the main menu. That modifier sets `envoys_add = 20`; no technology is currently used.

The current local `effects.log` documents `give_technology`, `while` with `count`, and `create_leader`. No dedicated `add_envoy`, `add_envoys`, or `create_envoy` effect was found. The `envoy` class exists in `common/leader_classes/00_base_classes.txt`, but persistence of directly created envoys beyond capacity has not been tested. Vanilla `astral_rift.2790` increases capacity through `reconverted_leader_modifier` alongside changing a leader's class to envoy.

Vanilla `tech_collective_self` uses `modifier = { envoys_add = 1 }`. Repeatable technologies in `00_soc_tech_repeatable.txt` use `levels = -1`; events in `distant_stars_events_1.txt` grant repeatable technologies through `give_technology`. These support the chosen approach; granting multiple levels in one click and actual envoy availability in the target version still require in-game testing.

Sources, line ranges, effect documentation, terminology, and fingerprints: [audit](../../TMP/TCTE/envoy_menu_audit.json). Game and Workshop sources are read-only.

## 3. Menu and accumulation

Path: planetary decision opening cheats → main menu → Extra Envoys → grant menu.

| Button | Increase to current envoy capacity | Technology levels granted |
| --- | ---: | ---: |
| 5 envoys | +5 | 1 |
| 10 envoys | +10 | 2 |
| 25 envoys | +25 | 5 |
| 50 envoys | +50 | 10 |
| 100 envoys | +100 | 20 |
| 500 envoys | +500 | 100 |

These are additions, not assignments of a total or mutually exclusive levels. For example, 5 → 10 → 25 gives +40 overall; clicking 500 twice gives +1000. Base capacity and other sources of bonuses remain intact. The mod adds no accumulation ceiling; engine limits still apply.

Each click grants the selected number of levels once, then reopens the same envoy menu through a hidden transition. Back returns to `tass_cheat.1`. Entering, opening, returning, and redisplaying the menu do not grant anything by themselves. Do not add monthly grants, timers, or automatic envoy task assignments.

Access is player-only and scoped to the player's country. Retain the lifecycle of `tass_cheat_menu_on`; the submenu does not set or remove this flag. Existing `modifier_tass_extra_envoy` no longer blocks entry or grants. A previously acquired +20 bonus is neither removed nor converted automatically: it is part of the country's initial state. The new path does not add or refresh that modifier; save migration is outside scope.

## 4. Repeatable technology

Add one technology, `tcte_tech_extra_envoys`: repeatable without a specified final level (`levels = -1`), society area, `statecraft` category, and `envoys_add = 5` per level.

This service technology is excluded from normal random research selection by zero weight, is not a starting technology, and is not granted automatically. Do not use an ownership prohibition in `potential` that could invalidate its effect for a recipient. Add no ethics, authority, origin, or DLC restrictions. Player access is enforced by the menu. Disable reverse engineering; add no side bonuses, feature flags, or `on_research_complete` events.

A button grants the next level using `give_technology = { tech = tcte_tech_extra_envoys message = no }`. Multiple levels use `while` with the fixed `count` from the table. Grants precede reopening the window. No separate counter variable is needed: accumulated progress is stored in the technology level and must survive save/load.

There is no separate country modifier applied through `add_modifier`. However, `envoys_add` remains a country bonus inside the technology definition; this is the distinction the user agreed to. Do not promise complete invisibility in researched-technology history: excluding normal research offers and suppressing notifications does not guarantee hiding it on every screen.

The mechanism raises envoy capacity; the game creates available envoys. Update timing while paused and after a game tick, bonus persistence, and replacement after an envoy dies require in-game verification. Direct `create_leader` spawning is not used.

## 5. Files and localization

- In existing `events/tass_cheat_events_1_country.txt`, change only the Extra Envoys option: updated tooltip, player access, and transition to the new menu; remove the old +20 grant and modifier-based block. Preserve other options.
- Add one triggered country event, `tcte_envoys.1`, in `events/tcte_envoy_menu_events.txt`: six grant buttons and Back. Do not copy unrelated events or change GUI files.
- Add only the new repeatable technology in `common/technology/tcte_envoy_technologies.txt`. Do not copy vanilla technologies, use `replace_path`, or change the base capacity in defines.
- Add RU/EN titles, a short description, buttons, tooltips, and technology name/description in `localisation/replace/tcte_envoy_menu_l_russian.yml` and `localisation/english/tcte_envoy_menu_l_english.yml`. All new keys start with `tcte_`; retain UTF-8 BOM and Stellaris localization formatting.

The menu title may reuse `tass_cheat.1.extra_envoy`. Do not use the old tooltip promising 20 envoys and one day in the new path. Player-facing text states amounts and cumulative behavior without explaining internal technology grants. Follow AGENTS.md terminology priorities; confirmed keys include `default_envoy` (Envoy), `envoy_costs` (Envoys), and `MOD_COUNTRY_ENVOYS_ADD` (Envoy Capacity). Reuse references where grammatical forms fit; do not expose grammatical metadata. Update the shared glossary without duplicate terms during implementation.

Update bilingual README files, changelog, and the Tass definition inventory. No new vanilla overrides are required. After approval and implementation, increase the version to `0.0.8`, retain `supported_version="v4.5.*"`, build the archive, and update the connected copy without modifying playsets. The baseline distribution was preserved until approval.

## 6. Validation and acceptance

Version 0.0.8 validates six grants, 176 sequences in an arithmetic model, navigation, absence of side effects, 18 new keys per language, and three reference baselines. Other main-menu blocks remain byte-identical; 110 previous runtime files are unchanged. The archive contains 116 files. The model does not verify engine technology stacking. [Report](../../TMP/TCTE/envoy_menu_validation.json); [constant evidence](../../TMP/TCTE/envoy_menu_sources.json).

Synthetic checks after implementation:

1. Verify sources, exactly one new technology and event, unique IDs, the six specified amounts, and Back.
2. Check `number of levels × 5`: every grant, repeated amounts, and mixed sequences. Compare accumulated levels with a model without presenting it as an engine test.
3. Verify `tcte_envoys.1` reopens after every grant, Back targets `tass_cheat.1`, entering and returning grant nothing, country scope is correct, and AI does not act.
4. Ensure the new path does not call `add_modifier`, is not blocked by the old modifier, does not directly create leaders, and has no automatic grants or duplicate counter.
5. Validate English, preferred Russian, and vanilla Russian localization, amounts, references, and BOM; preserve other TCTE functionality, including species modification and the resource menu.
6. Verify bilingual documentation, archive contents, and connected-copy identity.

The user tests initial capacity, each amount, repeated +500, the +5/+10/+25 sequence, save/load, lack of research notifications, behavior while paused and after a tick, assignment of new envoys, capacity after envoy death and replacement, and Back in-game. Test a regular empire and available gestalt variants. An existing +20 bonus must neither block the menu nor alter the size of the new grant. Verify the service technology does not appear in normal research offers or disturb currently selected research.

[Русское ТЗ](TZ_ENVOYS_RU.md).
