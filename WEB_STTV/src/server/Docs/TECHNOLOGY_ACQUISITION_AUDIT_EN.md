# Technology acquisition and readability audit

## Contents

- [Summary](#summary)
- [Correction register](#correction-register)
- [Changes since the first survey](#changes-since-the-first-survey)
- [Scope of verification](#scope-of-verification)

## Summary

Repeated the audit on 21 November 2026 for Stellaris 4.5.4 (1b4f). Chrome opened all 679 base technologies on the test site in Russian and English with all DLC enabled. All 1,358 pages passed checks for headings, displayed API text and inline images (768 occurrences). Game definitions, award types, sources and current wording were compared for each ID.

478 technologies show at least one named source. 289 show a research option, 248 a completed grant and 298 research progress. Sections overlap. The remaining 201 pages break down as follows.

| Base weight on 201 pages with no awards | Count | Interpretation |
|---|---:|---|
| One positive value | 156 | Candidates for normal research, subject to prerequisites, availability and weight modifiers. |
| Unspecified | 27 | All 27 carry the starting technology flag. |
| One zero value | 16 | Six debris candidates, nine scripted rewards and one conditional starting technology. |
| Declared twice | 2 | Dyson Swarm and Orbital Arc Furnace each declare 0 and 70. The third conflict, Dyson Gun, occurs on a page with a reward. |

[Index of all 679 technologies](<TECHNOLOGY_ACQUISITION_INDEX_EN.md>) · [Debris and the 16 priority technologies](<TECHNOLOGY_DEBRIS_AUDIT_EN.md>)

## Correction register

Coverage counts distinct technologies unless the unit is script sites. Groups overlap. Priority 1 concerns acquisition and condition meaning. Priority 2 covers indirect sources and presentation.

| Priority and area | Coverage | Finding | Correction or check |
|---|---|---|---|
| 1. Scripted rewards | 9 | Seven precursor secrets, Boarding Cables and Materiality Engine have empty acquisition sections. | Connect artifact actions to successful special projects (+10%). Show the Captain Inax grant for the cables and the research option following reintegration for the engine. [Nine reward chains](<TECHNOLOGY_DEBRIS_AUDIT_EN.md>) |
| 1. Debris research | 6 priority cases of 110 | Mining Drone Lasers, Cloud Lightning Conduits, Extradimensional Weaponry, Scourge Missiles, Swarm Spawning Pools and Cetana’s Nanites have no displayed acquisition sources. | Identify an equipped carrier and the requirements for researchable debris. Base progress is 10%. Exclude named fleets that forbid debris and verify combat outcomes in game. [Carriers and exclusions](<TECHNOLOGY_DEBRIS_AUDIT_EN.md>) |
| 1. Conditional starting grants | 19 of 42 starting | The card marks starting technology, but the page omits starting_potential. Ten of these 19 have no other acquisition sections. | State which empires start with it. Subspace Drive requires First Contact and one of four civics. [starting_potential](<E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_first_contact_tech.txt:447>) |
| 1. Entry point and recipient | 112 / 52 / 126 across 222 IDs | 112 have a reward with an unconfirmed entry point, 52 an unresolved recipient and 126 an unresolved system-initializer recipient (536, 685 and 801 command sites respectively). | Start with the Scion gift origin.21 (14 technologies) and observation outcomes. For preftl.2070 the situation completes, chooses fervent_belief and invokes the event. Verify the beneficiary separately from the situation owner. Keep NPC creation grants separate. [origin.21](<E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_1.txt:424>) · [preftl.2005](<E:/SteamLibrary/steamapps/common/Stellaris/common/situations/04_first_contact_dlc_situations.txt:423>) · [preftl.2070](<E:/SteamLibrary/steamapps/common/Stellaris/events/first_contact_dlc_situation_events.txt:3301>) |
| 2. Normal draw and indirect unlocks | 10 positive weights with a zero factor | A positive base weight can have a top-level zero factor or an unconditional ×0 modifier. Base zero also needs interpretation. Xeno-Linguistics has a conditional add = 100. | Interpret a draw together with its modifiers and prerequisites. Omega Theory has weight 60 and requires both predecessors. Both have weight 60 multiplied by zero unconditionally and have research options opened by Horizon Signal events. Explain this dependency on the Omega Theory page. [Omega](<E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_horizonsignal_tech.txt:58>) · [Horizon Signal](<E:/SteamLibrary/steamapps/common/Stellaris/events/horizonsignal_events.txt:493>) · [add](<E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:6572>) |
| 2. Random and shared rewards | 79 / 14 / 1 / 34 sites | Scripts contain 79 add_random_research_option, 14 copy_random_tech_from, one progress_all_researches and 34 copy_techs_from occurrences, including effect definitions. | For a random option show area, category, tier, applicable restrictions and progress. Theft depends on the other empire’s knowledge, positive weight and potential. General progress advances current research. Establish the receiving country before classifying mass copies. The number of eligible technologies depends on the campaign. [99%](<E:/SteamLibrary/steamapps/common/Stellaris/events/ancient_relics_arcsite_events_1.txt:717>) · [10%](<E:/SteamLibrary/steamapps/common/Stellaris/events/nemesis_operations_events_1.txt:764>) · [Foresight](<E:/SteamLibrary/steamapps/common/Stellaris/events/shroud_events.txt:12077>) |
| 1. Flag meaning | 327, including 189 with indistinguishable flags | Different checks on the same page can display the same sentence. 98 pages test crisis_special_project_4_complete. | Name the action and its owner. The same flag is set by Nemesis crisis projects and a BioGenesis project. Use the specific project name when the route determines it. [Nemesis](<E:/SteamLibrary/steamapps/common/Stellaris/common/special_projects/00_projects_nemesis.txt:491>) · [BioGenesis](<E:/SteamLibrary/steamapps/common/Stellaris/common/special_projects/05_projects_biogenesis.txt:54>) |
| 1. Conditions and objects | 58 / 133 / 171 RU, 177 EN¹ | 58 pages show an unresolved condition, 133 a saved event target, and 171 RU and 177 EN explicitly mention an unavailable name or translation. Ordered Retreat includes a comparison of an unnamed value against 100. | Start with current_awareness_level, species_portrait and inverted_switch. Name the owner and variable in comparisons. Resolve saved target roles from their assignment. [current_awareness_level](<E:/SteamLibrary/steamapps/common/Stellaris/events/first_contact_dlc_operations_events.txt:3475>) |
| 2. Source headings | 106 with a source title alone, 30 with identical headings | Arkship Construction has three council agendas with identical headings and a development focus reward with an unavailable name. 62 pages show a generic scripted event step. | Give the source type and distinguishing condition, such as the civilian, military or science arkship agenda. For hidden events, name the verified player action and keep the ID in details. |
| 2. Length and nesting | 50 with 500+ text nodes, 72 at depth 10+ | Temple of Transportation contains 22,896 text nodes in one language at depth 14. Ordered Retreat has 22,603. The outcome is difficult to find in the expanded branches. | Show the player action, beneficiary and outcome first. Present shared conditions once with complete branches on demand. Preserve AND/OR, negation, relative weights and distinct rewards. |
| Source data review | 3 | Dyson Swarm, Dyson Gun and Orbital Arc Furnace each declare two base weights. | Retain both values in source order and check the engine’s effective weight. |

¹ Diagnostics and visible text are counted separately. For example, unknown_condition occurs on 61 pages in each language, while 58 show the specific unresolved-condition phrase. A neutral description of the ruler or planet is appropriate when its name is available only in a running campaign.

## Changes since the first survey

Rechecked the Blue Lasers event title, active-event condition and station module. No main page text contains the earlier raw numeric event IDs (previously 252 pages), on_… hooks (314), simultaneous success/failure captions (119), deposits named “no” (40), unrendered icons (151), or Russian grammar tables (31). The register lists the semantic gaps that remain. [First readability survey](<../../../Docs/frontend/TECHNOLOGY_PAGE_READABILITY_EN.md>)

| Previously questioned technology | Current acquisition entries |
|---|---|
| Frozen World Habitats (tech_cryovault) | Research option from extreme_frontiers.1020. |
| Alloy Fossilization (tech_alloy_fossilization) | Research option from extreme_frontiers.435. |
| Trinary Computing and Ordered Retreat | Options from pre-FTL observation insights, including fircon.10. |
| Thruster Bio-integration | Two fauna component insights and a separate starting grant to Beastmasters. |

Recheck of the remaining findings from the first survey. RU / EN are technology counts per language. Where the original symptom changed, the last column specifies what the repeat check measured.

| Original symptom | Earlier RU / EN | Current observation |
|---|---:|---|
| Condition displaying its key in parentheses | 379 / 379 | 0 in the old form. 58 / 58 explicitly report incomplete interpretation. |
| Generic country flag wording | 302 / 302 | The literal phrase occurs on 301 / 301. All generic flag captions together affect 327 / 327. |
| Bare source title and nested “Source — …” | 478 / 478, 433 / 433 | 106 / 106 include a source type rendered by title alone. The old nested prefix disappeared. 62 / 62 show an unnamed scripted step. |
| Literal localization keys and other underscore tokens | 422 / 423, 165 / 165 | No technical underscore tokens found in displayed text. Unavailable object names are tracked in the correction register. |
| Dotted scope paths | 23 / 23 | The three old literal paths disappeared. Target roles still fall back on 133 / 133 pages. |
| Campaign substitutions | 68 / 67 | No raw bracketed Get expression found. Campaign-dependent localization is diagnosed on 66 / 65 pages. |
| Static placeholders, literal newline and concept reference | 3 / 3, 14 / 14, 1 / 1 | None of the three earlier markup forms was found in the main text. |

## Scope of verification

Scanned installed common, events, map and prescripted_countries scripts and DLC inputs (2,265 text files and 32 archives checked). Found 1,084 direct named commands of the three award types outside library definitions and tooltip blocks. Matching technology, award type, file and source object left six commands from two events marked is_test_event = yes and always = no. All others matched the scripted path inventory. Expanded calls were cross-checked against displayed award sources for every ID. A script occurrence alone does not establish a player reward.

Known NPC grants and branches excluding the player are kept separate from player rewards. Source definitions include 206 technology_swap blocks without separate published pages. The audit covers base pages with all DLC enabled. Combat debris, campaign-specific random pools and duplicate-weight precedence remain for in-game verification. Length thresholds select examples for review and do not by themselves establish a defect.

[Inventory with sources and diagnostics](<../../../../TMP/WEB_STTV/technology-audit/reports/audit.json>) · [Vanilla command locations](<../../../../TMP/WEB_STTV/technology-audit/reports/vanilla-sites.json>) · [Fresh browser results](<../../../../TMP/WEB_STTV/technology-audit/reports/browser/pages.json>)
