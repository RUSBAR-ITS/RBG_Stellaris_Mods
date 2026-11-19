# Technology chains — matching availability conditions

## Contents

- [Status and purpose](#status-and-purpose)
- [Compared data](#compared-data)
- [Selection rule](#selection-rule)
- [Rule boundaries](#rule-boundaries)
- [Example](#example)
- [Related documents](#related-documents)

## Status and purpose

Approved on 2026-11-18 as a `parent_tech` selection criterion after direct object upgrades and before functional affinity. This document records a decision for a future specification; the layout algorithm is unchanged in this iteration.

Matching conditions helps choose a continuation among the remaining technology prerequisites. It creates no new game dependencies and does not determine actual availability to a particular empire.

## Compared data

Inputs are the current technology `T`, remaining candidate set `C` and technology `potential` blocks after expansion.

Comparison includes complete block content and structure: commands, values, operators, nesting and scope transitions. File paths, line numbers and other provenance metadata do not participate. Source text formatting is not part of the condition tree content.

Matching is limited to nonempty `potential` blocks. A missing or empty block does not witness matching special conditions. Conditions in `weight_modifier` and `ai_weight` are excluded: they concern selection weights.

## Selection rule

1. If `C` already contains one candidate, selection is complete and this rule is not applied.
2. If `T` has no nonempty `potential`, skip the criterion.
3. Retain only current candidates whose nonempty `potential` completely matches technology `T`'s `potential` under the structural comparison described above.
4. Select a sole matching candidate and finish selection. Pass multiple matching candidates to the next criterion.
5. If there are no matches, skip the criterion and retain the previous set `C`.

Previously discarded candidates are not reintroduced. Original technology requirements and conditions remain in the database.

## Rule boundaries

- Partial matches, a shared individual keyword or an identical check inside different logical expressions are not used as proof.
- Structural matching does not require evaluating conditions for an empire. Proving logical equivalence of differently written expressions is outside this rule.
- `technology_swap.trigger` selects a technology representation and does not replace its `potential`. This criterion does not introduce automatic merging of those two blocks.
- Object construction conditions and conditions on their bonuses have a different context and are not substituted for a technology's own `potential` when comparing it.
- The rule assigns no ethics, origin or other user empire parameters. The standard empire filter remains a separate criterion.

## Example

In local Stellaris 4.5.4 files, [tech_transcendent_faith](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:5830) requires `tech_consecration_fields` and `tech_galactic_administration`.

It and [tech_consecration_fields](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:5803) have identical source blocks:

```text
potential = {
    OR = {
        is_spiritualist = yes
        AND = {
            is_gestalt = no
            has_make_spiritualist_perk = yes
        }
    }
}
```

This compact example precedes named trigger expansion; comparison uses the expanded blocks. [tech_galactic_administration](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:4721) has no own `potential`. If both prerequisites remain candidates, the rule selects `tech_consecration_fields`.

The example demonstrates applicability to this pair; no new full database run was performed while documenting the rule.

## Related documents

- [General chain and sorting rules](TECHNOLOGY_CHAINS_AND_SORTING_EN.md).
- [Direct object upgrades](CHAIN_DIRECT_UPGRADES_EN.md).
- [Empire condition dictionary](../semantics/EMPIRE_CONDITIONS_EN.md).
- [Technology and variant fields](../semantics/TECHNOLOGIES_EN.md).
- [Русская версия](CHAIN_AVAILABILITY_RU.md).
