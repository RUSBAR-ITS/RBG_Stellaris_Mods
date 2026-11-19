# Technology chains — functional criterion order review

## Contents

- [Decision and scope](#decision-and-scope)
- [Comparison method](#comparison-method)
- [Results](#results)
- [Variant sensitivity](#variant-sensitivity)
- [References](#references)

## Decision and scope

On 2026-11-19 the user agreed to place functional groups before direct functional relations provided other chains suffered no unwanted changes. Checking the current database's base representations found only the intended Juggernaut change. The future specification records this order: direct upgrades → matching `potential` → **functional groups → direct functional relations** → indirect affinity → production bonuses → object capacities → empire filter → seniority.

This is an analytical check of `parent_tech` selection, not a frontend sorting implementation. Card geometry and visual rendering were not tested. Results apply to the current data and documented evidence forms, not a guarantee of unchanged behavior in future game versions.

## Comparison method

- Used set `8d7f30af6cc5a9504e6fbb0e2126edae8d18fe9a159f9969e574926ca62b5f01` and the previously agreed standard empire profile. Sizes and SHA-256 hashes of the eight source databases required for comparison were checked against the research projections.
- Applied the same first six criteria to every technology: digit-stripped ID, area, category, mandatory status, direct upgrades and matching `potential`.
- Compared two orders on the same incoming set: direct relations → groups and groups → direct relations. Both approved groups are included: mobile combat ship and planet class change.
- Re-extracted supported direct relations from objects; results for incoming candidates matched the previous study. Verified stopping at one candidate, skipping empty results and not restoring eliminated candidates.
- Compared complete remaining sets, not just selected parents. Equal sets after this pair imply equal results from the unchanged later criteria. Isolating this swap therefore does not require reimplementing production and object capacity affinity.

Research scripts are in the working folder `data/chain_analysis/order_review/`. Product code and published databases remain unchanged. This is not a full new pass of every extended rule; no new overall ambiguity resolution totals are claimed.

## Results

| Check | Result |
| --- | ---: |
| Base technologies | 679 |
| Technologies with multiple direct prerequisites | 89 |
| Reached the compared criterion pair | 14 |
| Remaining candidate set changed | 1 |
| Candidate set unchanged | 678 |

The only change:

| Technology | Direct relations before groups | Groups before direct relations |
| --- | --- | --- |
| Juggernaut (`tech_juggernaut`) | Citadel (`tech_starbase_5`) | Battleships (`tech_battleships`) |

Previously, the relation through `capital_yards` and its Citadel requirement ended selection before the ship group. In the new order, the mobile combat ship group retains only Battleships. Both relations are supported by data; their priority changes while game requirements are preserved.

The new anchor is a direct prerequisite. The original requirement graph has no path from Battleships back to Juggernaut, so the new relation cannot create a parent cycle. The previous selected-parent graph was also verified to remain acyclic after this replacement. Equal inputs to later criteria rule out parent selection changes caused by this swap for other technologies.

## Variant sensitivity

Additionally checked 128 combinations of seven variants changing research area or category. With unlocked-object evidence held fixed, the swap affected only Juggernaut in 64 combinations; the other combinations produced no changes.

This is a separate area/category sensitivity check. It does not replace complete analysis of selected representations, `inherit_effects`, access conditions or other empire profiles. Full variant and layout checks belong in implementation of the corresponding algorithm.

## References

- [Comparison report, selection traces and checks](../../data/chain_analysis/order_review/report.json).
- [Recomputed evidence](../../data/chain_analysis/order_review/evidence.json).
- [Overall rule order](TECHNOLOGY_CHAINS_AND_SORTING_EN.md#sequential-rule-application).
- [Functional groups](CHAIN_FUNCTIONAL_GROUPS_EN.md).
- [Direct functional relations](CHAIN_DIRECT_RELATIONS_EN.md).
- [Русская версия](CHAIN_CRITERIA_ORDER_REVIEW_RU.md).
