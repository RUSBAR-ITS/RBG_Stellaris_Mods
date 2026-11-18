# Stellaris Technological Tree View — technology chains and sorting

## Contents

- [Purpose and status](#purpose-and-status)
- [Baseline requirements](#baseline-requirements)
- [Initial tree layout rules](#initial-tree-layout-rules)
- [Sequential rule application](#sequential-rule-application)
- [Infinitely repeatable technologies](#infinitely-repeatable-technologies)
- [Standard empire in reference mode](#standard-empire-in-reference-mode)
- [Final selection by the function of unlocked objects](#final-selection-by-the-function-of-unlocked-objects)
- [Rechecking the extended rules](#rechecking-the-extended-rules)
- [Reviewing the proposed continuations](#reviewing-the-proposed-continuations)
- [Anchor and vertical placement clarifications](#anchor-and-vertical-placement-clarifications)
- [ID priority and repeated analysis](#id-priority-and-repeated-analysis)
- [Research categories and predecessor selection](#research-categories-and-predecessor-selection)
- [Mandatory prerequisite priority](#mandatory-prerequisite-priority)
- [Additional databases for chain analysis](#additional-databases-for-chain-analysis)
- [Chain construction approaches](#chain-construction-approaches)
- [Rules for further discussion](#rules-for-further-discussion)
- [Starting technologies](#starting-technologies)
- [References](#references)

## Purpose and status

Working document dated 2026-11-17 for gradually collecting rules for identifying chains, ordering them and positioning cards. New rules are added after discussion with the user; proposals are kept distinct from accepted decisions.

This is not yet the specification for the next implementation. The user has defined the initial tree layout rules; the full algorithm is still being designed. This document does not change the current sorting.

## Baseline requirements

Previously agreed requirements to account for during design:

| ID | Requirement |
| --- | --- |
| R-01 | Display the progression of related technologies as chains; independently sorting each column is insufficient. |
| R-02 | Research areas run from top to bottom: physics, society, engineering. |
| R-03 | Columns normally correspond to the game's `tier`; a number in a technology identifier does not determine its column. Exception L-12 moves eligible infinitely repeatable technologies to display column 6 while preserving game `tier = 5`. |
| R-04 | Technology links use technology requirements from `prerequisites`. Conditions involving countries, traits, buildings or other objects do not become technology predecessors. |
| R-05 | Cards are stacked vertically within a column. Within one branch, a predecessor must appear above its dependent technology when both share a column and research area. Requirements from other branches remain game links but do not impose this vertical ordering. |
| R-06 | `technology_swap` variants remain representations of one base technology. Manually switching a variant preserves the base ID, tier and technology dependencies. |
| R-07 | Changing the theme does not change card order. Following the user's clarification, sorting depends on the name in the current language, so switching RU/EN may change the order. |

The current first-stage implementation sorts columns by requirement count, predecessor set and ID according to the [previous technology field specification](elements/TZ_TECHNOLOGY_FIELD_EN.md#vertical-order-and-grouping). The new rules below describe the intended replacement. The previous priorities are not automatically carried into the new algorithm; the new alphabetical ordering decision replaces language-independent ordering.

## Initial tree layout rules

The user defined the initial rules on 2026-11-17 and added further rules on 2026-11-18. Columns correspond to tiers with exception L-12; vertical positions are coordinated across columns: the layout forms a tree and permits empty positions.

| ID | Rule |
| --- | --- |
| L-01 | Starting technologies (`start_tech = yes`) appear at the very top of their research area; all others appear below. |
| L-02 | If a starting technology has a prerequisite, it appears below that prerequisite. |
| L-03 | Alphabetical ordering by the displayed name in the current language applies next. Switching RU/EN may change the layout. |
| L-04 | If a technology continues the same branch and requires another technology in the same tier and research area, it appears directly below it. Requiring a technology from a different branch does not by itself force placement below that technology. |
| L-05 | If the prerequisite is in the previous tier, the dependent technology appears directly to its right. |
| L-06 | If a technology is a prerequisite for multiple technologies in subsequent tiers, they are positioned after it with space reserved for branching; empty space appears below the original technology. |
| L-12 | Place an infinitely repeatable technology (`levels = -1`) with game `tier = 5` and at least one technology prerequisite in display column 6. The prerequisite may belong to any research area. |
| L-09 | With multiple prerequisites, first prefer exact equality between prerequisite and dependent technology IDs after deleting all digits `0–9`. Preserve all other characters. |
| L-07 | After L-09, filter placement candidates by matching research area (`area`), followed by matching research category (`category`), with the dependent technology. |
| L-08 | Among candidates selected under L-07, a mandatory technology prerequisite takes priority over an optional member of an `OR` group. |
| L-11 | When anchor selection is ambiguous in reference mode, remove prerequisite candidates whose availability requires a nonstandard empire type. Prefer the standard empire's technology path; a future user-defined empire will supply the selection context. |
| L-13 | For technologies covered by L-12, resolve ambiguous anchor selection by retaining prerequisites with the highest game `tier` among current candidates. Ties at the maximum `tier` remain ambiguous. |
| L-10 | If multiple candidates remain after the other rules, examine the functional relationship of unlocked objects as the final rule group. The user specified desired continuations for three cases; the general classification mechanism below is proposed for discussion. |

The anchor-selection order updated by the user on 2026-11-18 is L-09 → research area under L-07 → research category under L-07 → mandatory status under L-08. Only existing immediate prerequisites are candidates. At each step, retain matching candidates when any match exists; otherwise retain the current set for the next criterion. A single candidate makes the choice unambiguous. All original requirements are preserved, including additional dependencies and the `AND`/`OR` structure. An ID or category match does not turn an alternative into a mandatory requirement.

The numbering is for referencing rules. The complete precedence for interacting rules remains to be defined; an unspecified case is not automatically resolved by rule number alone.

## Sequential rule application

User clarification dated 2026-11-18:

1. Start with unique IDs of immediate technology prerequisites. If none exist, there is no candidate anchor.
2. Stop immediately when one candidate remains; later rules are not evaluated and cannot replace the result.
3. Apply each rule only to the current candidate set. It cannot restore candidates removed by preceding rules.
4. If a rule produces a nonempty result, replace the current set with that result.
5. If the result is empty, skip the rule and preserve the entire previous set. This is not an error or a reason to invent a dependency.
6. If multiple candidates remain after all rules, preserve the ambiguity for a separate decision; alphabetical ordering does not automatically choose a parent.

The functional relationship criteria under L-10 run after every other anchor-selection criterion, including additional evidence if incorporated into the final algorithm. General card placement rules operate separately from this selection.

## Infinitely repeatable technologies

The user's decision dated 2026-11-18 introduces separate placement and a chain continuation criterion:

1. L-12 applies when all three conditions hold: `levels = -1`, game `tier = 5`, and at least one immediate technology prerequisite. Include technology references inside `AND`/`OR`; neither matching research areas nor matching categories are required for the column move itself. The user removed the original research area restriction.
2. Move the card to display column **6 of its own research area**. Preserve the original `tier`, `area`, `levels` and requirement tree. This is a separate interface column, not a sixth game tier or a repeat research number.
3. When selection is ambiguous, L-13 retains current candidates with the maximum game `tier`. Seniority uses that field, not numbers in IDs, research cost or repeat counts. Previously eliminated candidates are not restored. Stop at one result; a tie does not select an arbitrary parent.
4. L-13 applies only to technologies covered by L-12 and does not introduce a general highest-tier prerequisite priority for other technologies. It precedes the final functional selection under L-10; its exact position among the other criteria remains to be specified in the full algorithm.

Checking the current `data/databases/technologies.json`: 21 out of 679 technologies have `levels = -1`; **19** meet the revised L-12. The exceptions are:

| Technology | Game tier and display column | Reason it is not moved |
| --- | --- | --- |
| `tech_repeatable_lcluster_clue` | 2 | No technology prerequisites; game `tier` is not 5. |
| `tech_cosmogenesis_thesis` | 4 | No technology prerequisites; game `tier` is not 5. |

`tech_repeatable_weapon_type_strike_craft_fire_damage` and `tech_repeatable_weapon_type_strike_craft_fire_rate` also move to society column 6. Their only prerequisite, `tech_strike_craft_3`, belongs to engineering; this relationship remains intact but no longer prevents the column move.

For `tech_repeatable_weapon_type_explosive_damage` and `tech_repeatable_weapon_type_explosive_fire_rate`, when both candidates remain, L-13 selects `tech_swarmer_missiles_2` (`tier = 4`) over `tech_missiles_3` (`tier = 2`). Both repeatables appear in column 6. Empty intermediate columns do not justify introducing missing technology dependencies.

The initial check in this section considered the new rules separately. A complete rerun with L-12/L-13 appears under “Rechecking the extended rules”; earlier counts are retained as research history. Technologies with a finite repeat limit are outside these rules.

## Standard empire in reference mode

User decision dated 2026-11-18: when selecting a chain continuation is ambiguous, reference mode follows the path of a standard empire. L-11 filters candidate technologies by their availability conditions.

- The filter affects placement anchor selection. All technologies, original prerequisites and the `AND`/`OR` structure remain in the database; excluding a candidate does not remove its card or the game requirement.
- In the investigated example, a standard empire is non-nomadic and does not use biological ships. `potential = { is_nomadic = yes }` excludes a candidate, as does a requirement for `country_uses_bio_ships = yes`. Corresponding conditions using `no` do not justify exclusion.
- Evaluate the logical meaning of availability conditions, including nested negations and alternatives. A special branch inside `OR` does not exclude a technology if a branch suitable for the standard empire exists. Mentioning a property in research or AI weights does not itself restrict availability.
- An unknown or not yet interpreted condition does not establish a nonstandard empire requirement. The full set of standard empire properties and supported conditions remains to be defined separately; do not automatically assign other country parameters.
- Preserve the general selection procedure: stop at one candidate; skip a filter producing no candidates and retain the previous set. If multiple candidates remain, continue applying rules.
- This filter belongs before the final functional selection under L-10. Its exact position relative to ID, area, category, mandatory status and object upgrade evidence remains undecided; this decision does not reorder those existing criteria.
- A future user-defined empire will cause the entire tree to be recalculated using its parameters. The configuration contents and rebuilding mechanism belong to later design work.

For `tech_juggernaut`, filtering the full candidate set excludes `tech_arkship_construction` (nomadic empires) and `tech_harbinger_growth_2` (biological ships). `tech_starbase_5` and `tech_battleships` remain. This filter alone does not select Battleships: continuing the ship chain requires a subsequent functional criterion.

Evidence: [arkship condition](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_nomads_dlc_tech.txt:10), [harbinger condition](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_biogenesis_tech.txt:541), [Citadel condition](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:1330), and [Battleships condition](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:185). The [country_uses_bio_ships](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/07_scripted_triggers_ships.txt:33) trigger checks use of the `bio_ship` category.

This rule is recorded for design; sorting code is unchanged. The counts in the later analysis section predate L-11 and are not results of applying this filter.

## Final selection by the function of unlocked objects

The user specified three desired continuations. Inspection of vanilla code supports them, but general automation requires processing object relationships outside the current three databases.

| Dependent technology | Preferred anchor | Verifiable basis |
| --- | --- | --- |
| `tech_civilian_arkship` | `tech_arkship_construction` | Civilian arkship construction directly requires both technologies in the expanded megastructure's `potential`. The anchor concerns building the ship itself; `tech_planetary_engineering` unlocks mining equipment, among other features, rather than this ship construction. |
| `tech_dark_matter_detection` | `tech_detection_array` | The `dark_matter_detector` building requires the `detection_array` module or an earlier queue entry for that module. Both objects affect `ship_cloaking_detection_add`; dark matter extraction supplies a resource rather than continuing the detection function. |
| `tech_dyson_gun` | `tech_lasers_3` | The technology unlocks a megastructure with a firing action leading to `damage_ship`; lasers unlock `weapon_component_template`. Their shared function is weaponry despite different object types. Wormhole stabilization concerns travel. |

Proposed analytical mechanism, not an approved implementation yet:

- First, among remaining candidates, look for direct relationships between unlocked objects: construction requires the candidate's technology, or an unlocked object requires/enhances an object unlocked by the candidate. Use specific construction, access and effect-application conditions; merely mentioning IDs together in AI weights, costs or arbitrary scripts is not such evidence.
- If selection remains ambiguous, compare functional purpose: ship construction, detection, weaponry and other separately defined classes. This is our analytical classification, not another ready-made game field.
- Small configuration rules define which object types, fields, modifiers and linked actions establish a function. Infer technology membership from sources; do not hardcode pairs of technology IDs into the rules. These three cases provide expected verification results.
- A technology may have multiple functions. Preserve the source and rationale for each classification; do not guess unknown functions from names or IDs. If a rule cannot distinguish candidates, apply the general skip/preserve-ambiguity procedure.

Ship-specific qualification: a broad “related to ships” tag is insufficient because `tech_planetary_engineering` also unlocks an arkship module. Furthermore, `prereqfor_desc.ship` is an unlock presentation block and even appears on the Stellar Cannon; it cannot prove ship hull construction without additional data.

Supporting locations:

- The [civilian arkship megastructure](E:/SteamLibrary/steamapps/common/Stellaris/common/megastructures/29_nomad_arkships.txt:1) passes its technology and ship type to the [construction template](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/megastructures/arkship.txt:33); the [mining module](E:/SteamLibrary/steamapps/common/Stellaris/common/starbase_modules/00_arkship_utility_modules.txt:298) links to Planetary Engineering through `show_in_tech` and an access condition.
- The [detection module](E:/SteamLibrary/steamapps/common/Stellaris/common/starbase_modules/00_starbase_modules.txt:282) and [enhancing building](E:/SteamLibrary/steamapps/common/Stellaris/common/starbase_buildings/00_starbase_buildings.txt:2353) contain their technology links, requirements and modifiers.
- A [Stellar Cannon stage](E:/SteamLibrary/steamapps/common/Stellaris/common/megastructures/31_dyson_gun.txt:259) sets `scripted_action = { dyson_shoot }`; its [action](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_actions/04_dyson_gun.txt:146) invokes an [on-action](E:/SteamLibrary/steamapps/common/Stellaris/common/on_actions/02_component_on_actions.txt:403), then an [event](E:/SteamLibrary/steamapps/common/Stellaris/events/nomads_events_1.txt:17274) and a [damage effect](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/nomads_effects.txt:1251). The [UV laser](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_weapons_energy.txt:281) is a weapon component with the `tech_lasers_3` prerequisite.

The current buildings database covers only `common/buildings`; starbase buildings and modules reside in `common/starbase_buildings` and `common/starbase_modules`. This analysis also needs ship and megastructure definitions and linked actions/events. How to include these sources and organize additional databases remains undecided. This discussion does not change the parser, database build or production sorting. The rerun below counts the three reviewed cases separately from automatic rules.

## Rechecking the extended rules

The repeated analysis dated 2026-11-18 covers all **679** base technologies in the published set: 178 without technology prerequisites, 412 with one and **89** with multiple prerequisites. SHA-256 confirms that all three `data/databases/*.json` files are byte-identical to the corresponding `data/stage11/browser_set/` files. Areas, categories, game tiers, `levels` and requirements were compared with the previous research.

For this run, the user confirmed a **non-nomadic, non-gestalt empire with biological founders and conventional ships**. Other ethics, origin, DLC, traditions and development paths remain unspecified. Only a candidate's `potential` in the expanded database tree is evaluated. Unknown conditions remain unknown; `OR` branches and negation are handled structurally. Other countries and objects do not automatically inherit the reference empire's properties. Incompatibility means a proven `false` under known profile facts, rather than a lack of confirmed availability.

Research order: **ID → area → category → mandatory membership → direct object upgrades → standard empire → highest tier for eligible repeatables → previously reviewed functional continuations**. This preserves the previous run and inserts the new filters before the final functional step; the complete priority is not yet an approved product algorithm. Selection stops at one candidate; empty filter results are skipped.

| Applied criteria | Remaining across the database | Within the previous 13 |
| --- | ---: | ---: |
| Previous run, including direct object upgrades | 16 | 13 |
| Then the standard empire profile | 14 | 11 |
| Then the highest-tier prerequisite for eligible repeatable technologies | 12 | 9 |
| Then three previously agreed functional continuations | **9** | **9** |

The final three choices are `tech_civilian_arkship → tech_arkship_construction`, `tech_dark_matter_detection → tech_detection_array` and `tech_dyson_gun → tech_lasers_3`. Their evidence is reviewed above, but a general automatic object-function classifier has not been created. The automatic result of this research is therefore **12**, or **9** after incorporating those agreed choices.

The new rules resolve four cases:

| Technology | Selected anchor | Reason |
| --- | --- | --- |
| Modular Engineering (`tech_modular_engineering`) | `tech_starbase_3` | The alternative `tech_waystation_2` requires a nomadic empire. |
| Robot Manufacturing Nexus (`tech_fe_assembly_1`) | `tech_robomodding` | `tech_robomodding_m` is incompatible with the confirmed profile. |
| Thermodynamic Yield Control | `tech_swarmer_missiles_2`, tier 4 | Higher than the remaining `tech_missiles_3`, tier 2. |
| Miniaturized Pre-Igniters | `tech_swarmer_missiles_2`, tier 4 | The same rule for an infinitely repeatable technology. |

Remaining candidates after all steps; numbers in parentheses are game tiers:

| Technology | Tier | Anchor candidates |
| --- | ---: | --- |
| Juggernaut (`tech_juggernaut`) | 5 | Citadel (4); Battleships (4) |
| Corps of Engineers (`tech_space_defense_station_improvement`) | 3 | Star Fortress (3); Modular Engineering (2) |
| Armor Hardening (`tech_armor_hardeners_1`) | 2 | Ceramo-Metal Alloys (2); Rare Crystal Manufacturing (2) |
| Ceramo-Metal Alloys (`tech_advanced_metallurgy_1`) | 2 | Holographic Casts (1); Ceramo-Metal Materials (1) |
| Mega-Engineering (`tech_mega_engineering`) | 5 | Citadel (4); Battleships (4) |
| Subspace Imaging Array (`tech_arkship_system_scanner`) | 4 | Gravitic Sensors (2); Automated Exploration Protocols (1) |
| Volcanic Terraforming (`tech_volcanic_terraforming`) | 2 | Terrestrial Sculpting (2); Deep Crust Engineering (2) |
| Metacognitive Faith (`tech_transcendent_faith`) | 4 | Consecration Fields (3); Galactic Administration (3) |
| Cross-Model Standardization (`tech_robomodding_points_1`) | 2 | Machine Template System (1); Artificial Specialists (2) |

For Juggernaut and Mega-Engineering, the profile removes nomadic candidates but leaves two conventional anchors. Battleships for Juggernaut is not counted as an automatic decision. Both Civilian Arkship candidates require a nomadic empire: the empty L-11 result is correctly skipped before applying the previously agreed functional continuation. Technologies outside the profile remain in the reference catalog.

L-12 moves **19** technologies to display column 6; moving a card does not select an anchor. Higher-tier priority does not apply to ordinary non-repeatable technologies.

Order sensitivity was checked: moving L-11 immediately after ID changes five otherwise unambiguous selections; placing it after area or category but before mandatory membership changes two (`tech_arkship_tier_2`, `tech_military_arkship`). Moving L-11 after mandatory membership does not change the result. Moving L-13 between the ID step and the final functional step also leaves the current database result unchanged. All tested orders retain the same nine ambiguous technologies; order nevertheless matters for chain membership.

Rerun artifacts are in `data/chain_analysis/`: `export_updated_inputs.ts` reads the current three databases, `research_profile.json` records profile facts and the research order, and `audit_updated_rules.py` produces `updated_rules_analysis.json` with all candidates and steps. `validate_updated_rules.py` checks partial condition evaluation, mandatory membership, empty filters, early termination and tier selection; **27 checks passed**, recorded in `updated_rules_validation.json`. The first five steps reproduced the earlier report for all 89 cases. Product code and source databases were not changed; geometric card placement is outside this run.

## Reviewing the proposed continuations

After the rerun, on 2026-11-18 the user proposed placement for the nine remaining technologies. The desired examples and verification results are recorded below; they do not replace a general algorithm with technology ID pairs. The previous nine-case report remains a snapshot of automatic selection with three earlier functional examples.

| Technology | Proposed anchor | Evidence review |
| --- | --- | --- |
| Juggernaut (5) | Battleships (4) | Unlocks the buildable `juggernaut` ship. Classification cannot rely on `class` alone: its game definition uses `shipclass_starbase`, despite its mobility and shipyard construction. |
| Corps of Engineers (3) | Star Fortress (3) | `starbase_upgrade_cost_mult = -0.15` and `starbase_upgrade_speed_mult = 0.25` modify starbase upgrades. Star Fortress and Modular Engineering are parallel continuations of `tech_starbase_3`, not a sequential pair. |
| Ceramo-Metal Alloys (2) | Holographic Casts (1) | The user accepted the production branch based on immediate function: `planet_metallurgists_produces_mult = 0.05` increases metallurgist output, while Holographic Casts unlocks upgraded foundries. This replaces the initial proposal to continue Ceramo-Metal Materials. |
| Mega-Engineering (5) | Citadel (4) | `feature_flags = { megaengineering }`, megastructure repairs and additional starbase capacity support the structure-related grouping. This is functional grouping, not a direct Citadel-to-megastructure upgrade. |
| Subspace Imaging Array (4) | Gravitic Sensors (2) | Higher-tier than the remaining Automated Exploration Protocols (1). The user selected seniority for this case; L-13 must not automatically be extended to every non-repeatable technology. |
| Metacognitive Faith (4) | Consecration Fields (3) | Both expanded `potential` blocks are identical. They share special access conditions rather than absolute exclusivity to one ethic; see below. |
| Cross-Model Standardization (2) | Artificial Specialists (2) | Desired continuation of robotics. The other candidate, Machine Template System (1), also concerns robots and unlocks `modify_robots`; the target adds robot and machine trait points. The broad function “robot development” does not distinguish the candidates; higher tier does. |

For Armor Hardening and Volcanic Terraforming, the user conditionally proposed placement below both candidates if they belong to the same chain. Reachability was checked in both directions across the complete `prerequisites` graph, alongside current anchor selections.

- **Armor Hardening:** there is no sequential chain between Ceramo-Metal Alloys and Rare Crystal Manufacturing. With the accepted production anchor, one branch is `tech_basic_industry → tech_alloys_1 → tech_advanced_metallurgy_1`, and the other is `tech_basic_industry → tech_rare_crystals`. Both converge at `tech_armor_hardeners_1`, which the user placed after alloys. The alloys' game requirement for materials, `tech_ship_armor_2`, remains a link to a different branch. Analytical support through predecessor effects is discussed below.
- **Ceramo-Metal Alloys predecessors:** `tech_alloys_1` requires `tech_basic_industry`; `tech_ship_armor_2` requires `tech_ship_armor_1`. These are separate branches, and neither candidate is an ancestor of the other. The user selected Holographic Casts based on production function; this choice does not require membership in one existing chain.
- **Volcanic Terraforming:** under the selected profile, `tech_terrestrial_sculpting` and `tech_volcano` share the anchor `tech_colonization_1`. They are sibling branches of one tree that reconverge at `tech_volcanic_terraforming`, not sequential dependencies. The first unlocks terraforming, while the second unlocks blocker removal, including volcanoes. All three share an area and game tier 2. The user chose to place the target vertically between its prerequisites: ordering within one branch does not automatically apply to links between different branches.

Consecration Fields and Metacognitive Faith share this condition: spiritualist **OR** a non-gestalt empire with the `make_spiritualist_1` federation perk. On activation, the perk itself includes technology grants for eligible non-spiritualist members. Thus “unavailable to other ethics” is incorrect; matching special availability conditions support the Consecration Fields preference. Compare condition structure, rather than mere occurrences of `has_ethic`.

The discussion identifies distinct tasks for the next algorithm:

1. **Chain anchor selection:** function, special availability, branch relationships and seniority are separate evidence. The preferences above and subsequent clarifications are expected-result examples; the overall priority of general criteria still needs agreement.
2. **Card ordering:** “predecessor above” applies within one branch. It cannot automatically apply to every prerequisite merely because column and area match: an additional game dependency may lead into another branch. Thus placing Volcanic Terraforming between two branches does not require an ID-specific exception. The earlier interpretation of mandatory placement below all prerequisites has been corrected following the user's clarification.
3. **Branch grouping:** a common ancestor does not establish one linear chain. If one candidate is an ancestor of another, continuation after the later one could be considered; the inspected pairs do not satisfy that condition. Sibling branches can be grouped without inventing a dependency between them.

Supporting sources:

- [Juggernaut](E:/SteamLibrary/steamapps/common/Stellaris/common/ship_sizes/18_juggernauts.txt:1), [Corps of Engineers effects](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:1605), [alloy effect](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2853), [Mega-Engineering](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_megastructures.txt:1).
- [Armor hardening component](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:250), [volcano blocker](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_blocker_deposits.txt:137), [Volcanic Terraforming](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:2161).
- [Consecration Fields](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:5803), [Metacognitive Faith](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:5830), [federation perk trigger](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/02_scripted_triggers_federations.txt:111), [perk and technology grants](E:/SteamLibrary/steamapps/common/Stellaris/common/federation_perks/00_perks.txt:508).
- [Robot modification](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_synthetic_dawn_tech.txt:35), [Cross-Model Standardization](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_synthetic_dawn_tech.txt:88), [Artificial Specialists](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:3214).

Research snapshot before the following clarifications: `data/chain_analysis/nine_case_review.json`, containing seven proposed anchors, two conditional cases, five branch comparisons and equal religious technology conditions. Production sorting and the previous numerical report remain unchanged; new general rules have not been implemented.

## Anchor and vertical placement clarifications

Subsequent user decisions dated 2026-11-18:

1. **Armor Hardening:** place after Ceramo-Metal Alloys (`tech_armor_hardeners_1 → tech_advanced_metallurgy_1` using “technology → anchor” notation). The choice is agreed; a general analytical criterion is still under discussion.
2. **Ceramo-Metal Alloys:** the user agreed on **Holographic Casts** (`tech_alloys_1`) as its anchor based on immediate function. `tech_advanced_metallurgy_1` increases metallurgist output by 5%, while `tech_alloys_1` unlocks upgraded foundries. The intended display chain is **Holographic Casts (1) → Ceramo-Metal Alloys (2) → Armor Hardening (2)**. Material and rare-crystal requirements remain additional game links.
3. **Volcanic Terraforming:** the user explicitly confirmed placement **vertically between its two prerequisites**, within the society tier-2 column, and clarified the scope of R-05/L-04: the ordering rule applies **within one branch**, whereas this case joins two different branches. One required technology can therefore be above and the other below without a technology-specific exception. The `AND` logic and game dependencies remain intact. The order of the two outer cards has not been specified separately; a general placement method for all converging branches still needs to be defined.
4. **Metacognitive Faith:** Consecration Fields is agreed as the anchor based on matching special availability conditions, including the federation exception. Compare condition structure, not just one ethic.
5. **Cross-Model Standardization:** use game tier to distinguish the remaining candidates: Artificial Specialists (2) outranks Machine Template System (1). This confirms a seniority example outside infinitely repeatable technologies; its general priority relative to other criteria still needs to be specified.

A new **hypothesis of functional affinity through candidate predecessors** was checked for Armor Hardening:

- The target `ARMOR_HARDENER_1` component, unlocked by Armor Hardening, contains `ship_modifier.ship_armor_hardening_add`.
- Ceramo-Metal Alloys mandatorily requires `tech_ship_armor_2`. Its unlocked `SMALL_ARMOR_2` component contains the same `ship_modifier.ship_armor_hardening_add` modifier.
- Rare Crystal Manufacturing requires only Industrial Base, which has no technology prerequisites. No components directly requiring either technology were found with this modifier.
- Comparing the target object's effects with effects of objects unlocked by candidate predecessors therefore distinguishes these paths. Compare effect keys in their proper context, not technology names or equal numeric bonuses.
- Traverse the full game prerequisite graph rather than the already selected display chain. The accepted production anchor for alloys does not remove their game requirement for armor materials, so the indirect evidence remains valid. A general algorithm still needs a search depth, handling of `OR` alternatives, and a priority between direct and indirect matches; an arbitrary shared distant technology must not automatically merge branches.

This checks one example; it does not approve or implement a universal rule. Sources: [armor component](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities.txt:147), [hardener component](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:250), [alloy prerequisites and effect](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2853), [upgraded foundry](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/04_manufacturing_buildings.txt:97). Evidence was also confirmed in `data/databases/components.json` and saved with JSON Pointers in `data/chain_analysis/armor_function_evidence.json`.

The observation about candidate counts is confirmed: all **nine** previously remaining cases had exactly **two** candidates. However, of the original 89 ambiguous technologies, 71 had two prerequisites, 14 had three, one had four, and three had five. Sequential filtering therefore continues to support any number of candidates; placement between two is a separate geometry case.

## ID priority and repeated analysis

The 2026-11-18 analysis used the published set `data/databases/{technologies,components,buildings}.json` through the current frontend adapters. It covered the base representations of all 679 technologies; 89 have multiple immediate prerequisites. Areas, categories and requirement structures were compared against the previous research for every technology: no differences were found. Category selection when manually switching variants remains a separate question.

Here, “ID similarity” means equality after removing digits: for example, `tech_afterburners_1` and `tech_afterburners_2` both become `tech_afterburners_`. Common prefixes, string distances, translated names and additional transformations are not used.

| Applied criteria | Ambiguous among all 89 | Within the previous 39 |
| --- | ---: | ---: |
| ID → area → category | 22 | 19 |
| Then the agreed mandatory-prerequisite priority | 19 | 16 |
| Then additional direct component/building upgrade evidence | 16 | 13 |

The successive ID, area and category criteria resolve 29, 29 and 9 cases out of 89, respectively. The ID rule resolves 20 of the previous 39. Mandatory status additionally distinguishes `tech_arkship_tier_2`, `tech_growth_chamber_1` and `tech_military_arkship`; two previous L-08 cases have already been distinguished by ID.

Object upgrade links additionally select `tech_cloaking_3` for `tech_cloaking_dark_matter`, `tech_basic_health` for `tech_frontier_health`, and `tech_xeno_diplomacy` for `tech_xeno_relations`. The last table row is an additional research scenario; the complete priority of upgrade evidence in the algorithm is not yet approved. In the current data, unambiguous choices from the first three criteria do not conflict with the discovered upgrade evidence.

The previous 39 did not cover every ambiguity: six other technologies had no prerequisite matching both area and category. The new order distinguishes three of them. Three remain: `tech_civilian_arkship`, `tech_dark_matter_detection`, and `tech_dyson_gun`. Therefore, the result with additional evidence is 16 across the database and 13 within the previous group. Removing digits resolves none of the previous 13 remaining cases; it provides a simpler selection method for already investigated continuations.

Reproducible analysis: `data/chain_analysis/audit_id_priority.ts`; result: `data/chain_analysis/id_priority_analysis.json`. The report includes SHA-256 hashes for all three input databases, the set ID, every candidate and each selection step. This checks anchor selection, not a completed geometric layout; current sorting code has not changed.

## Research categories and predecessor selection

A research category is specified by `category`, for example `category = { propulsion }`; the research area is a separate `area` field. All 679 base technologies in the current database have exactly one category, although the field is syntactically a list.

| Area | Categories of base technologies in the current database |
| --- | --- |
| Physics | Particles (`particles`), computing (`computing`), field manipulation (`field_manipulation`) |
| Society | Statecraft (`statecraft`), military theory (`military_theory`), biology (`biology`), new worlds (`new_worlds`), archaeostudies (`archaeostudies`), psionics (`psionics`) |
| Engineering | Industry (`industry`), materials (`materials`), propulsion (`propulsion`), voidcraft (`voidcraft`) |

This is the observed distribution, not a hard language restriction. Category definitions are in `common/technology/category/00_category.txt`. Russian labels were checked against `Localisation_Base/1-Prio_Russian_Localization_Fix_RE/russian/technology_l_russian.yml` and `ancient_relics_l_russian.yml`; no overrides of these keys were found in `replace`. English keys were checked against the corresponding English game localization files.

Checking L-07 against the base representations of 89 technologies with multiple immediate prerequisites:

| Prerequisites matching both `area` and `category` | Technologies |
| --- | ---: |
| Exactly one candidate | 44 |
| Multiple candidates | 39 |
| No candidates | 6 |

Of the 44 cases with one candidate, 11 had multiple candidates when considering area alone: the category distinguishes them. The count uses IDs mentioned in `prerequisites`, including `OR` alternatives; game conditions are not evaluated.

Example: **Planetary Reprocessor** (`tech_arkship_planetary_refinery`, `engineering / industry`) requires **Planetary Engineering** (`tech_planetary_engineering`, `engineering / industry`) and **Arkship Mastery** (`tech_arkship_tier_3`, `engineering / voidcraft`). Under L-07, Planetary Engineering becomes the preferred placement anchor; the arkship requirement is preserved.

Example of remaining ambiguity: **Advanced Afterburners** (`tech_afterburners_2`) requires `tech_afterburners_1` and `tech_thrusters_3`; all three belong to `engineering / propulsion`. L-07 alone is insufficient here.

Verification materials: `data/chain_analysis/category_analysis.json`, source database `data/stage10/database.json`. Eleven `technology_swap` blocks override the category. Whether to select the anchor using base or currently displayed categories needs a separate decision; the statistics above use base representations.

## Mandatory prerequisite priority

The user approved L-08 on 2026-11-17. Mandatory status is derived from the `prerequisites` structure without evaluating country state. An ID appearing in one `OR` alternative is not necessarily mandatory. All requirements and alternatives remain intact; only the preference for choosing a layout continuation changes.

If several eligible mandatory candidates remain, L-08 does not select one. If none remain, choosing between alternatives is a separate task. The rule preserves the area/category priority established by L-07.

Among the 39 investigated cases, this rule selects a unique candidate for five additional technologies:

| Technology | Preferred prerequisite |
| --- | --- |
| `tech_arkship_tier_2` | `tech_arkship_construction` |
| `tech_arkship_tier_3` | `tech_arkship_tier_2` |
| `tech_growth_chamber_1` | `tech_stingers` |
| `tech_growth_chamber_2` | `tech_growth_chamber_1` |
| `tech_military_arkship` | `tech_arkship_construction` |

Including the 21 cases supported by object upgrades or matching effects, there is a basis for selection in 26 of 39 cases; 13 remain ambiguous. This reflects research and approval of L-08, not approval of the entire algorithm or an implemented sorting change.

## Additional databases for chain analysis

The user defined the next scope: the backend must create two additional databases, for components and buildings; the frontend must work with three databases, including technologies.

| Database | Main game directory | Linking data |
| --- | --- | --- |
| Technologies | `common/technology` | ID, `prerequisites`, area, category and effects |
| Components | `common/component_templates` | `key`, `prerequisites`, `upgrades_to` |
| Buildings | `common/buildings` | Definition ID, `prerequisites`, `upgrades` |

The proposed foundation is the existing shared parser with separately configurable source and output sets. Each database retains the results of the full standard parsing and expansion pipeline; a separate processing step extracts links. The frontend will need separate object indexes and database-qualified references: the same JSON Pointer in different files identifies different nodes.

Also agreed: the user selects the three files in one action as one set; names and descriptions of all three kinds are immediately enriched in Russian and English. Opening prepared databases remains an explicit user action; application startup and page reload do not trigger generation.

[Backend stage 11](../TZ_BACKEND_STAGE_11_EN.md) and [frontend stage 2](TZ_FRONTEND_STAGE_2_EN.md) specifications have been drafted. Their shared set marker, node addressing, diagnostics, component/building localization rules and upgrade-evidence extraction are proposed for approval. Code and current sorting remain unchanged.

## Chain construction approaches

Two approaches were identified earlier. The initial rules above describe the desired behavior; selection of the complete method and its implementation are still pending.

| Approach | Content | Consequences |
| --- | --- | --- |
| Manual | Explicitly assign technologies to chains and define their order; the storage method remains to be chosen. | Easier to specify the intended result directly, but changes to technologies and links require reviewing these assignments. |
| Analytical | Derive chains from data using general rules. | Rules need iterative development and checks against branches, merges and other ambiguous cases. |

Proposal for the analytical approach: identify chain membership separately from positioning chains in columns. Start with several examples and then check the rules against the full database. This is a discussion proposal, not an approved algorithm.

## Rules for further discussion

The following decisions remain open:

- How to choose an anchor when ambiguity remains after L-07 and L-08 or there are no matches; how to choose between multiple `OR` alternatives.
- How placing all starting technologies at the top interacts with aligning their non-starting continuations to the right, and how “below the prerequisite” interacts with placement in an adjacent column.
- How to allocate space to multiple dependents in one tier, calculate branch heights and apply alphabetical ordering under otherwise equal conditions; how to resolve identical names.
- How to handle links spanning multiple tiers, crossing research areas or pointing toward a lower `tier`.
- How manually switching a variant and its category affects anchor selection and branch layout.

Existing research provides examples for checking proposals: lasers, reactors, missiles, mining stations, starbases and `tech_akx_worm_1…3`. Equality after removing digits is defined by L-09. An arbitrary shared ID prefix, absence of predecessors or membership in the same connected component has not by itself been accepted as a chain identification rule.

## Starting technologies

The `start_tech = yes` flag has been inspected; a full [starting technology list](STARTING_TECHNOLOGIES_EN.md) is provided separately.

In the current database it appears on 42 technologies: 38 have `tier = 0`, and four have `tier = 1`. Nineteen have `starting_potential`, and eleven have technology predecessors. Thus “starting technology”, “tier zero” and “vertex without predecessors” describe different properties.

The user approved placing starting technologies at the top under L-01 and accounting for their prerequisites under L-02. The flag alone does not imply an absence of predecessors.

## References

- [Analysis of all 39 ambiguous continuations](RESEARCH_AMBIGUOUS_CHAINS_EN.md): evaluating independent branches, explicit component/building upgrades, modifiers and alternatives. Mandatory prerequisite priority is accepted as L-08; the other research proposals do not automatically become approved rules.
- [Chain research using the current database](RESEARCH_TECHNOLOGY_CHAINS_EN.md).
- [Starting technologies and conditions](STARTING_TECHNOLOGIES_EN.md).
- [Current technology field specification](elements/TZ_TECHNOLOGY_FIELD_EN.md).
- [First frontend stage results](FRONTEND_STAGE_1_EN.md).

[Русская версия](TECHNOLOGY_CHAINS_AND_SORTING_RU.md).
