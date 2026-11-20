# Stage 21 — recursive indirect DLC restrictions

## Contents

- [1. Status and objective](#1-status-and-objective)
- [2. Confirmed inputs](#2-confirmed-inputs)
- [3. Additional databases](#3-additional-databases)
- [4. Evaluation model](#4-evaluation-model)
- [5. Object traversal rules](#5-object-traversal-rules)
- [6. Recursive traversal](#6-recursive-traversal)
- [7. Cycles and reuse](#7-cycles-and-reuse)
- [8. Configuration](#8-configuration)
- [9. Combinations and interface](#9-combinations-and-interface)
- [10. Evidence and coverage](#10-evidence-and-coverage)
- [11. Validation and acceptance](#11-validation-and-acceptance)
- [12. Implementation sequence](#12-implementation-sequence)
- [13. Sources](#13-sources)

## 1. Status and objective

**The main scope and addendum were approved by the user on 2026-11-19 and implemented.** Technology acquisition analysis is specified in the [approved addendum](TZ_BACKEND_STAGE_21_ACQUISITION_EN.md). Verification results and acceptance boundaries are in the [guide](BACKEND_STAGE_21_EN.md); browser and engine verification are not claimed complete.

Extend [stage 20](TZ_BACKEND_STAGE_20_EN.md) to resolve DLC restrictions through references to game objects. Example: technology → ship category → player-selectable ship sets → BioGenesis. Another route: technology → tradition → tradition category → DLC.

Coverage follows the entire imported DLC catalog. DLC names and their technology lists are not hardcoded. Rules describe relation types; concrete objects and restrictions come from prepared databases.

Keep reference mode without selecting a particular empire. Restrictions on initial object selection use a playable-empire context; NPC-only variants are not considered a way for the player to select that object. This does not assert that such NPCs cannot exist in the galaxy. The context must be included in configuration, evidence and calculation revision.

This stage does not simulate a particular campaign's history, research probability, DLC ownership, the user's particular ethics/origin or automatic `technology_swap` selection. Static analysis of technology grant routes is added through the separate draft addendum. Services and builds start explicitly. Switching DLC does not reread the game.

## 2. Confirmed inputs

In `data/stage20/dlc_none_report.json`, `tech_weaver_bio_fire_rate_2` remained visible: expanded `country_uses_bio_ships` contains `exists = this` and `uses_ship_category = bio_ship`, which stage 20 left unknown. Selectable sets `biogenesis_01` and `biogenesis_02` require BioGenesis in `selectable`. The separate `biogenesis_01_fallen_empire` has `selectable = { always = no }` and must not provide this selection route to the player.

Initial source inventory, without insertion expansion or reachability evaluation:

| New database kind | TXT files | Root definitions |
| --- | ---: | ---: |
| `ascension_perks` | 2 | 49 |
| `traditions` | 33 | 234 |
| `tradition_categories` | 34 | 33 |

Each of the latter two directories has one comment-only README with no objects. No duplicate root IDs or syntax errors were found in this limited pass. This is not full-build validation. Working results: `TMP/WEB_STTV/stage21_design_inventory.json` relative to the repository root.

Current no-DLC diagnostics include `uses_ship_category` for 88 technologies, `has_ascension_perk` for 53, `has_origin` for 49, `has_authority` for 36 and `has_tradition` for 3. Counts overlap and represent unknown checks, not incorrectly displayed technologies. They do not include every leaf beneath unsupported wrappers. The new audit must separately inventory such subtrees.

## 3. Additional databases

Propose expanding the shared registry from 25 to 28 kinds:

| Variable | Path relative to `STELLARIS_ROOT` | Kind |
| --- | --- | --- |
| `ASCENSION_PERKS_DIR` | `common/ascension_perks` | `ascension_perks` |
| `TRADITIONS_DIR` | `common/traditions` | `traditions` |
| `TRADITION_CATEGORIES_DIR` | `common/tradition_categories` | `tradition_categories` |

The acquisition addendum proposes `crisis_paths` and `crisis_levels`, bringing the total to 30 kinds, plus a separate technical acquisition index. These additional sources have not yet been imported; requirements are in the [addendum](TZ_BACKEND_STAGE_21_ACQUISITION_EN.md#2-inputs-and-index-preparation).

All three directories use the existing parser, insertion libraries, static variables, parallel preparation, separate documents and atomic manifest publication. Root object identity is its block key. Object counts are not constants. Do not copy game source files into the product.

Add RU/EN localization with existing priorities. Use the object key and `_desc` for ascension perks; the object key and `_delayed` for traditions, as documented by the game README. For categories, honor explicit `desc`, followed by the configured standard key. Verify actual keys before adding rules. Preserve localization for nested `tradition_swap` entries with their own names/descriptions. A localization name does not automatically become a new game ID.

Add the kinds to source settings, the object registry, localization targets, necessary schemas and the shared frontend reader. Load them selectively for calculations, not in full whenever a screen opens. Separate tradition screens and new images are outside this stage. Do not silently degrade when an old set lacks required references: report that a new set must be prepared.

## 4. Evaluation model

Distinguish two questions:

1. **Can the required object be acquired/selected in the relevant context with this DLC set?**
2. **Does a particular empire currently have that object?**

The stage proves restrictions on the first question. If DLC excludes every eligible route to an object, a positive possession condition becomes `false`. Otherwise possession remains `unknown`, because no empire profile was selected. DLC availability does not make `has_origin`, `has_tradition` or a similar condition `true`.

Retain `true` / `false` / `unknown` for conditions, plus DLC causality and evidence. Compare evaluation with the same graph when DLC states are unknown. An independent restriction is not a DLC restriction. In particular, an empty provider set caused by an indexing problem does not prove DLC unavailability.

A field preventing empire-creation selection is not a universal prohibition on an object's existence. `playable`, `selectable`, `potential`, `possible` and `species_potential_add` have different contexts. Species modification requirements do not prove that an encountered species lacks a trait; `ai_playable` is not an additional player requirement. Every propagation of restrictions must have an explicitly described basis in its rule.

Existing hiding through a DLC-dependent zero weight multiplier remains a separate display rule. It does not prove that owning the technology is impossible and does not automatically propagate through `has_technology` or to descendants.

## 5. Object traversal rules

Proposed rule families:

| Condition/relation | Reference resolution and boundaries |
| --- | --- |
| `uses_ship_category = ID` | Category in `ship_categories`; providers in `graphical_culture` through `ship_kinds`. Evaluate `selectable` for a playable empire. Eligible providers form an OR. Do not make `randomized` an additional mandatory condition for manual selection. |
| `has_origin = ID` | A `civics` object with `is_origin = yes`; confirmed restrictions on origin selection. |
| `has_civic` / `has_valid_civic` | A `civics` object of the appropriate type. Missing DLC may exclude both cases, but model availability proves neither possession nor validity. |
| `has_authority = ID` | `authorities`; only restrictions applicable to the authority and evaluated context. |
| `has_ascension_perk = ID` | `ascension_perks`; acquisition conditions in `potential`/`possible`, including references to other perks and traditions. Current-state requirements remain unknown. |
| `has_tradition = ID` | `traditions` and every category referencing the ID through `traditions`, `adoption_bonus` or `finish_bonus`. Tradition requirements and the chosen category route form an AND; alternative categories form an OR. |
| `has_trait`, species class/archetype checks | `traits`, `species_classes`, `species_archetypes`, considering species/leader scope and acquisition method. A ban on selecting a portrait or adding a trait is not a ban on possessing that species. Unconfirmed implications remain unknown. |
| Technology and other object references | Preserve and inventory them. Evaluate only through a confirmed availability rule, not card visibility or the selected `parent_tech`. |

Verify restriction fields for each group against sources before enabling them. Government requirement syntax (`origin = { value = ... }` and similar forms) differs from normal triggers and needs a separately configured handler. Do not treat every `value` as a reference.

For each route distinguish an absent field, missing object, ambiguous ID and unsupported shape. An absent optional field does not prohibit an object. An unresolved reference is `unknown` with diagnostics; conflicting unique IDs are a set error. Multiple categories or providers of one ship category are valid alternatives, not ID conflicts.

Do not turn `tradition_swap`, `advanced_authority_swap` and similar constructs into independent objects based solely on `name`. Preserve the variant's base relation, activation condition and inheritance. If its impact on availability is unconfirmed, report an unresolved route; disabling the variant's DLC does not prohibit the entire base object. A graphics `fallback` alone does not prove inheritance of gameplay restrictions.

## 6. Recursive traversal

Recursion is mandatory at two levels:

- **Within conditions:** preserve nesting, operators and scopes down to leaf conditions.
- **Across objects:** resolve a reference through the manifest index, select configured target fields, recursively traverse their conditions and further references.

Shared pipeline: selected technology variants → source availability/zero-weight conditions → required objects → restrictions and providers → visibility → existing parent/child selection. Insertion history and metadata are not executable conditions. Already expanded scripted triggers do not need another expansion pass.

Evaluate `AND`, `OR`, `NOT`, `NAND`, `NOR` according to the confirmed stage-20 semantics at any depth. A false required AND member establishes failure despite unknown siblings. OR is false only when all branches are false. Preserve negation. Unsupported operator forms remain unknown and are diagnosed.

Propose a handler for trigger-context `if` / `else_if` / `else`: a known guard selects a branch; an unknown guard requires evaluating every still-possible outcome, with a known result only when they agree. Having no executed branch adds no restriction. Do not apply this to effects. Constant-threshold `calc_true_if` can use bounds on true conditions: from the number of `true` children to `true + unknown`; the comparison is known if it agrees across the entire range. Complex thresholds remain unknown.

Scope transitions and quantifiers use explicitly supported rules only. For `any_*`, absence of a satisfying object can only be proved when the condition is impossible across the whole eligible domain. A possible object does not establish actual possession. Do not extract `host_has_dlc` from an unknown wrapper and apply it to the parent independently of the wrapper's semantics.

The diagnostic traversal still visits unknown subtrees to discover unhandled references/DLC checks. These observations support reporting, not hiding evidence.

## 7. Cycles and reuse

A graph node is identified by database kind, object ID/address, evaluation purpose, variant and context. Track the current recursion path separately from the shared cache: a repeated active-path node is a cycle; a completed node is reusable.

A cycle is not `false`. Cyclic regions start unknown and are refined to a stable result using proven restrictions. An external DLC restriction may resolve part of a cycle; a cycle without sufficient evidence remains unknown. An interim `unknown` encountered on a back edge must not be cached as the final answer for all other requests. Results must not depend on technology/object traversal order.

Configure limits for depth, visited nodes and refinement steps. Reaching a limit produces a specific diagnostic and an unknown result for the unfinished branch; a condition independently proved by another branch may retain its value. Do not silently truncate traversal or treat incomplete evidence as a restriction.

Read and hash-check a document once per necessary snapshot through the existing reader. Keep repeated conditions and indexes in memory. Reuse the reference graph across DLC profiles; evaluation results depend on the complete normalized profile. Existing storage persists completed combinations; no additional persistent cache database is needed in this stage.

## 8. Configuration

Keep `config/enrichment/dlc.json` as the entry point. Proposed expandable rule directory: `config/enrichment/dlc/`, with separate `ship_categories`, `empire_objects`, `ascension` and `species` groups; shared traversal/context settings remain in the root configuration. Configuration declares connected filenames/paths; do not discover rules by loading every JSON file in a directory.

Each rule describes:

- a stable ID, enabled flag and supported handler;
- predicate, supported value shape and context;
- target database kind, object selection, restriction fields and their combination/order;
- provider/membership relations and alternative-route rules;
- applicability to selection, acquisition or possession;
- a supporting definition/documentation reference and diagnostic code.

Code retains traversal, logic, reading and verified semantic handlers. Configuration neither executes Python nor introduces a universal programming language. An unknown handler ID or invalid configuration fails before calculation. A game predicate without a proven rule remains an unknown game condition, not a parser error.

Existing configuration mechanisms hold new source/target/output paths and limits. Change schemas in the generator and regenerate them. Do not restore a bulky whitelist of every game command.

## 9. Combinations and interface

Keep existing local API operations and explicit Apply. Python consumes the new references and rules. The frontend receives prepared visibility/relations and atomically updates the snapshot; no second condition evaluator in TypeScript.

Result revision includes implementation/semantic version, traversal rules, context, selected variants, DLC profile and revisions of all contributing catalogs. Multi-provider relations must include the complete relevant index revision: adding a provider invalidates earlier evidence even when previously read objects remain unchanged. Input revisions do not include this calculation's own output enrichment.

Stage-20 combinations cannot be presented as results of the new rules. A revision mismatch requires recalculation; errors retain the previous published set. Preserve sources, localization and existing technology variants.

Do not propagate hiding through `parent_tech`/`children`: these are placement relations, not the full requirement formula. Keep the existing independent-root behavior when no visible parent candidate remains, unless the technology's own unavailability is separately proved. Static acquisition routes are covered by the addendum; full event-history simulation is not required.

## 10. Evidence and coverage

Extend calculation reports with the technology source/field, traversal sequence, rules/contexts, objects/addresses, DLC and selected states, node results and baseline. Evidence for a false OR/provider set must cover every branch. Shared parts may be stored once with node references; cycles do not expand into infinite JSON.

Distinguish direct DLC restrictions, indirect restrictions, zero DLC weight, no proven restriction and unresolved routes. Diagnose unknown commands/wrappers, unsupported contexts, missing references, incomplete provider domains, cycles and limits. Do not confuse verified-file counts with semantically handled conditions.

A separate coverage report includes every catalog DLC, discovered direct/indirect dependencies, affected-technology counts and unresolved routes with reasons. When no impact is found, state “no dependencies found in the investigated scope,” not “this DLC does not affect the game.” Include cosmetic DLC as well.

Covering all DLC does not mean executing every game command. A known DLC route that remains unsupported is an explicit coverage gap; a general successful test count cannot conceal it. Before acceptance, either resolve each such route within the agreed scope or present the concrete example and limitation to the user.

## 11. Validation and acceptance

Useful synthetic scenarios:

1. A deep object chain, a shared node used by several technologies and each document read once.
2. Nested AND/OR/negation, an independent restriction, unknown siblings, conditional branches and `calc_true_if` bounds.
3. Several providers: all blocked; one available; one unknown; incomplete domain. Provider order does not affect the result.
4. Ascension perk → tradition → category; adoption/finish bonuses; a tradition in several categories.
5. Base-object independence from DLC gating only its variant; scope preservation; no mistaken propagation of `ai_playable`, graphics fallback or species-modification restrictions.
6. Direct/indirect cycles, a cycle with an external DLC restriction, traversal limits, unresolved references and ID conflicts. Reordering inputs does not alter results.
7. Identical-input caching; changes to rules, profile, definitions or provider membership invalidate reuse. A hidden technology's zero weight does not automatically make `has_technology` false.
8. Unchanged source AST, parent/child integrity, failure/cancellation before publication, no game access during DLC Apply.

Real-set matrix: all DLC enabled; all disabled; each DLC individually disabled from the full set; each individually enabled from the empty set; additional mixed profiles for discovered multi-DLC AND/OR/negation. Read DLC count from the catalog and deduplicate identical profiles. This is a targeted matrix, not enumeration of all `2^N` combinations.

Run the matrix against one prepared graph without publishing a complete snapshot for every profile. Separately exercise API → publication → frontend opening for selected reference profiles. Without BioGenesis, verify removal of the weaver weapon branch through ship-category evidence; enabling the DLC must not itself select a biological empire.

Verify RU/EN for new objects, opening a 28-kind set, selective catalog loading, repeat Apply, cancellation and preservation of the previous tree on error. Measure indexing, traversal/recalculation, memory, documents read and publication. Correctness requires explainable decisions and no false prohibitions, not a predetermined visible-technology count.

## 12. Implementation sequence

After approval: import three references → verify and record routes/semantics → recursive evaluator and diagnostics → revisions/combinations/API → DLC matrix and browser acceptance → RU/EN guide and changelog.

The intermediate main implementation added three sources, their configuration/schemas, the recursive graph and diagnostics, preparing a 28-kind set. The scope was then expanded to 30 kinds. The 86-profile matrix and selected publications through service operations without an HTTP listener were repeated for the addendum. No services were started; browser acceptance is not claimed.

The user chose an extension following the [technology acquisition research](RESEARCH_COSMOGENESIS_ACQUISITION_EN.md). The [addendum](TZ_BACKEND_STAGE_21_ACQUISITION_EN.md) is approved and implemented: 30 kinds, acquisition index and semantic handlers. Expanded-scope results and verification limitations are in the [guide](BACKEND_STAGE_21_EN.md). Specific IDs must not replace general evidence-based rules.

## 13. Sources

- [Previous filtering](TZ_BACKEND_STAGE_20_EN.md), [reference import](TZ_BACKEND_STAGE_19_EN.md), [DLC interface](frontend/TZ_FRONTEND_STAGE_10_EN.md).
- [Empire condition glossary](semantics/EMPIRE_CONDITIONS_EN.md), [logic and context](semantics/LOGIC_AND_CONTEXT_EN.md).
- [Weaver Booster Blaster](/E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_biogenesis_tech.txt:1558).
- [country_uses_bio_ships](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/07_scripted_triggers_ships.txt:33), [DLC trigger](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:482).
- [Selectable ship set](/E:/SteamLibrary/steamapps/common/Stellaris/common/graphical_culture/00_graphical_culture.txt:1434), [NPC fallen-empire set](/E:/SteamLibrary/steamapps/common/Stellaris/common/graphical_culture/00_graphical_culture.txt:633).
- [Cosmogenesis perk](/E:/SteamLibrary/steamapps/common/Stellaris/common/ascension_perks/00_ascension_perks.txt:330), [Virtuality category](/E:/SteamLibrary/steamapps/common/Stellaris/common/tradition_categories/01_virtuality.txt:1).
- [Tradition documentation](/E:/SteamLibrary/steamapps/common/Stellaris/common/traditions/99_README_TRADITIONS.txt:1), [category documentation](/E:/SteamLibrary/steamapps/common/Stellaris/common/tradition_categories/99_README_TRADITION_CATEGORIES.txt:1).

[Русская версия](TZ_BACKEND_STAGE_21_RU.md).
