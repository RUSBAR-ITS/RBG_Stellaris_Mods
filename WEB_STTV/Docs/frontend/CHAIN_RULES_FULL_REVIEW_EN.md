# Technology chains — complete analytical pass

## Contents

- [Review scope](#review-scope)
- [Criterion order](#criterion-order)
- [Totals](#totals)
- [Changes from the previous complete pass](#changes-from-the-previous-complete-pass)
- [Where selection finishes](#where-selection-finishes)
- [Evidence and checks](#evidence-and-checks)
- [Remaining placement work](#remaining-placement-work)
- [Result boundaries](#result-boundaries)
- [Artifacts](#artifacts)

## Review scope

The pass was performed on 2026-11-19 against published database set `8d7f30af6cc5a9504e6fbb0e2126edae8d18fe9a159f9969e574926ca62b5f01`. It covers all 679 base technology representations and the approved predecessor-selection additions. This is a research calculation for design, without integrating the algorithm into the product.

It uses the agreed reference profile: a non-nomadic, non-gestalt empire with biological founders and conventional ships. Ethics beyond the gestalt distinction, origin, DLC and development paths are unspecified. Unknown conditions remain unknown; the filter removes only candidates with a confirmed contradiction to known facts. If it would remove all candidates, the previous set is retained.

Game requirements remain unchanged. `parent_tech` is a selected analytical anchor, not a replacement for the complete prerequisite graph.

## Criterion order

1. ID equality after removing digits.
2. Same research area.
3. Same research category.
4. Mandatory technology prerequisite.
5. Direct upgrade of unlocked objects.
6. Complete structural match of nonempty `potential` conditions.
7. Functional groups: mobile combat ship, planet class change, anti-ship weaponry.
8. Direct functional object relations.
9. Indirect functional affinity through one original prerequisite edge of the candidate.
10. Affinity through the technology's own production bonuses.
11. Affinity through its own increases in object capacity.
12. Agreed standard empire filter.
13. Highest game `tier` among the remaining candidates.

Selection stops at a sole candidate; an empty criterion result is skipped. Discarded candidates are never restored. Evidence counts are not votes. Alphabetical order, manual technology pairs and future coordinates do not participate in predecessor selection.

## Totals

| Measure | Result |
| --- | ---: |
| Total base technologies | 679 |
| No technology prerequisites; no parent needed | 178 |
| One direct prerequisite | 412 |
| Multiple direct prerequisites | 89 |
| Of these 89, a unique parent is selected | 89 |
| Total technologies with a selected parent | 501 |
| Remaining ambiguities | **0** |
| Mismatches against 12 agreed acceptance examples | **0** |
| Cycles in the selected-parent graph | **0** |

Every technology requiring a parent therefore has a unique selection in the checked mode. The 178 root technologies are not ambiguities. This is the result of the agreed analytical criteria on current data, not a claim that the game itself defines a unique parent.

## Changes from the previous complete pass

Comparison against `current_review/report.json`, produced before the latest additions:

| Technology | Before | After | Reason |
| --- | --- | --- | --- |
| Juggernaut (`tech_juggernaut`) | Citadel | Battleships | The mobile combat ship group now runs before the direct relation to starbase construction. |
| Ceramo-Metal Alloys (`tech_advanced_metallurgy_1`) | Unresolved | Holographic Casts | Production bonus → metallurgist category → job → unlocked building. |
| Mega-Engineering (`tech_mega_engineering`) | Unresolved | Citadel | Starbase capacity narrows the set to Citadel and arkship; empire filtering retains Citadel. |
| Stellar Cannon (`tech_dyson_gun`) | Wormhole Stabilization | UV Lasers | Shared weaponry group confirmed through components and the firing action route. |
| Volcanic Terraforming (`tech_volcanic_terraforming`) | Unresolved | Terrestrial Sculpting | Shared planet class change group. |

The other **674** technologies have the same parent and status as in the previous complete pass. That pass left three ambiguities and two known expected-chain mismatches; all five cases are now resolved by general rules.

Armor Hardening still follows Ceramo-Metal Alloys. Its indirect evidence uses the alloys' original requirement for an armor technology even though the alloys themselves are placed after Holographic Casts. This confirms the need to traverse the original graph rather than only selected parents.

## Where selection finishes

This table covers the 89 technologies with multiple direct requirements. The 412 technologies with a single requirement need no filtering.

| Final applied criterion | Parents selected |
| --- | ---: |
| Digit-stripped ID | 29 |
| Research area | 29 |
| Research category | 9 |
| Mandatory status | 3 |
| Direct object upgrades | 3 |
| Matching `potential` | 2 |
| Functional groups | 3 |
| Direct functional relations | 0 |
| Indirect affinity | 1 |
| Production bonuses | 1 |
| Object capacity | 0 |
| Empire filter | 3 |
| Game tier | 6 |

A zero in this table does not make a rule useless: for example, object capacity narrows Mega-Engineering's three candidates to two before the empire profile finishes selection. Fourteen technologies reach the functional stage with multiple candidates.

## Evidence and checks

- Checked common set identity, sizes and SHA-256 for 14 used databases; projections were verified against published files. For events, the actual input database hash was recorded and the required linked event extracted separately.
- Recomputed direct upgrades, functional groups, direct relations, indirect affinity, production and capacity evidence from data. Manual choices were not injected into selection.
- Production affinity verifies category modifier-generation rules, the job's production category and positive additions of that job in a building. Job provision conditions are retained.
- Capacity uses the approved mapping `country_starbase_capacity_add` → `starbase_capacity_used` → `ship_size` → hull requirements. Other capacity mappings were not guessed.
- Every selected parent exists and is an original direct prerequisite of its child. Checked stopping at one candidate, skipping empty results and monotonic reduction of candidates.
- Reversing technology and candidate traversal order produced identical parents and statuses. Source technology fields remained unchanged. The selected-parent graph has no cycles.
- All 12 acceptance examples match. They are stored separately and read by verification after calculation; the selection function does not use this list.
- An ambiguity log was generated with snapshots of mode, profile, variant selection and rules; its entry list is empty in this pass.

## Remaining placement work

A selected parent does not yet determine card coordinates. The resulting graph includes:

| Selected-parent edge property | Count |
| --- | ---: |
| Same game tier | 147 |
| Parent has a higher game tier than its child | 10 |
| Different research areas | 37 |

These groups may overlap. Requirements come from the database; tiers were not rewritten to fit an edge direction. Subsequent tree placement must account for these edges while retaining each card's own tier and area.

Separately confirmed moving **19** infinitely repeatable technologies from game tier 5 to display column 6: each has at least one technology prerequisite. The game tier is preserved. This pass did not calculate `location`, branch heights, reserved spaces, alphabetical placement or special positioning between branches.

## Result boundaries

- The absence of ambiguities applies to base representations and the specified profile. Manual `technology_swap` selection, inherited effects and other modes require separate verification.
- “Complete pass” means applying the entire agreed sequence to every base technology. It is not a universal interpretation of arbitrary game commands: it uses confirmed evidence forms documented in related specifications.
- Indirect affinity compares component `ship_modifier` fields with matching context and sign at depth 1. Production uses an exact category match and job provision through supported building fields. Other forms are not guessed.
- Event execution conditions, actual empire state and dynamic effect amounts are not evaluated. Conditional evidence remains conditional.
- Published databases and the product frontend/backend remain unchanged. Only research materials and documentation changed; visual sorting is still the previous implementation.

## Artifacts

- [Complete report with 679 decisions and traces](../../data/chain_analysis/final_review/report.json).
- [Evidence and criterion matches](../../data/chain_analysis/final_review/evidence.json).
- [Ambiguity log](../../data/chain_analysis/final_review/ambiguities.json).
- [Research pass settings](../../data/chain_analysis/final_review/rules.json).
- [Acceptance examples used only by verification](../../data/chain_analysis/final_review/expectations.json).
- [Calculation entry point](../../data/chain_analysis/final_review/run.py).
- [General chain rules](TECHNOLOGY_CHAINS_AND_SORTING_EN.md).
- [Русская версия](CHAIN_RULES_FULL_REVIEW_RU.md).
