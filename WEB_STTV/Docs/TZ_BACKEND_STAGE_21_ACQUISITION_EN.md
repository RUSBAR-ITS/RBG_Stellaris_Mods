# Stage 21 — addendum: technology acquisition analysis

## Contents

- [1. Status and objective](#1-status-and-objective)
- [2. Inputs and index preparation](#2-inputs-and-index-preparation)
- [3. Acquisition routes](#3-acquisition-routes)
- [4. Calls and conditions](#4-calls-and-conditions)
- [5. Proving exclusion and coverage](#5-proving-exclusion-and-coverage)
- [6. Storage and configuration](#6-storage-and-configuration)
- [7. Integration and diagnostics](#7-integration-and-diagnostics)
- [8. Validation and acceptance](#8-validation-and-acceptance)

## 1. Status and objective

**Addendum approved by the user on 2026-11-19 and implemented.** Results and verification boundaries are in the [guide](BACKEND_STAGE_21_EN.md). The user chose to extend [stage 21](TZ_BACKEND_STAGE_21_EN.md) with technology acquisition analysis instead of completing it with a general `has_technology` diagnostic. Completed implementation work is retained; final acceptance follows verification.

Distinguish normal research draws, specially unlocked research options, immediate grants of researched technologies, and current ownership. For `has_technology`, establish only proven inability to acquire a technology due to DLC; possible acquisition does not establish current ownership.

Context: a new unmodified campaign with a fixed DLC set, a playable empire, and the selected reference combination. Console commands and manual save editing are not gameplay routes. Changing DLC after acquisition, simulating a particular campaign, timing, event probability, and resource simulation are out of scope. Effects creating NPCs do not automatically provide acquisition routes for the player.

Basis: [Cosmogenesis research](RESEARCH_COSMOGENESIS_ACQUISITION_EN.md). Zero weight on `tech_cosmogenesis_world` and `tech_cosmogenesis_escort` coexists with `add_research_option` calls from crisis levels. Simply propagating `potential` or card visibility cannot replace examination of these routes.

## 2. Inputs and index preparation

Add two regular database kinds to the main stage's 28, bringing the registry to 30:

| Variable | Directory | Kind | Identity |
| --- | --- | --- | --- |
| `CRISIS_PATHS_DIR` | `common/crisis_paths` | `crisis_paths` | Root definition key |
| `CRISIS_LEVELS_DIR` | `common/crisis_levels` | `crisis_levels` | Root definition key |

Use normal preparation, separate documents, manifest publication, RU/EN localization where keys exist, and existing priorities. Verify explicit keys and standard suffixes against game sources; do not invent text. No dedicated crisis screens are required.

Prepare a technical acquisition index from configured sources: recursive `common`, `events`, and `prescripted_countries`, with the `.txt` extension. This is a script relation index, not additional user-facing catalogs of every game entity. Insertion/function directories remain libraries: definitions are not independent execution entry points.

A textual inventory of current sources found six acquisition-command families in 131 files: 84 event files and 47 files under `common`. The latter include currently unimported `council_agendas`, `country_focus`, `patrons`, `solar_system_initializers`, `specialist_subject_perks`, `tradable_actions`, `astral_actions`, and `federation_perks`. This inventory indicates source composition, not executability. Working report: `data/stage21/acquisition_source_inventory.json`; counts are not constants.

Index callers even when they contain no direct grant command. Text searches are research tools, not the production method for proving absence of acquisition routes. Reuse the existing parser, libraries, and substitutions. Reuse the same preparation result for already processed documents; apply the same stages to additional files. A parse failure does not mean a grant is absent.

Preserve definitions, calls, and necessary fragments with conditions and scopes. Check the sufficiency of the compact representation against source AST: dropping an unknown fragment must not turn an unknown route into an absent route. On failure, retain the unknown fragment and reason in coverage; corruption of the technical index itself blocks publication.

## 3. Acquisition routes

| Route | Analysis required |
| --- | --- |
| Starting technology | `start_tech`, separate `starting_potential`, applicable restrictions and confirmed initial-grant context. Do not treat `start_tech` as a universal condition bypass. |
| Normal research | `potential`, technology prerequisite logic, and eligibility for a weighted draw. Do not calculate probabilities or present availability. Unsupported weight changes remain unknown; a base zero does not close special routes. |
| `add_research_option` | Reachability of the effect and its recipient; it opens an option rather than establishing completed research. Do not require positive normal weight. Confirm engine checks after opening separately; they do not replace call conditions. |
| `give_technology` | Direct researched-technology grant in the target country scope. Do not automatically add `potential` without confirmation that the particular mechanism checks it. |
| `add_tech_progress` | Progress change; investigate opening/completion separately. The command alone does not establish a complete grant or permission to research. |
| `add_random_research_option` | Category/area/tier, selection parameters, `fail_effects`, and confirmed engine rules. Unknown selection preserves possible targets and uncertainty. |
| `copy_random_tech_from` | Source, recipient and target constraints; local documentation requires positive weight and `potential`; `progress` distinguishes a research option with progress from a complete grant. Donor availability is not player availability. |
| `copy_techs_from` | Donor, recipient, exclusions, and confirmed copying restrictions. Do not interpret copying as an unconditional grant of every database entry. |

For each semantic rule, record its primary source and confirmation boundary. Compare local log descriptions against actual uses; disputed engine behaviour remains unknown until confirmed. Do not classify every similarly named command as a grant.

Normal and special routes combine with OR. Research prerequisites and restrictions of the normal route do not automatically apply to direct grants. Within a route, mandatory restrictions combine with AND while retaining original OR groups and negation.

## 4. Calls and conditions

Build reverse references from acquisition sites to callers and valid entry points; an effect definition does not prove it is called. Adding or removing a caller changes the proof revision.

The first required chain is `ascension_perk.on_enabled` → `activate_crisis_progression` → `crisis_path.levels` → `crisis_level.on_unlock` → acquisition effect. Preserve level order and consider perk selection restrictions, level `allow`, and preceding stages. Currency/empire state remains unknown unless determined by DLC. Resolve `has_crisis_level` through this model; do not guess the current empire's level.

Declare additional supported entry types separately: enabling a tradition/perk, a configured object effect, an automatic event, an `on_action`, an explicit event call, and choosing an event option. Each entry type has its own condition fields and scope. `is_triggered_only = yes` requires a calling route; an event definition is not such a route. An unsupported entry is an unknown route with a source address, not an unconditional entry or an absent route.

For `if` / `else_if` / `else`, analyse effect execution guards and branches. Do not apply the trigger evaluator's result-consensus rule to effects. For random lists, preserve every potentially executable alternative without calculating probabilities. State-changing effects before checks cannot be ignored: if an unsupported change can affect a result, that result is unknown.

Distinguish `root`, `from`, `prev`, `owner`, recipient, and donor. Changing country scope does not automatically preserve the original country's properties. `host_has_dlc` is global to the fixed profile, whereas ethics, flags, species, and technology checks depend on scope and time. Quantifiers require a confirmed domain.

Do not expand prepared insertions again. Expansion history provides provenance and library relations, not another executable AST. Unresolved parameters/dynamic targets preserve uncertainty; if they cannot be narrowed, they potentially concern every suitable technology. Refine cyclic calls conservatively; a cycle without an independent basis does not prove exclusion.

## 5. Proving exclusion and coverage

Evaluate possible acquisition using all identified routes and their coverage status. For positive `has_technology`:

- every route is proven impossible and target-specific coverage is complete → `false`;
- at least one route is possible or unknown → `unknown`;
- incomplete coverage, an unknown dynamic grant, unconfirmed engine semantics, or recipient scope → `unknown` with a reason.

Even confirmed possible acquisition does not produce `true` for actual ownership. Apply negation using the shared logic, not by reversing the entire technology result.

Coverage includes source composition, recognized mechanisms, all calling routes, and dynamic-selection rules. An empty ID search, absence of a call in loaded files, false `potential`, or zero weight is individually insufficient. A generic unknown grant must not disappear merely because its ID text did not match the target.

As in the main stage, compare against the graph with unknown DLC states to distinguish DLC causality from independent exclusions. Proof must cover all excluded acquisition alternatives. Unproven assumptions about “normal game behaviour” are not default rules.

## 6. Storage and configuration

Proposed configuration groups: `config/enrichment/acquisition/sources.json`, `effects.json`, and `entries.json`, explicitly referenced by `config/enrichment/dlc.json`. Configure paths, extensions, handlers, supported forms, target fields, scopes, evidence sources, and limits. Code contains small semantic handlers; a universal registry of all commands is not reintroduced. Do not hardcode Cosmogenesis IDs into rules.

Store the technical index in separate JSON documents per source file, preserving indentation and line breaks. A proposed `acquisition` manifest section declares version, context, source coverage, documents, hashes, and target/call indexes. This is internal set enrichment, not a 31st user-facing database kind. Declare its structure in generated JSON Schema.

Publish index documents and all 30 kinds as one consistent snapshot. A set missing a required or current index needs explicit preparation; Apply neither reads the game nor launches generation. The frontend accepts the new manifest revision and ignores semantic index content during normal opening while retaining snapshot consistency.

Use existing parallel preparation and insertion libraries. Once prepared, reuse the index across DLC applications and keep the graph in memory. Revisions include sources and their composition, effect/entry rules, parser/library/analysis versions, variants, and context. Verify hashes on read; full audit remains separate. Adding a grant file invalidates earlier coverage proofs even if previously read files are unchanged.

## 7. Integration and diagnostics

Acquisition analysis feeds `has_technology`, followed by existing filtering and parent selection. `parent_tech`, card location, and current visibility are not acquisition evidence.

Reports preserve the source/address and type of acquisition, recipient, calling chain/entry, conditions, results, technology relations, and coverage. Store shared graph parts once. Distinguish “unlock route”, “possible acquisition”, “ownership unknown”, and “proven DLC exclusion”.

Diagnose unsupported mechanisms/entries, unresolved targets/scopes, incomplete sources, unknown engine behaviour, absent callers with an incomplete index, cycles, and limits separately. Coverage gaps and their actual effect on visibility are distinct report fields. Preserve atomic publication, cancellation, and the previous snapshot on failure.

## 8. Validation and acceptance

Synthetic cases: a direct DLC gate plus an independent grant; zero weight with a special unlock; multiple callers with different DLC; a sole open alternative; direct grants without normal prerequisites; unknown/dynamic targets; a different recipient; nested effect branches; random alternatives; state changes; level order; cycles; incomplete indexes; new grants/files invalidate cache; cancellation never publishes half a snapshot.

The real run must explain both examined Cosmogenesis routes and all eight consumers, rather than merely locate IDs. Verify the six Lathe technologies' own restrictions and the alternatives for missiles/torpedoes. Do not conceal an unhandled route: report its source and the specific obstacle to proof before final acceptance. Expected unavailability of the two technologies is not a substitute for evidence.

Repeat the main stage's DLC matrix over one graph. For selected profiles, exercise recalculation → publication → frontend opening. Verify all 30 kinds, new-reference localization, selective reads, no game access during Apply, and no frontend reads of the technical index for the ordinary tree view.

Measure index preparation cost, size, graph building, repeated evaluations, memory, and documents read separately. Report parsing coverage and semantic coverage separately. In-game engine verification remains the user's responsibility; describe any necessary scenario precisely and never present unperformed checks as passed.

[Русская версия](TZ_BACKEND_STAGE_21_ACQUISITION_RU.md).
