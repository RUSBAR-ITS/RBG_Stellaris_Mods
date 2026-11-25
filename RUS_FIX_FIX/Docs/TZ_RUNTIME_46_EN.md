# RUS_FIX_FIX — proposed fixes for the Stellaris 4.6.0 logs

## Contents

- [Scope and sequence](#scope-and-sequence)
- [Empires in the new game screen](#empires-in-the-new-game-screen)
- [Job names](#job-names)
- [Empire adjectives](#empire-adjectives)
- [Ship name inflection](#ship-name-inflection)
- [Ship modifier labels](#ship-modifier-labels)
- [Acceptance](#acceptance)

## Scope and sequence

**Status in 4.5.15.** The empire and job changes passed parser checks and await in-game verification. The user closed the ship name inflection review. The ship modifier review compared logs, scripts and translations. Empire adjectives have a separate test plan. [First-stage checks](../../TMP/RUS_FIX_FIX/empires_jobs_4.5.15.json).

The baseline is a Russian-language Stellaris 4.6.0 run with local build 4.5.14. Preserve the upstream author's terminology and inflection. The four Tass ship sizes and their 20 keys belong to a separate translation. [Overall specification](TZ_COMPAT_46_EN.md) · [Log and source inventory](../../TMP/RUS_FIX_FIX/runtime_design_46.json).

## Empires in the new game screen

The engine selected four incomplete definitions from `prescripted_countries/99_rinfix_prescripted.txt` and hid all four empires. Retire that file and supply four files at their exact vanilla 4.6.0 paths under `prescripted_countries/`. Carry over all 13 definitions in their original order. Apply one upstream translation change to each of the following empires.

| Vanilla file | Empire | Field | Value |
| --- | --- | --- | --- |
| `90_toxoids_prescripted_countries.txt` | `knights` | `ruler.ruler_title_female` | `PRESCRIPTED_ruler_title_female_knights` («Королева») |
| `89_first_contact_prescripted_countries.txt` | `resistance` | `ruler.ruler_title_female` | `PRESCRIPTED_ruler_title_resistance` («Вождь») |
| `88_astral_planes_prescripted_countries.txt` | `certeran_covenant` | `ruler.ruler_title_female` | `PRESCRIPTED_ruler_title_female_certeran_covenant` («Первая прародительница») |
| `00_top_countries.txt` | `plantoid_humans` | `adjective` | `PRESCRIPTED_adjective_plantoid_humans` (stem «Зеленеющ») |

Use the parser to compare structure and order with vanilla. The expected differences are three added title fields and one changed adjective reference. Verify that each ID has one effective definition. Add these four paths to the vanilla files reviewed on game updates.

## Job names

- In `common/pop_jobs/fake_jobs_rinfix`, remove the single `swap_type` block under `bureaucrat_rinfix` that calls the missing `bureaucrat_is_culture_worker` trigger. Both log entries point to line 421. Check the order and weights of the remaining branches. Vanilla defines `culture_worker` as its own job. The author supplies separate forms for leader backgrounds. Check biographies for both bureaucrats and culture workers, including «работником культуры» and «работницей культуры».
- Include the typo previously identified by source review in the general specification. In `GetResearcherPlural_rinfix` in `common/scripted_loc/scripted_loc_rinfix`, change `_evosymbiont_plural_rinfix_cases` to the existing `evosymbiont_plural_rinfix_cases` key. Check the reference and the rendered grammatical case.

## Empire adjectives

The log records 33 warnings for a different group of four empires. There are 16 for `gorthikan`, 15 for `graparx_trophy_hunters`, and one each for `guardianship_of_nyrr` and `free_sunbuilt_uplifters`. All four definitions point to an existing Russian entry with a stem and inflected forms. The vanilla Graparx entry has an additional `corp:Грапаркс $1$` form. The other three author entries cover all their vanilla grammatical tags.

Compare three runs using the same empires and DLC configuration — Russian vanilla, the modded setup with the fix, and that setup with only the vanilla Graparx `corp` form restored. Reopen the empire list and individual designs. Compare warnings by empire, the adjective in the editor and the generated names, including a corporate context where available. Accept a targeted fix for a reproduced case. Preserve the remaining forms until the requested variant is identified. The warning count does not identify that variant.

## Ship name inflection

All 9,217 names in the warnings match the upstream author’s strings. Every nominative fits within 26 characters. The complete strings contain 27–204 characters including grammatical markup. All carry gender and 9,205 include explicit case variants. Vanilla sets `SHIP_NAME_SIZE_MAX = 26` in `unchecked_defines/00_interface.txt`. These lengths suggest that the check may count the full string.

The user confirmed the previous check. Preserve the author's names, gender and case forms together with the vanilla length limit.

## Ship modifier labels

`setup.log` records five short keys for each of 320 vanilla ship sizes. All 1,600 are absent from vanilla EN, vanilla RU and effective Russian localisation. Comparing the names with `script_documentation/modifiers.log` and 2,351 vanilla `common/` and `events/` files found zero registered modifiers and zero direct uses under the short names. English and effective Russian strings contain zero direct `$short_key$` references. The initial review matched 126 similar labels using two naming patterns.

| Requested suffix | Meaning | References found out of 320 |
| --- | --- | ---: |
| `build_speed_mult` | Build speed | 41 |
| `build_cost_mult` | Build cost | 20 |
| `upkeep_mult` | Upkeep | 18 |
| `hull_mult` | Relative change to hull points | 36 |
| `hull_add` | Flat change to hull points | 11 |

Matching modifier IDs and economic categories identified 134 English labels. All resolve in Russian. Of the examined modifiers, 88 occur directly in vanilla scripts. All 88 are registered and have Russian text. All 32 labels explicitly referenced by localisation in this set also resolve in Russian.

The corvette technology uses `ship_corvette_cost_mult`. All six mauler variants share `ship_mauler_cost_mult`. Both effective Russian technology tooltips resolve to a 5% cost reduction and a 25% increase in build speed. The engine registers `shipsize_mauler_stage_1_hull_add` and `shipsize_mauler_stage_1_hull_mult`. Both lack a dedicated label in EN and RU and have no direct references in the scripts checked. File inspection cannot establish how the engine renders dynamically built tooltips.

The parser resolved all ten probe keys and both technology texts remained identical with the overlay. The control run on 25 November 2026 at 19:54 (UTC+7) recorded each of the 1,600 vanilla keys once, including all ten probe keys and the control `destroyer_hull_add`, plus 20 Tass keys. Its `error.log` contains none of the previous hidden empire, empty adjective, portrait or obsolete bureaucrat trigger messages. That log alone cannot verify each title and adjective in the editor. [Control run](../../TMP/RUS_FIX_FIX/ship_modifier_probe/control_run_20261125_195447.json).

In the test run on 25 November 2026 at 20:03:48 (UTC+7), vanilla entries in `setup.log` fell from 1,600 to 1,590. Comparing the counts for every key found exactly five entries removed for `corvette` and five for `mauler_stage_1`. The control `destroyer_hull_add` appeared once in each run. Both runs recorded 20 Tass entries. This confirms the startup check recognises the short keys. In-game label rendering was outside this experiment. The probe file was removed from the connected mod after the comparison. A player-visible blank label, raw key or mistranslation would justify a targeted change to the distribution. [Comparison of the two runs](../../TMP/RUS_FIX_FIX/ship_modifier_probe/result_run_20261125_200348.json) · [Script and localisation evidence](../../TMP/RUS_FIX_FIX/ship_modifier_audit_46.json).

## Acceptance

- **Before launch.** Use the parser to check the four empire files, job references, uniqueness of new keys, Russian reference resolution and preservation of upstream grammatical variants. Match modifier coverage to the vanilla 4.6.0 ship size definitions.
- **After the first batch.** The user opens the new game screen. All four empires should open with a portrait, origin and the specified title or adjective when the required DLC is available. Check the author’s `florin`, a sibling vanilla design and custom empire creation. Inspect the fresh `error.log` for the four duplicate definitions, four hidden designs and both trigger errors. Recheck the empty portrait warning separately. Its relationship to the designs is unconfirmed.
- **If a label defect is observed.** Record the language, exact screen and visible key. Match it to the effective modifier, English label and effective Russian text. Verify wording and numeric formatting in that same screen. Track the 20 Tass keys separately.
