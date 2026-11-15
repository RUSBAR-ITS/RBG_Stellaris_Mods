# TCTE — advanced species modification toggle specification

## Contents

- [1. Status and scope](#1-status-and-scope)
- [2. Bonuses and button behavior](#2-bonuses-and-button-behavior)
- [3. Implementation and localization](#3-implementation-and-localization)
- [4. Positive trait removal research](#4-positive-trait-removal-research)
- [5. Validation and acceptance](#5-validation-and-acceptance)

## 1. Status and scope

**The user agreed to +100/+30 and toggling on 2026-11-15. On the same date, the user explicitly requested extending the removal trigger with the combined technology and active-cheat condition. Version `0.0.7` is implemented and synthetic checks passed; in-game verification remains with the user.** Retain Advanced Species Modification as a country modifier, increase its bonuses to +100 trait points and +30 trait picks, and allow removal through the same main-menu entry. The baseline release is `0.0.5`.

Baseline: Tass Cheat Tool `20261012`, Workshop ID `682851228`, and installed Stellaris `v4.5.*`. Sources, definitions, and fingerprints are recorded in the [audit](../../TMP/TCTE/species_modding_audit.json).

The scope includes extending `can_remove_beneficial_genetic_traits`: an additional permission applies when the player country has both `tech_gene_expressions` and `modifier_tass_extra_species_modding`. Original tradition conditions remain intact. Extra Envoy behavior is outside this specification; its subsequent 0.0.8 change is implemented under a [separate specification](TZ_ENVOYS_EN.md).

## 2. Bonuses and button behavior

Retain the original ID `modifier_tass_extra_species_modding`, icon, and permanent duration when enabled (`days = -1`). Replace values as follows:

| Archetype | Trait points | Trait picks |
| --- | --- | --- |
| `BIOLOGICAL` | `BIOLOGICAL_species_trait_points_add = 100` | `BIOLOGICAL_species_trait_picks_add = 30` |
| `ROBOT` | `ROBOT_species_trait_points_add = 100` | `ROBOT_species_trait_picks_add = 30` |
| `MACHINE` | `MACHINE_species_trait_points_add = 100` | `MACHINE_species_trait_picks_add = 30` |

These are additions to the country's existing values, not assignments of final totals. No new technologies, traditions, or traits are granted.

| Country state | Only displayed button | Action |
| --- | --- | --- |
| Modifier absent | Advanced Species Modification | Adds the original modifier permanently and reopens the main menu |
| Modifier present | Remove Advanced Species Modification | Removes that modifier and reopens the main menu |

The entry retains the position of the original cheat. Both labels are never shown simultaneously; Already Active no longer blocks access to removal. Presence is determined through `has_modifier`, including when the original modifier is already present in a save. No separate state flag is needed.

After removal, the button offers enabling again. Re-enabling must not accumulate bonus copies. Actions affect only the country opening the menu. Removing the bonus does not initiate species modification, strip species traits, or revoke researched technologies or traditions; template validity after lowering the limits requires in-game verification.

## 3. Implementation and localization

Override two original Tass files inside TCTE, retaining their relative paths:

- `common/static_modifiers/tass_cheat_static_modifiers.txt`: change only the six numeric values in `modifier_tass_extra_species_modding` from 50/5 to 100/30; preserve other modifiers;
- `events/tass_cheat_events_1_country.txt`: replace the original `tass_cheat.1.trait_points` option with two mutually exclusive options checking absence or presence of the modifier. The first calls `add_modifier`, the second calls `remove_modifier`; both return to `tass_cheat.1` through `hidden_effect`.

Preserve the main event ID, other options, order, country scope, player access, `tass_cheat_menu_on`, and normal closing behavior. The existing `tass_cheat.4` resource-menu entry must continue working with TCTE 0.0.5. Do not use directory-wide `replace_path`.

Under the user's explicit 0.0.7 correction, remove the full copy of `common/scripted_triggers/05_scripted_triggers_traits.txt`. Include only the modified `can_remove_beneficial_genetic_traits` in `common/scripted_triggers/tcte_species_traits_triggers.txt`, preserving its 0.0.6 block unchanged. Omit the other 49 definitions from TCTE: they load from the original game file.

Scripted triggers use the last loaded definition of an ID (LIOS; [mod developer notes](https://github.com/openly-retro/stellaris-machine-robot-expansion/wiki/Dev-notes:-Modding-Den-highlights)). `tcte_species_traits_triggers.txt` sorts after `05_scripted_triggers_traits.txt`, the only definition of this ID found in vanilla and Tass. Retain the vanilla ID for existing calls. Do not use `replace_path` or modify game files. Verify actual engine loading in-game.

The removal button and new tooltips use `tcte_` keys in Russian and English. The enable label may retain the original key. The event must reference the current +100/+30 tooltip rather than the previous +50/+5 text. Tooltips explain the additional permission with `$tech_gene_expressions$` and its loss when disabling the cheat, while normal permissions remain intact. Preserve localization format, UTF-8 BOM, and references to existing game terminology.

Update the README, changelog, specification, and separate base-mod override inventory in both languages. Distinguish the source file from the separate TCTE file containing one trigger in the vanilla change inventory. Increase the version to `0.0.7`, preserve `supported_version="v4.5.*"` and the Tass Cheat Tool dependency, and update the archive and connected copy, removing the previous full copy from the installation. Playsets, policies, the resource menu, envoys, and other cheats remain unchanged.

## 4. Positive trait removal research

In the installed version, permission is checked in each trait's `species_possible_remove`. The general permission for beneficial organic traits uses `can_remove_beneficial_genetic_traits` in `common/scripted_triggers/05_scripted_triggers_traits.txt`, line 71. Its `this` scope is the species and `from` is the modifying country; it first checks that `from` exists.

This trigger requires:

- if `has_biogenesis_dlc = no` **or** `tr_genetics_adopt` has been adopted, `tr_genetics_resequencing` — **Genetic Resequencing**;
- in the other branch, with Biogenesis and without `tr_genetics_adopt`, `tr_purity_genotype_regeneration` — **Genotype Regeneration**.

This is a tradition presence check, not a numeric modifier. Definitions of `tr_genetics_resequencing` and `tr_purity_genotype_regeneration` contain no numeric bonus granting removal; the connection is implemented directly by `has_tradition` in the trigger.

A separate technology path exists through **Targeted Gene Expressions**, `tech_gene_expressions` (`common/technology/00_soc_tech.txt`, line 3132). The `can_remove_vocational_genetic_traits` trigger (line 63 of the same trigger file) checks `from = { has_technology = tech_gene_expressions }`. This permits removal only for traits calling that check. For example, `trait_agrarian` (Agrarian) accepts the general **or** technology-based trigger, while `trait_quick_learners` (Quick Learners) calls only the general trigger.

**Gene Tailoring**, `tech_gene_tailoring`, enables basic trait modification through `feature_flags = { modify_traits pop_self_modification }` and adds points. These flags do not themselves replace the beneficial trait removal conditions above. Names were checked against English keys and the preferred Russian baseline.

At the user's explicit request, extend only `can_remove_beneficial_genetic_traits`. Preserve `hidden_trigger = { exists = from }` and checks in `from`, the modifying country. The resulting logic is **original vanilla permission OR (player country AND technology AND active modifier)**. Combine `is_ai = no`, `has_technology = tech_gene_expressions`, and `has_modifier = modifier_tass_extra_species_modding` with AND in the new branch; retain the unchanged original branch under OR.

| Original permission | Technology | Cheat | Player result |
| --- | --- | --- | --- |
| No | No | No | Denied |
| No | Yes | No | Denied |
| No | No | Yes | Denied |
| No | Yes | Yes | Allowed |
| Yes | Either | Either | Allowed |

AI retains the original logic even with the technology and modifier. Without `from`, permission is denied. The cheat can be enabled without the technology: +100/+30 applies immediately, while removal permission requires the joint condition. Technology is not automatically granted. Removing the modifier removes the additional permission; original tradition conditions continue working.

Do not change `can_remove_vocational_genetic_traits`, other triggers, or individual trait definitions. The new permission applies only where `can_remove_beneficial_genetic_traits` is called; other conditions of each trait still apply. The change extends editing permission without automatically removing traits.

## 5. Validation and acceptance

The 0.0.7 correction is implemented: the distribution contains one trigger definition in a separate file; the previous full copy is absent. The trigger block is byte-identical to 0.0.6, 110 other runtime files are preserved, and only the version changes in the manifest. Checked filename ordering, retention of 49 vanilla definitions in a static loading model, all 256 condition combinations, and archive contents. [0.0.7 report](../../TMP/TCTE/trigger_override_validation.json). Actual engine loading remains untested.

Actual 0.0.6 result: passed 256 permission combinations, four visibility states, eight toggle transitions, six numeric bonuses, and expansion of new references against three localization baselines. The other 49 vanilla triggers and 106 previous runtime files are preserved. [Report](../../TMP/TCTE/species_modding_validation.json), [condition table](../../TMP/TCTE/species_modding_truth_table.json), [sources and constants](../../TMP/TCTE/species_modding_sources.json).

After implementation, verify:

1. Source fingerprints against the researched baseline; values exactly 100/30 for all three archetypes. Other definitions in the source modifier file remain intact.
2. Both `has_modifier` states: exactly one correct option is visible; enabling grants the original modifier once permanently, and removal removes only it. Enable → remove → enable does not accumulate bonuses.
3. Both actions return to the main menu; its flag, access conditions, and every other option remain intact, especially the resource-menu entry and Extra Envoy action.
4. RU/EN keys, references, encodings, and agreement between tooltip numbers and code. New buttons and tooltips contain no obsolete 50/5 values.
5. For the 0.0.7 correction, preserve other runtime files relative to 0.0.6 except the manifest version and the move to a single-trigger file. Verify absence of the full copy from the mod, archive, and connected copy; check bilingual documentation.
6. Exhaustively combine technology, modifier, player/AI, `from` presence, Biogenesis, the adopted genetics tree, and both traditions: the result must equal original permission OR the new joint check. Neither technology nor cheat alone grants new permission. Preserve the original branch; other triggers load from the vanilla file.

The user tests a new and already active modifier in-game, label changes after every click, resulting points and picks for all three archetypes, removal of only the cheat's bonuses, re-enabling, and template state after bonus removal. Separately check all four technology/cheat combinations without the required tradition, then preservation of tradition-based permission with the cheat disabled. Quick Learners (`trait_quick_learners`) provides a clean test because it uses the general trigger without the alternative vocational editing permission. Synthetic checks do not verify engine limit recalculation or menu rendering.

[Русская версия ТЗ](TZ_SPECIES_RU.md).
