# WEB_STTV specification. Technology acquisition and page readability

## Contents

- [Scope and baseline](#scope-and-baseline)
- [Correction register](#correction-register)
- [Named rewards and starting eligibility](#named-rewards-and-starting-eligibility)
- [Chain entry and recipient](#chain-entry-and-recipient)
- [Debris research](#debris-research)
- [Ordinary research and indirect access](#ordinary-research-and-indirect-access)
- [Random selection and general effects](#random-selection-and-general-effects)
- [Condition wording and source names](#condition-wording-and-source-names)
- [Long branches](#long-branches)
- [Import and server data](#import-and-server-data)
- [Acceptance across all technologies](#acceptance-across-all-technologies)

## Scope and baseline

Draft for approval. A player reading a card tooltip or a technology page should be able to tell how to research the technology, who can receive it, under what conditions, and which facts depend on the current game. This specification covers every row in the audit. The detailed tables for the first iteration form its appendix. Sections may be delivered separately and tracked in one results register. [First-iteration appendix](TZ_TECHNOLOGY_ACQUISITION_FIXES_1_EN.md) · [Full audit](TECHNOLOGY_ACQUISITION_AUDIT_EN.md) · [Inventory by ID](TECHNOLOGY_ACQUISITION_INDEX_EN.md)

The baseline is Stellaris 4.5.4 (1b4f) with all DLC, 679 base technologies and 1,358 RU and EN pages. At least one named source appears for 478 technologies. A research option opens for 289, a fully researched technology is granted for 248, and research progress is awarded for 298. A technology can belong to all three groups. Among the 201 technologies with empty reward sections, 156 have one positive weight, 27 omit weight and are starting technologies, 16 have one zero weight, and two declare weight twice. Of 97 technologies with one explicitly zero weight, 81 already have a source. Review every group. The 206 `technology_swap` blocks have no separate base pages in this snapshot.

Retain the three reward sections for unlocking a research option, immediately granting a researched technology, and adding partial research progress. Explain ordinary draws, starting eligibility and indirect access alongside the applicable availability, prerequisites or weight. If a visible technology has a source that requires a disabled DLC, name that DLC and mark it as disabled. The existing tree rules govern parent selection and card placement.

## Correction register

Counts refer to the baseline. The default unit is a technology. Count overlapping groups by ID. The last column gives the observable acceptance condition.

| Audit finding | Coverage | Acceptance condition |
|---|---:|---|
| Scripted rewards | 9 | Each of the seven precursor secrets awards +10% in the applicable outcome. Boarding Cables receives a full grant and the Materiality Engine a research option. |
| Debris research | 6 priority technologies out of 110 | Each supported candidate identifies a carrier and the conditions for analysis. A prohibition excludes the affected route. |
| Conditional starting grants | 19 of 42 starting technologies | All 19 show actual starting eligibility. The remaining 23 have no empty eligibility block. |
| Entry and recipient | 112 / 52 / 126, 222 distinct IDs | Each flagged path identifies the entry and recipient status or states exactly what is unknown. NPC grants are distinguished. |
| Ordinary research and indirect access | 10 with positive weight and a zeroing rule | Explain the zeroing rule, conditional additions and required research. Attribute a predecessor's event to the applicable step. |
| Random and general rewards | 79 / 14 / 1 / 34 sites | All four commands have a recipient, candidate domain and actual type of outcome. |
| Flag meanings | 327, including 189 with identical wording for distinct conditions | Readers can distinguish supported circumstances on the same page. Scope and negation survive. |
| Condition arguments and objects | 58 / 133 / 171 RU and 177 EN | Identify the check, object and value. Use the known role for a campaign-specific name. Measure visible wording and diagnostics separately. |
| Source names | 106 without a type, 30 with identical titles, 62 with an unnamed step | Readers can distinguish sources by type, action or branch, including all three arkship agendas. |
| Length and nesting | 50 with at least 500 text nodes, 72 at depth 10 or more | The summary gives the gameplay outcome. Expanded details recover every condition and outcome. |
| Conflicting base weights | 3 | Preserve both values and declaration order, and state whether the effective weight is known. |

## Named rewards and starting eligibility

Apply common traversal rules to the definitions. Trace project activation, successful completion and 17 progress sites for the seven minor artifact actions. Count alternative responses separately. For Boarding Cables, trace Captain Inax's ship being disabled, both recipient selection branches, and the grant in `after`. For the Materiality Engine, retain the situation outcome, reintegration, the 30-day delay, and the response that opens the research option. Check the recipient's origin in both cases. The appendix tables of IDs, branches and expected values apply to both languages. [Reward and starting eligibility tables](TZ_TECHNOLOGY_ACQUISITION_FIXES_1_EN.md)

For `start_tech = yes` with `starting_potential`, show a separate “Starting eligibility” explanation. General `potential` applies in its own context. The Subspace Drive control requires First Contact and one of four civics. Together with the nine rewards and six debris candidates, this accounts for all 16 priority technologies with zero weight and empty sections.

## Chain entry and recipient

Trace each execution from the player action or in-game condition through calls, outcomes, responses, delays and scope changes to the command. Resolve the initiator, the situation or object owner and the empire receiving the outcome separately. Follow `from`, `prev`, `owner`, `target` and saved targets at the actual call site. Different entries to one command can have different recipients, DLC or conditions.

Review 536 records with an unconfirmed entry, 685 with an unresolved recipient and 801 with a recipient question in a system initializer. For each, record the game ID, command and branch address, entry, evidence for the recipient, and conclusion. A supported player route qualifies for the reward section. A confirmed NPC grant, unreachable test or illustrative tooltip receives the corresponding exclusion reason. State the condition when the connection depends on campaign state. If evidence is insufficient, identify the specific unknown transition or recipient.

Controls include the 14 Scion gift technologies through `origin.21` and the `fervent_belief` branch from situation completion through `preftl.2005` to `preftl.2070`. For the latter, follow the observer, the observed empire and the beneficiary separately. [Source evidence](TECHNOLOGY_ACQUISITION_AUDIT_EN.md)

## Debris research

Trace a component's technology prerequisite to a fixed ship carrying it. Match the component against actual section equipment or a required component in the design, then find an executable ship creation site, including expanded effects. Account for `is_reverse_engineerable`, a fleet-specific `spawn_debris` prohibition, known reverse engineering protection, debris policy, and the requirement for the technology to be unknown. A prohibition on one fleet excludes that source alone.

For Mining Drone Lasers the text should explain that analyzing suitable debris from an ancient mining drone equipped with the laser can advance research. The baseline defines 10% base progress for an eligible component via `DEBRIS_ANALYZED_TECH_PROGRESS`. Keep the basis and game version for the value. Debris drop probability, the outcome of a specific battle and engine selection among several component prerequisites require separate evidence. [Game constant](E:/SteamLibrary/steamapps/common/Stellaris/common/defines/00_defines.txt:922) · [Carrier inventory](TECHNOLOGY_DEBRIS_AUDIT_EN.md)

Review all 110 candidates. The six priority IDs are `tech_mining_drone_weapon_1`, `tech_space_cloud_weapon_1`, `tech_extradimensional_weapon_1`, `tech_scourge_missile_1`, `tech_swarm_strike_craft_1` and `tech_nanite_repair_system_synth_queen`. Another 11 also have empty sections. The other 93 already have a different source. Preserve existing routes for `tech_dragon_armor`. Exclusion and uncertainty controls are Inax's fleet with debris disabled, Subspace Drive with reverse engineering disabled, a component without an identified carrier, a component with several prerequisites, and a station-only creation site. Record the evidence status for each such link. Limit claims about procedural ship designs and unknown debris composition to the available evidence.

## Ordinary research and indirect access

Read the prerequisite graph, `potential`, `allow`, base weight and applicable ordinary research weight modifiers together. Preserve AND, OR, negation, comparisons, and the conditions on `factor` and `add`. Distinguish AI choice weight. Describe campaign-dependent conditions and distinguish relative weight from probability.

For Omega Theory (`tech_akx_worm_3`, weight 60), show both mandatory technologies and their research options through the Horizon Signal. A modifier zeroes the initial weight of 60 for each prerequisite. Give a short explanation and links to both predecessors on the Omega Theory page. Traversal must account for alternatives, shared predecessors and cycles. Preserve the conditional `add = 100` for Xeno-Linguistics. The current display exception for `crystal_armor_1_weight` continues to apply.

Treat missing weight, an explicit zero and multiple declarations separately. Show 0 and 70 for `tech_dyson_swarm`, 0 and 50 for `tech_dyson_gun`, and 0 and 70 for `tech_orbital_arc_furnace` in details, in source order. Mark the effective value as undetermined until engine precedence is established. [Control definitions](TECHNOLOGY_ACQUISITION_AUDIT_EN.md)

## Random selection and general effects

Review all sites of the four commands, including reusable effect definitions. Associate each definition with an actual invocation, branch and recipient. Respect command-specific filters and defaults. A technology page may describe a conditional opportunity when the technology can be matched to the selection rules. State any campaign-dependent conditions explicitly. If no individual candidate can be established, record the mechanism, reason and an example entry in the audit.

| Command | Sites | Meaning and control |
|---|---:|---|
| `add_random_research_option` | 79 | A random research option from the eligible pool. Retain area, category, tier, selection flags, prerequisite handling, additional progress and empty-pool outcome where specified. Control case — a tier-two engineering option with 99% progress. |
| `copy_random_tech_from` | 14 | Select from a different empire's knowledge with positive weight and satisfied `potential` for the recipient. Omitting the progress parameter grants the technology. Providing it opens the option with the stated progress. Control case — an operation with 10% progress. |
| `progress_all_researches` | 1 | Advance the empire's current research. State that work on the technology must already be in progress. |
| `copy_techs_from` | 34 | Copy from a specified empire to the beneficiary, respecting exclusions, weights and modifiers. Check NPC initialization paths. |

Distinguish progress percentage, relative branch weight and selection probability in the text. If an outcome opens a research option and grants partial progress, link both entries to that outcome. [In-game call sites](TECHNOLOGY_ACQUISITION_AUDIT_EN.md) · [Game effect documentation](<C:/Users/RUSBAR/Documents/Paradox Interactive/Stellaris/logs/script_documentation/effects.log>)

## Condition wording and source names

- **Flags.** Map each check to the relevant set, clear or expiry site, owner and reachable branch. Check both Nemesis and BioGenesis projects for `crisis_special_project_4_complete` on 98 pages. Name the project when the branch establishes it. Keep both possibilities when both apply. For every generic or duplicate label record its distinguishing fact or the precise limit of the evidence.
- **Arguments.** For `current_awareness_level`, `species_portrait`, `inverted_switch`, `check_variable` and other flagged operators, recover the operand, comparison, value, branches and scope. Trace saved targets to their assignment. For Ordered Retreat explain whose value is compared against 100 and what it measures to the extent the script establishes this. A campaign-specific planet or ruler name may be described by role. Record missing translations separately. Distinguish the 58 pages with the visible fallback from the 61 with an unknown-condition diagnostic in each language.
- **Sources.** Give the type and action in the short text. Use a confirmed entry for a hidden handler and a supported distinction for identically named sources. Check the civilian, military and science arkship council agendas, and the development focus reward. Keep the key, address and original branch in technical details.
- **Localization.** The server resolves game names and inserts values into RU/EN templates. The visible text retains scope, logical nesting, polarity, numbers, icons and colors. Use distinct diagnostic reasons for a campaign-dependent name and a missing translation. [Condition text rules](TZ_CONDITION_TEXT_EN.md) · [Blue Lasers review](../../../Docs/frontend/TECHNOLOGY_PAGE_READABILITY_EN.md)

## Long branches

Show the action, recipient, reward type and amount, if applicable, first. Conditions that enable a source and those that select an individual outcome remain available in keyboard-accessible expandable details on both the tooltip and the page. A shared fragment may be displayed once only when its meaning, scope and applicability match across the grouped branches. Preserve AND/OR distinctions, responses, relative weights, delays, DLC and each outcome's reward.

Controls are Temple of Transportation (22,896 text nodes, depth 14) and Ordered Retreat (22,603 nodes in one language). For Blue Lasers, the summary must distinguish different progress awards and a full grant. Every outcome in the baseline response must remain traceable to its conditions in the details. The table thresholds select the usability review sample.

## Import and server data

1. Add two complete directories to the parser and loader profiles — `common/artifact_actions/*.txt` (28 definitions) and `common/global_ship_designs/*.txt` (39 files, 436 design names in the baseline). Import each definition into its own `artifact_actions` or `global_ship_designs` document with a matching provenance record. Use the root key for an action and the inner `name` field for repeated `ship_design` roots. Match IDs and addresses from the source file through MongoDB. Report conflicting definition names before any data is lost. Check the versioned debris coefficient against the game definition on snapshot updates. [Parser profile](../../../config/parser_sources.json) · [Loader profile](../../../config/loader.json)
2. The server derives links from imported documents and uses the existing source index and `technology_tooltips` documents. Extend the earlier index scope to debris and dynamic effects. The revision must cover relevant collections, provenance, rules and localization at the layer where they affect the result. Serving a prepared document again must avoid traversing the game collections. [Source index](../sttv_server/progress_sources.py) · [Earlier research progress specification](TZ_TOOLTIP_RESEARCH_PROGRESS_EN.md)
3. The tooltip and page use the same `POST /api/trees/technology-tooltip` result. The frontend presents the summary and details in the selected language. Acquisition rules, localization lookup and source evidence belong to the server. The existing source-index, tooltip-collection and combined derived-data reset operations must cover the added information and preserve imported documents. [Server operations](../sttv_server/http.py)

## Acceptance across all technologies

1. Reproduce the result on an empty test database using the project profiles, including localization. Reconcile both added directories. Store before-and-after reports under `TMP/WEB_STTV/<run>/reports/`. For each ID and register row record the original observation, new result, evidence link and any outstanding question. Count pages, distinct technologies and command sites separately.
2. Repeat the baseline comparison of 1,084 direct named commands in the base game and DLC, and separately verify expanded insertions. Six sites in two test events remain negative controls. Compare source ID, recipient, reward type, branch address and percentage. Once the nine scripted sources are fixed, the first-iteration expectation is at least 487 technologies with a named source on this snapshot. Explain each addition, disappearance and change in meaning in final acceptance.
3. Open **all 679 technology pages in both Russian and English** in the browser with all DLC enabled. Check rewards, availability, weights, collapsed summaries and expanded text. Verify page and tooltip agreement for the same input. Also test all DLC disabled and a mixed selection with the source's DLC disabled. Test initial preparation, warm reads, individual and combined resets, and rebuilding.
4. Preserve previously fixed cases. The main text must remain free of raw event IDs, `on_*`, `|||` grammar tables, technical substitutions and scope paths, unresolved icons and literal newline escapes. Check Boolean `has_deposit = no`, mutually exclusive success/failure captions, the active event and the starbase module on Blue Lasers. Verify established routes for Frozen World Habitats, Trinary Computing, Alloy Fossilization, Thruster Bio-integration and Ordered Retreat. [Original readability audit](../../../Docs/frontend/TECHNOLOGY_PAGE_READABILITY_EN.md) · [Follow-up findings](TECHNOLOGY_ACQUISITION_AUDIT_EN.md)
5. Report a disposition for each register row and list outstanding cases by ID. Close a confirmed defect after checking the corrected output against its source and page. For a genuinely indeterminate outcome, name the unknown condition and the check that could resolve it. Record the user's in-game checks separately — actual post-battle debris, random selection in a particular campaign and engine precedence for duplicate weight declarations. The page sweep verifies rendering and script-supported paths.

[Русская версия](TZ_TECHNOLOGY_ACQUISITION_FIXES_RU.md)
