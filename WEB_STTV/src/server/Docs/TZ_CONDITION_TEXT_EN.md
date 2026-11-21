# WEB_STTV specification. Describing game conditions in plain language

The WEB_STTV server owns the rules. The technology page and tooltip are the first consumers. Define the meaning of a game construct once and reuse that definition wherever the construct has the same meaning.

## Contents

- [Scope and baseline](#scope-and-baseline)
- [Shared renderer contract](#shared-renderer-contract)
- [Tooltip collection and reset](#tooltip-collection-and-reset)
- [Adding a rule](#adding-a-rule)
- [Logic and subjects](#logic-and-subjects)
- [Language and incomplete information](#language-and-incomplete-information)
- [Conditions in acquisition paths](#conditions-in-acquisition-paths)
- [Reference cases](#reference-cases)
- [Delivery and acceptance](#delivery-and-acceptance)
- [First-stage inventory](#first-stage-inventory)

## Scope and baseline

The server produces RU/EN descriptions of **what must hold, for which subject, and under which alternatives**. Initial integration covers `prerequisites`, `potential`, `allow`, weight modifier conditions and the guards of all three acquisition methods. The same call must accept a building, situation or event condition. Existing functions determine availability, select sources and build the tree. Describing a requirement does not imply that the player satisfies it.

The baseline covers 679 base technologies in v4.5.4 in both languages. On 379 pages a condition loses its operand or body. On 40 a boolean becomes a deposit name. On 119 both success and failure captions are displayed. Currently `Content.unknown` returns the original node and `ProgressContent.unknown` displays just its key. Reuse the existing recursive traversal, server localization lookup and shared frontend component. [Audit](../../../Docs/frontend/TECHNOLOGY_PAGE_READABILITY_EN.md) · [Technology conditions](../sttv_server/technology_tooltip.py) · [Reward conditions](../sttv_server/progress_content.py) · [Display component](../../frontend/ui/composite/TechnologyTooltipDetails.tsx)

## Shared renderer contract

| Input | Owner and purpose |
| --- | --- |
| Parsed script node or ordered list | The caller supplies original operators, values and children. For a list it identifies the containing role, e.g. prerequisites, branch guards or command arguments. |
| Context | Originating object type and ID, section, current subject and established call-chain roles. Resolve `from` at the call site. Event entry and response conditions can have different subjects. |
| Presentation | Language, reference mode and known settings such as enabled DLC. A known DLC selection supplies the DLC annotation. It provides no evidence about active events or an empire's stockpile. |
| Provenance | Document and node address where available. A synthetic branch guard refers back to its call site or original branch. |

Return ordered nodes for the existing API and separate diagnostics. A node carries its kind (condition, group, scope or caption), localized text and any children. References retain object type and ID. Groups retain their operator. Subject, comparison, typed arguments and polarity are available during processing before choosing a phrase. The caller supplies the outer section, reward heading and effect amount. The frontend displays the text, nesting, emphasis and game icons. Page and tooltip receive identical content for the same settings.

For example, a negation around a single `has_active_event = { crisis.4135 }` can produce one condition with negative wording and a reference to event `crisis.4135`. An `OR` over two independent conditions produces a group with both children. Original addresses remain traceable after simplification.

## Tooltip collection and reset

The server stores prepared content in the MongoDB collection `technology_tooltips`. One document per base technology ID contains the condition structure, typed references, acquisition branches and source addresses. The page and tooltip read the same document. Localization and selected DLC annotations are applied on read. The first request for a technology uses a current document when available, including after a server restart. If it is missing or the source data or rules revision has changed, the server prepares a fresh record for the requested ID.

Add **Reset tooltip content** under **System settings → Database operations**. This action clears the entire collection and takes no technology ID. On success the collection has zero prepared documents, the client clears its tooltip cache across all languages and DLC selections, and the status bar reports the result. The loader export, built trees and shared source index are retained. The next explicit page or tooltip request creates the requested technology's document. An in-flight request started before the reset must not restore stale data in the collection or the client cache.

Resetting all built data includes this collection. Resetting the acquisition source index also invalidates the tooltip documents that depend on it. The technology page keeps its normal viewing controls. [Derived data operations](TZ_TOOLTIP_RESEARCH_PROGRESS_EN.md)

## Adding a rule

1. **Identify the construct.** A simple rule needs one entry in a shared server table giving its script key, accepted value shape, operators, domain type of its argument and phrase key. Add a contextual discriminator only where meaning actually differs. Each language has its own phrase templates with matching named parameters. The existing localization function resolves object names. [Phrase dictionary](TZ_TOOLTIP_DICTIONARY_EN.md) · [Localization key settings](../config/localization_keys.json)
2. **Select one applicable rule.** Prefer an exact key, context, operator and shape match, then an applicable general form for that key. An overloaded command can accept a boolean, number, reference, list of references or named argument block. Match script keywords and known scope transitions case-insensitively. Preserve the original case of IDs, localization keys and string arguments. Equally specific rules produce a diagnostic. Unsupported operators, additional fields and unexpected values require explicit handling.
3. **Substitute the operand.** For `has_starbase_module = <id>`, one rule declares a starbase module, looks up `sm_<id>` and uses “The station has the ‘{module}’ module”. A future module with the same form and a game translation needs no extra condition rule. For `has_deposit`, distinguish the boolean presence check from a reference to a particular deposit. Prefixes such as `has_`, `is_` and `any_` alone cannot establish semantics.
4. **Handle structured forms in code where necessary.** Use a named handler for a block with several argument roles, a filtered count or a computed operand. In `resource_stockpile_compare`, the fields `resource`, `value` and `mult` form one comparison. Preserve the operator from `value`, the unit and any computed multiplier. Interpret other children as checks only when the block's semantics allow it. Adding a routine condition should require adding its rule and translations without editing the page, parser or loader.

Proposed entries in `src/server/config/condition_rules.json` illustrate the two kinds of `has_deposit`. For this key the exact boolean literals take precedence over the reference form. Add the module name rule `sm_<id>` to the existing `localization_keys.json`. When the object declares its own title field, the server takes the localization key from that field.

```json
[
  {"key": "has_starbase_module", "operator": "=", "form": "reference", "reference": "starbase_module", "phrase": "sttv_tooltip_has_starbase_module"},
  {"key": "has_deposit", "operator": "=", "form": "boolean", "phrases": {"yes": "sttv_tooltip_has_any_deposit", "no": "sttv_tooltip_has_no_deposit"}},
  {"key": "has_deposit", "operator": "=", "form": "reference", "reference": "deposit", "phrase": "sttv_tooltip_has_deposit"}
]
```

## Logic and subjects

- In condition containers preserve implicit conjunction, explicit `AND`, `OR`, `NOT`, `NAND` and `NOR`, order and repetitions. OR means “at least one”, NAND means “not all”, NOR means “none”. Apply the agreed single-child AND/OR simplifications. For negation of one recognized predicate use the agreed negative wording or exact inverse comparison. Otherwise retain the group and all operands, including multi-child `NOT`. Empty or partially understood groups cannot make a guard unconditional. [Semantics](../../../Docs/semantics/LOGIC_AND_CONTEXT_EN.md) · [Agreed simplifications](TZ_TOOLTIP_CONDITION_SIMPLIFICATION_EN.md)
- A scope transition changes the subject inside its block. Preserve `root`, `this`, `prev`, `from`, chained paths, saved targets, optional `?` transitions and quantifiers. Two checks inside one `any_owned_…` must hold for **the same** object. `exists = owner` requires an owner to exist. `owner = { … }` applies child conditions to the owner. When the caller cannot identify the role of `from`, describe its known relation to the calling context and retain the uncertainty.
- For `if / else_if / else`, retain the current guard and exclusion of earlier branches of that chain. For `switch`, retain the selector, selected branch and condition for `default`. Distinguish a threshold, weight addition, multiplier, relative outcome weight and percentage of research progress. Zero is a meaningful value. A calculated threshold may be expressed as a formula.
- A scalar `custom_tooltip` supplies a caption. In its block form separate caption fields from actual conditions. Produce one neutral requirement in reference mode. An existing game phrase can stand for the subtree when it preserves the whole meaning. Otherwise display the actual conditions. `success_text` and `fail_text` are two presentations of the same check. The children of `hidden_trigger` retain their effect. Respect the agreed display suppression of `has_country_flag = crystal_armor_1_weight`: suppressing a modifier's only guard cannot turn it into an unconditional bonus. [Game tooltips](../../../Docs/semantics/TOOLTIPS_EN.md) · [Flag exception](TZ_TOOLTIP_FLAGS_EN.md)

## Language and incomplete information

- A complete phrase names the action and its object. A homogeneous group of researched technologies can share a heading containing the verb. In a mixed group an individual technology receives the full “Has researched the technology…” phrase. A heading introducing a list ends with one colon. Keep the agreed “(×N) condition” modifier format. Format numbers and formulas for the selected language.
- Resolve typed object IDs in batches through the existing lookup for the requested language. For example, `primitive` in `is_country_type` needs the country-type label “pre-FTL civilization”. For named objects, variables and flags use evidence for the value in the relevant scope. For flags check the owner, setter and clearing sites. Resolve static variables from versioned game data. A campaign-specific ruler or planet name can be represented by an established role. Apply the project's RU/EN source priorities. Render complete grammatical forms, inflected names and recognized icons in player-facing text. [Flag dictionary](TZ_TOOLTIP_FLAGS_EN.md) · [Icon and form inventory](../../../Docs/frontend/TECHNOLOGY_PAGE_READABILITY_EN.md#icons-and-localization)
- Distinguish an **unknown construct**, **unknown subject role**, **missing object name** and **missing phrase translation**. For a known module ID with no title, show “A station module is required (name unavailable)” and keep its ID accessible in details. If a condition is only partly understood, mark the incomplete part in place and preserve sibling branches and their logical relationship. If a negative phrase is missing, a readable explicit negation around the positive form is sufficient.
- A diagnostic contains the reason, original key, operator and operand or subtree, object, section, available source address and language for localization issues. Repeated issues may share a record listing their locations. The full original expression must remain available for verification. An “Additional condition (key)” label, an empty string or silently dropping the node fails this contract.

## Conditions in acquisition paths

The existing source index finds paths. At extraction time retain the subject and address at the point where each guard is checked. One path can switch owners several times before granting a reward. If this requires a change to derived index records, use the existing reset operation to rebuild them. [Source index](../sttv_server/progress_sources.py)

Present the sequence as “circumstance → event or choice → recipient and reward”. Event titles, lifecycle stages, hooks and guards each receive labels appropriate to their role. Resolve an event title including inheritance via `base`, local overrides and cycle detection. Describe an untitled hidden event by its confirmed trigger, e.g. `shroud.1010` becomes “Upon completion of the Experimental Testing situation”. Apply a consistent style to event references regardless of color markup in the title. [Three acquisition sections](../../../Docs/frontend/TZ_TECHNOLOGY_PAGE_AND_ACQUISITION_EN.md)

A shared part of a path can be shown once if the object, subject, recipient, conditions and result match over that part. Alternatives retain their choices, restrictions and rewards. Events sharing a name and different reward amounts retain their identities. A source requiring disabled DLC stays visible with the corresponding annotation in reference mode.

## Reference cases

| Input or case | Expected reading |
| --- | --- |
| `NOT = { has_active_event = { crisis.4135 } }` on crisis level five | “The event ‘The End is Nigh’ must be inactive.” Verify the multi-event form separately against this command's list semantics. |
| `OR` between a non-nomadic empire and an owned waystation with the anchor | “A nomadic empire must own at least one waystation fitted with an Aetherophasic Anchor.” A non-nomadic empire satisfies the first alternative. |
| `capital_scope → observation_outpost → has_mission = specimen_collection` | “The observed civilization's capital has an observation post on Aggressive Observation.” The full guard also checks that the post has an owner. The observer makes the choice. |
| `has_deposit = no` and synthetic `has_deposit = <deposit_id>` | “There are no deposits” and “Has the ‘{name}’ deposit”. |
| `resource_stockpile_compare = { resource = astral_threads value >= 1000 }` | “Has at least 1,000 Astral Threads in stock.” Replacing the operator with `>` makes the threshold strictly greater. |
| Building `dark_matter_detector` | “A Detection Array is installed or precedes the detector in the build queue.” Reuse the anchor's `has_starbase_module` rule. Preserve the separate prohibition in the adjacent `NOT`. |
| `OR` between a known technology and an unknown predicate with an argument | Show both the technology alternative and the incomplete check. Keep the exact argument in diagnostics. |
| Blue Lasers via Medical Side Effects | Where the reward applies, a closed research option opens with +80% progress. An already open option receives +100%. The observation table's 50 is a relative weight. The three numbers have different roles. |

Game examples are drawn from the [fifth crisis level](<E:/SteamLibrary/steamapps/common/Stellaris/common/crisis_levels/00_crisis_levels.txt:154>), [observation trigger](<E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/02_scripted_triggers_first_contact_dlc.txt:50>), [starbase building](<E:/SteamLibrary/steamapps/common/Stellaris/common/starbase_buildings/00_starbase_buildings.txt:2364>) and [reward branches](<E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/00_scripted_effects.txt:4903>).

## Delivery and acceptance

1. **Shared renderer.** Connect all four technology sections and the guards of all three reward methods. Check recursion, overloaded keys, nested subjects, negations, thresholds and preservation of unknown branches. The same fragment with the same subject and role must read consistently across callers. Accept the building example through the same entry point without requiring a building page.
2. **Dictionary and sources.** Investigate the forms listed below on the snapshot. For each, record the supported shape, game evidence for its role and any outstanding uncertainty. For the 148 events and 57 `on_…` keys, start with the source type and existing game labels. Review the 281 check/flag pairs lacking a specific phrase. Add RU/EN phrases where evidence supports them and record the specific reason and use sites for the remainder. A generic placeholder does not count as support.
3. **Rendering and checks.** Display the shared nodes in the existing component. Verify the six audited icons, clean game markup, readable nesting, localized numbers and page/tooltip parity. Include a deliberately incomplete flag or dynamic target.
4. **Snapshot acceptance.** Compare all 679 technologies before and after in both languages with all DLC enabled. Recount affected pages and distinct operands per form, separating meaningful renderings, partial renderings with reasons and discrepancies. Require zero lost operands or child branches, zero objects named `no` from boolean checks and zero simultaneous mutually exclusive statuses in reference mode. When main text omits the game ID, match by ID and source address in the data. Verify the wording and polarity of confirmed cases. A generic placeholder fails the understood reference cases. The deliberately unknown command tests preservation of a partial result.
5. **Regression checks.** Compare source IDs, reward addresses, choices, recipients, outcomes, amounts and membership of the three sections. Verify structural simplifications on truth assignments for small expressions, including NAND/NOR and an unresolved branch. Check a source with its required DLC enabled and disabled. On this snapshot, the section counts are 289, 248 and 298 technologies respectively. Keep indexed acquisition lookup and batched localization reads. A page request must not scan all events or query MongoDB once per leaf. Store the resulting comparison in `TMP/WEB_STTV/<run>/reports/`.

6. **Full browser sweep.** After implementation, take all base technology IDs from the snapshot under test. With all DLC enabled, open the direct page `#/technology/<id>?lang=ru` for each ID, then its English version with `lang=en`. Wait for rendering. For each ID and language pair, compare the heading, sections and visible condition text with the verified API data. Check list nesting, absence of unprocessed game tokens and successful loading of the inline icons called for by the text. Record the result for every pair and the reason for each failure. Snapshot v4.5.4 has 679 × 2 = **1,358** distinct pages. Acceptance requires a successful check for every expected pair with no omissions. Recalculate coverage from the snapshot IDs when the snapshot changes.

7. **Collection reset.** Prepare documents for two different technologies and open them with different languages and DLC selections. Run the reset from system settings. Verify the empty collection and client cache before any new request. Repeating the reset on an empty collection must succeed. Request one technology and check that only its document is created. Cover an in-flight request, the global reset and the source-index reset.

8. Test the stand from a clean parser export through a full database drop, loader import and verification of every input collection. Check localization and sprites using the configured profiles. Record source IDs before the drop.

## First-stage inventory

The list includes all 132 distinct keys and paths behind the 134 spellings of the audited placeholder. The groupings establish a research queue. Confirm each actual form against its key, operand and context. The target names and compound paths in the first row share a scope traversal rule. The inventory also contains operands and affected technologies. [Snapshot working report](../../../../TMP/WEB_STTV/technology-page-readability/reports/inventory.json)

| Research group | Keys or paths |
| --- | --- |
| Subject, scope transition or selection (58) | `any_deposit`, `any_fleet_in_system`, `any_moon`, `any_neighbor_system`, `any_owned_fleet`, `any_owned_megastructure`, `any_playable_country`, `any_situation`, `any_system`, `capital_scope`, `capital_scope.observation_outpost_owner`, `contact_country`, `controller`, `event_target:atomic_clock_planet.solar_system`, `event_target:coils_planet`, `event_target:contact_empire`, `event_target:contact_speaker`, `event_target:curator_enclave_country`, `event_target:fortress_country`, `event_target:fotd_seperatist_planet@root`, `event_target:guardian_dragon_planet`, `event_target:guardian_technosphere_country`, `event_target:hibernator_planet`, `event_target:last_talon_ship`, `event_target:living_planet_tar`, `event_target:mindwarden_enclave_country`, `event_target:pre_ftl_country`, `event_target:pre_ftl_planet`, `event_target:pre_ftl_species`, `event_target:primitive_civ`, `event_target:shroudwalker_enclave_country`, `explorer`, `from`, `from.controller`, `from.leader`, `from.owner`, `from.solar_system`, `from.target`, `fromfrom`, `fromfrom.owner`, `fromfrom.solar_system`, `fromfromfrom`, `fromfromfrom.fleet`, `leader`, `observation_outpost_owner`, `original_owner`, `owner?`, `owner_main_species`, `planet?`, `root`, `root.contact_country`, `root.from`, `root.fromfromfrom`, `root.owner`, `solar_system?`, `space_owner`, `target.owner`, `this.owner` |
| Boolean check (18) | `has_any_strategic_resource`, `has_ground_combat`, `has_moon`, `has_observation_outpost`, `has_owner`, `is_artificial`, `is_asteroid`, `is_at_war`, `is_capital`, `is_colonizable`, `is_colony`, `is_homeworld`, `is_moon`, `is_primitive`, `is_ringworld`, `is_space_fauna`, `is_star`, `is_under_colonization` |
| Named argument or domain check (32) | `agreement_preset`, `carrier_is_type`, `current_stage`, `has_access_fleet`, `has_active_tradition`, `has_building`, `has_climate`, `has_completed_event_chain_counter`, `has_covenant`, `has_event_chain`, `has_overlord`, `has_patron_relation`, `has_planet_class`, `has_pre_ftl_age`, `has_special_project`, `has_starbase_module`, `ideal_planet_class`, `is_at_war_with`, `is_hostile`, `is_hostile_to`, `is_in_domain`, `is_in_federation_with`, `is_megastructure_type`, `is_ship_class`, `is_ship_size`, `is_species_class`, `is_star_class`, `is_tutorial_level`, `is_unfriendly_to`, `last_building_changed`, `leader_class`, `uplift_is_archetype` |
| Quantity and comparison (11) | `attunement`, `check_variable`, `distance`, `end_game_years_passed`, `num_ascension_perks`, `num_minerals`, `num_planets_in_system`, `num_researched_techs_of_tier`, `resource_stockpile_compare`, `situation_progress`, `trust` |
| Event reference or list (1) | `has_active_event` |
| Conditional branch (1) | `else_if` |
| Flag and owning scope (11) | `has_astral_rift_flag`, `has_carrier_flag`, `has_first_contact_flag`, `has_leader_flag`, `has_planet_flag`, `has_relation_flag`, `has_ship_flag`, `has_situation_flag`, `has_species_flag`, `has_star_flag`, `is_occupied_flag` |

[Русская версия](TZ_CONDITION_TEXT_RU.md)
