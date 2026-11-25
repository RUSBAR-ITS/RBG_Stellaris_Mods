# Wiki acceptance on Stellaris 4.6.0

## Contents

- [Clean rebuild](#clean-rebuild)
- [Parser exception checks](#parser-exception-checks)
- [Trees and pages](#trees-and-pages)
- [Data and wording gaps](#data-and-wording-gaps)

## Clean rebuild

On 25 November 2026 the test wiki was updated from 4.5.4 to Corona Borealis 4.6.0 (3d1a). Before dropping `wiki`, the loader checked the export inventory, identifiers and BSON sizes. The clean import published 359,322 documents to 110 source collections. An independent read from MongoDB matched the export, including reconstruction of source locations. Loading took 645.62 s, verification took 565.01 s, and image verification and transfer took 30.66 s. Four technology icons and the Willpower thumbnail were uploaded.

| Objects | 4.5.4 | 4.6.0 |
|---|---:|---:|
| Technologies | 679 | 683 |
| DLC catalog entries | 36 | 37 |
| Events | 10,111 | 10,504 |
| RU and EN localization records | 306,310 | 316,303 |

The parser prepared five libraries from 818 files and processed all 845 files in the profile. Three approved exceptions cover the new DLC. Restore the missing assignment operator on `increase_pop_political_power`, apply the default `no` to seven unguarded substitutions in `move_galactic_halls` when its caller omits the argument, and forward the trait class to the nested `council_no` icon template. All 18 parser tests passed. [Exception rules](../../Instruments/Stellaris_Parser/stellaris_parser/config/source_exceptions.json)

## Parser exception checks

Each of the eight rules in `source_exceptions.json` was disabled separately in memory for every 4.6.0 input file it covers. The extensionless inline path was tested separately. The table gives handler invocations per parse and the outcome with the rule disabled.

| Source | Result on 4.6.0 |
|---|---|
| Jobs, `06_event_jobs.txt` | One reference has an extra trailing separator. Parsing fails at line 2176. |
| Relics, `RELIC` from `SELECTED_RELIC` | 15 substitutions each in `grand_archive_events.txt` and `leviathans_events_1.txt`. Both files fail on the missing argument without the rule. |
| Nomads, `RANDOM = 0` | Nine substitutions. Disabling the rule leaves the effect without its `RANDOM` argument. |
| `dlc002` metadata | One inserted `=`. Without it parsing succeeds, but `paradoxplaza_store_url` and the empty string become two separate values. |
| Traits, `trait/icon` | 55 substitutions across 5 of 13 configured files. Disabling the rule yields identical documents for the other eight. |
| Traits, `trait/icon_element/council_no` | 63 substitutions across all 11 configured files. Two are in the Willpower file. |
| `tr_purity_imperfection_remediation_wilderness` tradition | The file still ships without `.txt`. Without the explicit path, `01_purity.txt` fails to resolve the template. |
| New Willpower rules | Without the `increase_pop_political_power` correction, library preparation fails at line 1879. The handler supplies one missing argument in `move_galactic_halls`. Disabling it stops the parse at line 2667. |

Eight files under `common/traits/` can be removed from the **outer** `trait/icon` rule. They are `00_admiral_traits.txt`, `00_general_traits.txt`, `00_generic_leader_traits.txt`, `00_governor_traits.txt`, `00_scientist_traits.txt`, `08_ancrel_traits.txt`, `15_biogenesis_leader_traits.txt` and `16_infernals_traits.txt`. Expansion history from 4.5.4 and 4.6.0 shows the same number of calls without an explicit class in each of the 13 files, with zero in those eight in both versions. The nested `council_no` rule still needs its entire list. [Parse results](../../TMP/WEB_STTV/willpower-sources-4.6.0/reports/exceptions-and-sources.json) · [Call comparison](../../TMP/WEB_STTV/willpower-sources-4.6.0/reports/trait-calls-by-version.json)

## Trees and pages

Ten combinations of DLC, mixed trees and the event technology filter passed. Checks covered reciprocal parent and child links, cycles, unique RU and EN coordinates and reopening persisted trees. There are 682 visible cards with all DLC, 678 with only Willpower disabled, 468 with only Willpower enabled and 464 with all DLC disabled. With all DLC enabled, `has_ancrel = no` excludes `tech_archeology_lab`.

Chrome exercised 1,366 pages. Titles, sections, conditions and icons matched the API responses. The Blue Lasers card and standalone page also matched after opening a reward with the keyboard. Comparison against the previous release flagged reward addresses on 1,038 language pages. Comparing game sources and award content preserved all previously displayed source groups and award outcomes for the 679 existing technologies. Another source was found for 262 technologies. [Tree matrix](../../TMP/WEB_STTV/rebuild-4.6.0-20261125/reports/tree-matrix.json) · [Page comparison](../../TMP/WEB_STTV/rebuild-4.6.0-20261125/reports/compatibility.json)

## Data and wording gaps

| Area | Finding |
|---|---|
| Willpower crisis perks | The import profile omits `common/menace_perks`. A level-two crisis perk grants `tech_cultural_envoys` fully researched. A level-five perk contains six 50% progress commands for jump drives and cloaking technologies. The cloaking outcomes depend on First Contact and the branches of an `inverted_switch`. |
| Yuht ideology tenet | The profile omits `common/ideologies/tenets`. Unlocking `tenet_lost_makers_yuht` grants a research option for `tech_ecological_adaptation` if the technology has not been researched. |
| Cultural Envoys title | The wiki displays a campaign-value placeholder. In `common/scripted_loc/16_scripted_loc_forceofwill.txt`, `GetCulturalEnvoyNamePlural` has three conditional names and an explicit `default = cultural_envoy_default_plural`. The reference view can use “Cultural Envoys” / «Культурные послы». |
| Ideology sources and conditions | The action `on_ideology_momentum_positive` lacks a caption on 261 technologies. The newly encountered check `num_active_tenets` affects 261. Four technologies also need the `ideology?` scope, and one needs a `free_building_slots` comparison. The sets overlap. |
| Galactic Halls | The country type `rebel` has no displayed name. The weight block contains `mult = 2`, which the renderer currently shows as a partial condition. Its game semantics in this particular block still need confirmation. |
| Individual awards and flags | Psionic Theory uses generic captions for `lost_makers_precursor_zroni` and `lost_makers_precursor_adakkaria`. Wormhole Stabilization uses a generic saved target for `event_target:selected_precursor_system`. Ideological Projection describes `unlock_tech_ideology_projection` through the actions that set the flag. |

The audit found 265 technologies per language with at least one of the tested wording issues. A separate check found dynamic labels on 262 technologies. The main case is event `forceofwill.1560`, whose title interpolates a specific empire’s tenet. No raw game markup was detected on the 1,366 pages. Acquisition findings are based on game scripts and published pages. [Rewards outside the import](../../TMP/WEB_STTV/rebuild-4.6.0-20261125/reports/outside-import.json) · [Wording audit](../../TMP/WEB_STTV/rebuild-4.6.0-20261125/reports/wording.json)
