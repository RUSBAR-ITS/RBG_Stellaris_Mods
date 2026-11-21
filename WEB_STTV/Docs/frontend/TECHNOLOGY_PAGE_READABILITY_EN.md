# Technology page readability in Stellaris 4.5.4

## Contents

- [Coverage](#coverage)
- [Blue Lasers](#blue-lasers)
- [Recurring findings](#recurring-findings)
- [Displaying sources and conditions](#displaying-sources-and-conditions)
- [Icons and localization](#icons-and-localization)
- [Checks for a future change](#checks-for-a-future-change)

## Coverage

On 21 November 2026 the published page data was checked for all 679 base technologies in Stellaris Cygnus v4.5.4 (1b4f). All 1,358 RU/EN requests succeeded with the default selection of all DLC. The page and the tooltip use the same endpoint. The survey covered names, descriptions, prerequisites, availability, weight and all three acquisition sections. Six direct pages were also opened in Chrome in each language. Other DLC selections and playthroughs were outside this measurement. [Keys, examples and affected technology IDs](../../../TMP/WEB_STTV/technology-page-readability/reports/inventory.json) · [Browser checks](../../../TMP/WEB_STTV/technology-page-readability/reports/browser.json)

In the inventory, `display` records patterns found in visible text. `diagnostics` records the server's findings. Each lists affected technology IDs. A `ru_en` list applies to both languages. The `game_event_definitions` section traces visible event IDs to vanilla files and `inline_sprites` maps icons to textures. Script-like tokens and substitutions are candidates for review. The scan cannot establish the grammatical correctness of every other sentence.

## Blue Lasers

**Observation.** “Medical Side Effects” is the title of `fircon.2001`, received by the observation post owner. Its caller `fircon.2000` is a hidden situation event with no title. The monthly pre-FTL observation event table assigns this outcome a relative weight of 50. The situation and the gatekeeper `preftl.50` determine whether the table is reached. [Situation](<E:/SteamLibrary/steamapps/common/Stellaris/common/situations/03_AI_empire_situations.txt:54>) · [Table invocation](<E:/SteamLibrary/steamapps/common/Stellaris/events/first_contact_dlc_situation_events.txt:367>) · [Outcome weight](<E:/SteamLibrary/steamapps/common/Stellaris/common/on_actions/00_on_actions.txt:166>) · [Both events](<E:/SteamLibrary/steamapps/common/Stellaris/events/first_contact_dlc_events.txt:4707>)

Example presentation of one branch:

> **Event “Medical Side Effects”**  
> May occur during monthly observation of a pre-FTL civilization. Its capital must have an observation post with an owner and the “Aggressive Observation” mission. Requires First Contact.  
> Choose the response to increase beam power and test it on the population.  
> If Blue Lasers is the selected reward and can be researched, an unavailable research option opens with +80% progress. An already open option receives +100% progress.

This excerpt omits other conditions for brevity. The full view also needs lithoid and machine exclusions, event repetition flags, previously researched lasers and the recipient. The situation owner's checks concern the observed civilization. The observing empire receives the choice and reward. Intermediate steps and their IDs can remain available in details. [Observation trigger](<E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/02_scripted_triggers_first_contact_dlc.txt:50>) · [Technology selection](<E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/first_contact_dlc_effects.txt:824>) · [Progress award](<E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/00_scripted_effects.txt:4903>)

**Crisis.** “Existential Threat” is the fifth crisis level. Unlocking it schedules “The Aetherophasic Engine” five days later. Its response options schedule “The Star-Eaters” a further five days later. That event grants missing technologies including Blue Lasers. This is the meaning of `on_unlock` in this branch. [Level definition and event call](<E:/SteamLibrary/steamapps/common/Stellaris/common/crisis_levels/00_crisis_levels.txt:154>) · [Choices and grants](<E:/SteamLibrary/steamapps/common/Stellaris/events/nemesis_crisis_endgame.txt:188>)

| Current display | Proposed reading |
| --- | --- |
| A false condition containing “Additional condition (has_active_event)” | “The event ‘The End is Nigh’ must be inactive.” The expression is `NOT { has_active_event = { crisis.4135 } }`. Other branches pass entire lists of events. |
| “Additional condition (has_starbase_module)” | “A nomadic empire must own a waystation with an Aetherophasic Anchor module.” Non-nomadic empires satisfy the other arm of the `OR`. The module name is available under `sm_waystation_aetherophasic_anchor`. |
| Russian inflection table for `primitive` followed by “Additional condition (capital_scope)” | “The observed country is a pre-FTL civilization.” Follow with the observation post checks above. The bare game key is an adjective. The country type needs a noun label, and the capital scope needs its child checks. |
| Both success and failure text about completing a project | “The fourth special project in the Become the Crisis chain is complete.” A reference page has no current campaign state with which to choose a success or failure indicator. |

The game script and localization contain the operands, negation, nested checks and required names. [Crisis level conditions](<E:/SteamLibrary/steamapps/common/Stellaris/common/crisis_levels/00_crisis_levels.txt:156>) · [Event](<E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/nemesis_content_l_english.yml:126>) · [Mission](<E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/main_3_l_english.yml:2456>) · [Module](<E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/nomads_2_l_english.yml:742>)

## Recurring findings

Counts are distinct pages for each pattern. A technology can occur in several rows.

| Visible pattern | RU | EN | Finding |
| --- | ---: | ---: | --- |
| “Additional condition (key)” | 379 | 379 | 134 spellings, 132 case-insensitive keys. A value, comparison or nested block disappears. |
| Numeric event ID in the text | 252 | 252 | 148 different events including hidden checks, dialogs with inherited titles and one event with a missing translation for its title. |
| Literal `on_…` | 314 | 314 | 57 hooks and lifecycle stages. `on_unlock` alone appears on 123 pages. |
| Generic special empire condition | 302 | 302 | Diagnostics identify 281 distinct check and flag pairs lacking a specific label. |
| Success and failure captions shown together | 119 | 119 | One `custom_tooltip` reads as several conditions. |
| A deposit named “no” | 40 | 40 | The boolean `has_deposit = no` was rendered as a deposit name. Display “There are no deposits”. |
| Unsupported inline icon | 151 | 151 | Six tokens, listed below. |
| Complete `\|\|\|` inflection table | 31 | 0 | `primitive` affects 21 pages. Other cases include names and dynamically inflected phrases. |
| Bracketed game-context substitution | 68 | 67 | Includes ruler and planet names in responses that depend on the ongoing game. |
| Unresolved dollar-delimited reference or number | 3 | 3 | Two population variables and `ACCORD_INTENSIFICATION_TRIGGER_ONCE`. |
| Literal `\n` | 14 | 14 | The string includes an encoded line break. |
| Game concept reference | 1 | 1 | `tech_cloning` prints `['concept_biomorphosis']`. Both translations already provide the name “Biomorphosis” / «Биоморфоз» through `concept_biomorphosis → genetic_ascension_situation`. |

478 technologies have a confirmed acquisition source. On 433 pages at least one intermediate step says simply “Source”. Among 394 distinct events used as group headings, 12 titles contain game color markup and 382 do not. The purple `§U` in the Blue Lasers example comes from the crisis level's localized name.

## Displaying sources and conditions

1. **Type and order.** Show paths from the triggering action to the reward. Label events, crisis levels, anomalies, situations and special projects by type. Give event titles a consistent style in both themes. Preserve game formatting in quotations and responses. Return a type and ID for intermediate sources and preserve the subject, operator, operand and children of each check. Currently the root group carries a source type, while intermediate steps use a generic phrase. [Section builder](../../src/server/sttv_server/progress_content.py) · [Renderer](../../src/frontend/ui/composite/TechnologyTooltipDetails.tsx)
2. **Title or purpose.** Of the 148 visible event IDs, 129 explicitly set `hide_window = yes` and have no title. Use the verified trigger path to explain their purpose. For example, “On completion of the Experimental Testing situation” can replace `shroud.1010` on 98 pages. Another 18 events inherit a title through `base`, including nine dialogs declared through inline scripts. `leviathans.4105` inherits “Curators” and lets the player choose a collection reward stage. Follow the base chain, respect local overrides and detect cycles. `tutorial.53` declares `tutorial.52.name`, for which no entry was found in the checked RU/EN sources. Cases like this need a project label. Keep technical IDs in details. [Situation completion](<E:/SteamLibrary/steamapps/common/Stellaris/common/situations/13_shroud_situations.txt:551>) · [Curator dialog](<E:/SteamLibrary/steamapps/common/Stellaris/events/leviathans_events_1.txt:7523>) · [Existing title lookup](../../src/server/sttv_server/progress_sources.py)
3. **Dictionary and game localization.** Maintain RU/EN phrases for actions and roles, such as “Upon unlocking the crisis level” and “Upon first entering this situation stage”. Interpret `on_first_enter` in the owning object's context. Resolve event, module, mission and council agenda names using type-specific rules. For example, `agenda_arkship_engineering_civilian` already has `council_agenda_agenda_arkship_engineering_civilian_name`. Research the setter, clearing conditions and owning scope before describing a flag. The observer's `fircon_2000_fired` is set for 1,800 game days at the start of “Medical Side Effects”. [Flag assignment](<E:/SteamLibrary/steamapps/common/Stellaris/events/first_contact_dlc_events.txt:4755>) · [Council agenda name](<E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/nomads_1_l_english.yml:2638>)
4. **Scope and operand type.** `capital_scope`, `from.owner` and `any_owned_megastructure` change the subject. Render child checks under the correct subject. `check_variable` and `resource_stockpile_compare` need a quantity, comparison, value and any multiplier. Flags require polarity and an owner. `has_active_event` can take a list, `has_starbase_module` takes a module and `has_deposit` accepts a boolean or a deposit ID. When a condition is partly understood, retain the known structure and mark the unresolved part. It can affect an entire `NOT` or `OR`.
5. **Repetition.** Five choices in the event preceding “The Star-Eaters” lead to the same reward. Show shared steps and checks once while keeping choice-specific restrictions. Group by object identity, action and equivalent results. Identical prose can refer to distinct recipients, reward amounts or checks. Preserve the three acquisition sections.

## Icons and localization

| Token | Pages | Vanilla texture relative to `gfx/interface/icons/` |
| --- | ---: | --- |
| `trigger_no` | 148 | `text_icons/trigger_no.dds` |
| `trigger_yes` | 119 | `text_icons/trigger_yes.dds` |
| `engineering` | 5 | `resources/engineering_research.dds` |
| `opinion` | 3 | `text_icons/tooltip_opinion.dds` |
| `physics` | 2 | `resources/physics_research.dds` |
| `pop` | 2 | `text_icons/icon_text_pop.dds` |

All six sprite definitions and textures exist. The loader profile already includes the two research images. These need token mappings. The other four need images and accessible RU/EN labels. A paired `success_text/fail_text` in reference mode should yield one neutral requirement. A standalone inline icon can still be displayed where the source text calls for it. [Vanilla sprites](<E:/SteamLibrary/steamapps/common/Stellaris/interface/texticons.gfx:290>) · [Image loader profile](../../config/loader_images.json) · [Inline icon map](../../config/frontend/game_text_icons.json)

Select a complete inflected form for its context or use a verified object label. Truncation at the first separator leaves a Russian adjective stem. For a dynamic reference such as `[Target.Owner.GetRulerName]`, substitute a role like “the ruler of the observed civilization” only where the chain establishes that role. `@extermination_pop_loss` and `@destruction_planet_pop_min` reference static variables in this release. Resolve them from versioned data and diagnose the missing `ACCORD_INTENSIFICATION_TRIGGER_ONCE` key separately. [Russian inflection data](../../../Localisation_Base/1-Prio_Russian_Localization_Fix_RE/russian/first_contact_l_russian.yml) · [Scripted variables](<E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_variables/09_scripted_variables_shroud.txt:178>)

## Checks for a future change

Start with incorrect condition semantics, then cover source labels and icons. Compare a fresh RU/EN sweep to the per-ID inventory. On Blue Lasers verify negated “The End is Nigh”, the nomadic anchor requirement, the recipient and both progress awards. Use `tech_containment_vessel` for inherited curator titles, `tech_administrative_ai` for situation completion, `tech_alloy_fossilization` for absent deposits and `tech_psionic_bombers` for static variables and a missing translation key. Compare acquisition sources, branches and amounts before and after changing the display. These are proposals for the next specification.
