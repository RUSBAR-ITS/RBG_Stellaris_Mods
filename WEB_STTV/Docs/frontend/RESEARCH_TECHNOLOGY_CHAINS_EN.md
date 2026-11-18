# Stellaris Technological Tree View — technology chain research

## Contents

- [Research scope](#research-scope)
- [Current sorting behavior](#current-sorting-behavior)
- [Link structure](#link-structure)
- [Chain examples](#chain-examples)
- [Family continuation and additional requirements](#family-continuation-and-additional-requirements)
- [Tier and identifier limitations](#tier-and-identifier-limitations)
- [Automatically selected candidates](#automatically-selected-candidates)
- [Conclusion for further discussion](#conclusion-for-further-discussion)
- [Artifacts and verification](#artifacts-and-verification)

## Research scope

Research dated 2026-11-17, requested after testing the first frontend. Input: existing `data/stage10/database.json`. The analysis covers base technologies and their `prerequisites`; availability conditions and game state are not evaluated. `technology_swap` variants remain representations of base technologies, not separate chain vertices.

These are findings and proposals for discussion. Product code and sorting were not changed in this iteration; this document does not approve new grouping rules.

## Current sorting behavior

`sttvLayout` in `src/frontend/data/layout.ts` constructs each column in each area independently. `sttvOrderColumn` respects dependencies within a column, then compares requirement counts, predecessor sets, and IDs. There is no shared chain-row assignment across adjacent columns.

Consequently, consecutive technologies of a family can appear at different vertical positions: ordering within each column is valid, but family progression is not aligned across columns. This explains the problem observed by the user.

## Link structure

A link below means an ID reference in `prerequisites`, including alternatives. It does not necessarily represent a separately mandatory condition.

| Metric | Count |
| --- | ---: |
| Base technologies | 679 |
| Variant representations | 206 |
| Unique predecessor-to-technology pairs | 615 |
| Technologies without technology predecessors | 178 |
| Technologies with one immediate predecessor | 412 |
| Technologies with multiple immediate predecessors | 89 |
| Technologies containing `OR` requirements | 19 |
| `OR` groups in original requirements | 21 |
| Technologies referenced by multiple other technologies | 115 |
| Isolated technologies without incoming or outgoing links | 115 |
| Connected components ignoring direction | 156 |
| Largest component | 393 technologies |
| Links between base representations in different areas | 91 |
| Links within the same `tier` | 193 |
| Links from a greater `tier` to a smaller one | 13 |

The graph has no directed cycles, and every referenced technology ID resolves. Of the 89 technologies with multiple predecessors, 19 contain `OR` alternatives; the remaining 70 have only simultaneous requirements. Of 156 components, 115 are single vertices, leaving 41 connected multi-technology sections.

Connected-component membership is too broad for a family: grouping the largest component would produce a single 393-technology group.

## Chain examples

| Family | Sequence supported by actual dependencies | `tier` |
| --- | --- | --- |
| Lasers | Red → Blue → UV → X-Ray → Gamma Lasers; `tech_lasers_1…5` | `0 → 1 → 2 → 3 → 4` |
| Shields | Deflectors → Improved Deflectors → Shields → Advanced Shields → Hyper Shields; `tech_shields_1…5` | `0 → 1 → 2 → 3 → 4` |
| Reactors | Fission → Fusion → Cold Fusion → Antimatter → Zero Point → Dark Matter Power | `0 → 1 → 2 → 3 → 4 → 5` |
| Missiles | `tech_missiles_1 → tech_missiles_2 → tech_missiles_3 → tech_missiles_4 → tech_missiles_5` | `0 → 1 → 2 → 3 → 4` |
| Mining stations | `tech_space_mining_1 → … → tech_space_mining_5` | `1 → 1 → 2 → 2 → 3` |
| Starbases | `tech_starbase_1 → … → tech_starbase_5` | `0 → 0 → 2 → 3 → 4` |

The reactor sequence is supported by `prerequisites` despite lacking consecutive numbers in IDs: `tech_fission_power → tech_fusion_power → tech_cold_fusion_power → tech_antimatter_power → tech_zero_point_power → tech_dark_matter_power_core`.

Reference locations retained in the database: lasers in `common/technology/00_phys_weapon_tech.txt`, lines 8, 30, 85, 140, 195; reactors in `00_phys_tech.txt`, lines 1487, 1521, 1575, 1627, 1679, followed by `00_fallen_empire_tech.txt:43`; mining stations in `00_eng_tech.txt:2384` onwards. These are database provenance coordinates, not a new inspection of the installed game.

## Family continuation and additional requirements

`tech_lasers_2` has four immediate dependents: `tech_lasers_3`, `tech_plasma_1`, `tech_disruptors_1`, and `tech_repeatable_weapon_type_energy_fire_rate`. `tech_lasers_3` is the obvious laser-family continuation candidate, but the graph does not mark it as the main continuation and the others as side branches.

`tech_missiles_2` has two simultaneous requirements:

```text
tech_missiles_1 + tech_fusion_power → tech_missiles_2
```

For the missile family, `tech_missiles_1` appears to be the continuation predecessor, while `tech_fusion_power` is an additional requirement from the reactor family. This is a display interpretation; both game dependencies remain intact.

Similarly, `tech_basic_science_lab_3` requires `tech_basic_science_lab_2` and `tech_colonial_centralization`. Mega-Engineering combines Zero Point Power and two alternative groups, then opens ten other technologies. Such vertices cannot be automatically assigned to a single progression solely by counting links.

No explicit family or primary-predecessor field was found among the top-level fields of the 679 technologies. `area`, `category`, IDs, and names provide additional clues, but `prerequisites` does not distinguish series progression from external conditions.

## Tier and identifier limitations

ID numbering differs from `tier`. Five mining-station technologies occupy three tiers; the first two starbase technologies both have `tier=0`. Even within numeric families, 41 links connect technologies in the same tier. A chain therefore cannot always occupy one horizontal row with one card per column.

Among 13 links toward smaller tiers, one example is `tech_antimatter_power` (`3`) → `tech_reactor_boosters_3` (`1`). This is not a directed cycle. A lower-tier transition alone does not prove a data error; `tier` is not graph depth.

Matching IDs after removing the last number also do not establish a linear sequence:

- `tech_akx_worm_1` and `tech_akx_worm_2` jointly require research before `tech_akx_worm_3`. All have `tier=3`; the second belongs to society, the others to physics. This merges two branches instead of forming `1 → 2 → 3`.
- `tech_crystal_armor_1` and `tech_crystal_armor_2` have no `prerequisites` link in this database.
- `tech_cosmogenesis_crisis_1…5` likewise do not form a sequence through `prerequisites`.

Area statistics use base representations. Manual variant changes may change the displayed area while preserving base IDs and dependencies.

## Automatically selected candidates

Two simple selection methods were examined without changing the product:

1. **Structural linear fragments.** Retain an edge when its source has exactly one dependent and its target exactly one predecessor. This yields 94 maximal fragments covering 242 technologies. Side branches break ordinary families under this rule; for example, it does not preserve the entire laser sequence.
2. **Numeric families plus actual links.** Group IDs by their prefix before the final `_number`, then inspect existing links within each group. There are 98 multi-technology groups and 182 internal links. Two groups have no links and one merges two inputs; the remaining 95 form linear candidates covering 275 technologies. External requirements are retained.

The union of both selections covers 335 unique technologies. This is candidate coverage, not a finished partition: selections overlap and thematic validity/family boundaries still need decisions. Exclusion from these selections does not mean a technology lacks a chain; reactors illustrate progression without a numeric pattern.

## Conclusion for further discussion

Display grouping would benefit from separate chain membership and continuation definitions while retaining the complete requirement tree. This would align laser progression by tier, keep plasma as a neighboring branch, and avoid merging reactors into missiles because of an additional prerequisite.

Verified numeric families provide a starting point, followed by unnumbered sequences and ambiguous merges. Multiple same-tier members need vertical placement within the chain's corresponding column. Rules for selecting the main continuation, membership in multiple families, and geometry still require discussion and approval.

## Artifacts and verification

- `data/chain_analysis/inspect.ts`: reproducible research pass using the existing adapter and reading additional fields from the original tree.
- `data/chain_analysis/analysis.json`: technologies, provenance, dependencies, components, fragments, numeric groups, and special cases.
- `data/chain_analysis/verification.json`: independent traversal of original JSON `prerequisites`; all 679 IDs and 615 link pairs match, with 21 `OR` groups.
- Input SHA-256: `a3ef07a166dee5b7be4a17608e20c6545a99321247802268939985b92689c858`. A repeat check confirmed that the database file was unchanged.

Run from `WEB_STTV` with Node.js and dependencies available: `node --import tsx data/chain_analysis/inspect.ts`. Artifacts under `data/` are Git-ignored; findings are retained in this bilingual document.

[Русская версия](RESEARCH_TECHNOLOGY_CHAINS_RU.md).
