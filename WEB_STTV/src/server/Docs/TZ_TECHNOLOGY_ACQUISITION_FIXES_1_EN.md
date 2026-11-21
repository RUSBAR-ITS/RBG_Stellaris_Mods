# WEB_STTV specification. Technology acquisition and starting eligibility. Iteration 1

## Contents

- [Scope](#scope)
- [Nine scripted rewards](#nine-scripted-rewards)
- [Starting eligibility](#starting-eligibility)
- [Import and server contract](#import-and-server-contract)
- [Acceptance](#acceptance)

## Scope

Draft for approval and appendix to the overall specification. In Stellaris 4.5.4 (1b4f), nine base technologies have empty acquisition sections despite traceable rewards. A further 19 starting technologies have eligibility conditions that their pages omit. These are 28 distinct technologies. This iteration covers the same content in the card tooltip and on the technology page in RU and EN. The main specification defines the complete scope and final acceptance. [Overall specification](TZ_TECHNOLOGY_ACQUISITION_FIXES_EN.md) · [Correction register](TECHNOLOGY_ACQUISITION_AUDIT_EN.md) · [Technology inventory](TECHNOLOGY_ACQUISITION_INDEX_EN.md)

## Nine scripted rewards

In the existing acquisition section, show the player action, beneficiary and outcome. For the seven precursor technologies, a minor artifact action starts a named special project. Successful completion leads to an event whose applicable outcome awards the empire **+10% research progress**. Read the action’s availability and the option conditions from their game definitions. For example, the Irassian action requires discovery of the Irassian world and is available until the action is first taken. The initiating empire owns the project. [Action](E:/SteamLibrary/steamapps/common/Stellaris/common/artifact_actions/artifact_actions.txt:556) · [Project success](E:/SteamLibrary/steamapps/common/Stellaris/common/special_projects/00_projects_ancient_relics.txt:150) · [Reward](E:/SteamLibrary/steamapps/common/Stellaris/events/ancient_relics_arcsite_events_2.txt:6630)

| Technology | Action | Project | Event | +10% award sites |
|---|---|---|---|---:|
| `tech_secrets_irassian` | `artifact_irassian_research` | `IRASSIAN_SECRETS` | `ancrel.9001` | 1 |
| `tech_secrets_yuht` | `artifact_yuht_research` | `YUHT_SECRETS` | `ancrel.10050` | 2 |
| `tech_secrets_league` | `artifact_league_research` | `LEAGUE_SECRETS` | `ancrel.10200` | 3 |
| `tech_secrets_cybrex` | `artifact_cybrex_research` | `CYBREX_SECRETS` | `ancrel.10250` | 2 |
| `tech_secrets_vultaum` | `artifact_vultaum_research` | `VULTAUM_SECRETS` | `ancrel.10100` | 5 |
| `tech_secrets_baol` | `artifact_baol_research` | `BAOL_SECRETS` | `ancrel.10300` | 3 |
| `tech_secrets_zroni` | `artifact_zroni_research` | `ZRONI_SECRETS` | `ancrel.10350` | 1 |

Example summary for Irassian Naval Yards: “Complete the special project ‘Delve into the Secrets of the Irassians’ to gain +10% research progress.” Identify the action “Secrets of the Irassians” in the source conditions. The server resolves both names by their game localization keys. [EN strings](E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/ancient_relics_l_english.yml:359)

Associate each award with the branch that grants it. Two mutually exclusive options granting 10% each may share a single “+10%” label with alternative conditions. Retain the addresses of all 17 award sites and the branch logic. Distinguish starting the project from completing it successfully. The executable command in the outcome establishes the source of the reward.

| Technology | Route, recipient and expected section |
|---|---|
| Boarding Cables · `tech_boarding_cables` | Disabling Captain Inax’s ship triggers `on_ship_disabled → grand_archive.8260 → grand_archive.8264 → grand_archive.8265`. The first branch uses the disabling ship’s controller if the combat flag matches. The other selects an eligible playable empire by its combat flag. The recipient must have `origin_treasure_hunters`. After the conversation, `after` grants the entire technology if still unknown. Show it in the completed-technology section. Every available reply leads to the same grant. [Entry](E:/SteamLibrary/steamapps/common/Stellaris/common/on_actions/00_on_actions.txt:2053) · [Recipient](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_grand_archive.txt:4400) · [Grant](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_grand_archive.txt:4509) |
| Materiality Engine · `tech_materiality_engine` | In the control ending of the `origin_shroud_forged` situation, `on_fail` calls `shroud_forged.50` for the situation target. Its reply starts `SHROUD_FORGED_REINTEGRATION`. Project success calls `shroud_forged.60`. Its reply schedules `shroud_forged.30` after 30 days. Reply `.30.a` unlocks the research option for an empire with this origin. Show it in the research-option section. [Situation outcome](E:/SteamLibrary/steamapps/common/Stellaris/common/situations/03_origin_situations.txt:232) · [Project success](E:/SteamLibrary/steamapps/common/Stellaris/common/special_projects/00_projects_origins.txt:14) · [Delay](E:/SteamLibrary/steamapps/common/Stellaris/events/shroud_forged_events.txt:571) · [Research option](E:/SteamLibrary/steamapps/common/Stellaris/events/shroud_forged_events.txt:214) |

## Starting eligibility

For a base technology with `start_tech = yes` and a nonempty `starting_potential`, add **“Starting eligibility” / «Получение на старте»** below the existing conditions in the availability section. The card’s starting marker continues to reflect `start_tech`. The new heading covers initial eligibility. General restrictions from `potential` remain visible alongside it, including when the starting block checks only civics. Omit the heading when the starting condition is absent. Tree filtering is a separate concern.

| Vanilla condition | Acceptance technologies |
|---|---|
| `is_nomadic = no` | `tech_solar_panel_network`, `tech_starbase_1`, `tech_starbase_2`, `tech_space_defense_station_1`, `tech_mechanized_mining`, `tech_colonization_1` |
| `is_nomadic = yes` | `tech_nomads_mechanized_mining`, `tech_waystation_1` |
| `is_low_tech_start = no` | `tech_basic_science_lab_1`, `tech_planetary_government`, `tech_maulers`, `tech_weavers`, `tech_weaver_bio_evasion_1`, `tech_weaver_bio_anti_evasion_1` |
| `is_low_tech_start = no` + `country_uses_bio_ships = no` | `tech_corvettes` |
| `is_eager_explorer_empire = yes` | `tech_subspace_drive` |
| `is_eager_explorer_empire = no` | `tech_hyper_drive_1` |
| `is_wilderness_empire = yes` | `tech_wilderness_terraform` |
| `has_origin = origin_fruitful` | `tech_critter_feeder` |

Render expanded scripted checks using localized names, preserving AND, OR and negation. Subspace Drive has a general First Contact requirement and requires **one of four** starting civics: `civic_eager_explorers`, `civic_privatized_exploration`, `civic_hive_stargazers`, `civic_machine_exploration_protocol`. The hyperdrive has the opposite starting condition. Corvettes require both conditions. The low-tech start trigger covers pre-FTL civilizations, two origins and the explorer civics. [Drive definition](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_first_contact_tech.txt:418) · [Trigger definitions](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:3877)

## Import and server contract

1. Include all `common/artifact_actions/*.txt` in the parser profile and the corresponding output path in the loader profile. Import each named root definition as one document in `artifact_actions`, keyed by its block name. Store its provenance in `artifact_actions_provenance` using loader conventions. The reference file contains 28 unique definitions. The parser handles local `@` declarations. Events, projects, situations and technologies are already imported. [Parser profile](../../../config/parser_sources.json) · [Loader profile](../../../config/loader.json)
2. Add artifact actions as entry points on the server. Follow executable calls, including `hidden_effect`, to the award command. Preserve entry conditions, branch decisions, recipient selection and command addresses. For Inax, resolve the call-site reassignment of `scopes.from`. For the situation, resolve `target` in its branch. Keep a diagnostic with its source address when reachability or the recipient cannot be established. Apply rules to the data. IDs in the tables are acceptance examples. [Source traversal](../sttv_server/progress_sources.py) · [Call paths](../sttv_server/acquisition_paths.py)
3. Extend `POST /api/trees/technology-tooltip` with an optional array of standard expressions in `sections.starting_potential`. The three scripted award types use the existing `research_options`, `researched_grants` and `research_progress` keys. Apply the existing disabled-DLC indication to proven source requirements. The server resolves RU/EN names and condition phrases. The shared frontend component renders the nodes and localized heading. [Condition text](TZ_CONDITION_TEXT_EN.md) · [Shared renderer](../../frontend/ui/composite/TechnologyTooltipDetails.tsx)
4. Include the input collections and rules in the existing revision mechanism for the source index and `technology_tooltips`. A warm request uses the prepared document. After an input change or a derived-data reset the next request returns the current routes and conditions. [Cache service](../sttv_server/tree/service.py)

## Acceptance

- **Import.** Compare the IDs of all 28 actions across vanilla input, parser artifacts and MongoDB. For the seven actions, trace each `enable_special_project` to its reward event and verify addresses and amounts at all 17 sites. Reproduce the result from project profiles.
- **Awards.** Check all nine technologies on both languages against the routes above. For Inax, cover both recipient branches, a different origin, an already known technology and the shared grant after every reply. For Materiality Engine, check the required situation outcome, project success, delay and award type. A test event, tooltip-only commands and grants to a separate NPC empire serve as negative controls.
- **Start.** Check every ID in the 19-technology table. Exactly those 19 base pages per language must include the new block in this snapshot. The other 23 of the 42 starting technologies retain the card marker and omit the empty heading. For both explorer-civic polarities and for Corvettes, inspect nesting and localized names. Compare tooltip and page under identical settings.
- **Regression.** Open all 679 base pages in a browser in RU and EN with all DLC enabled. Compare source identities, award types, branches, addresses, percentages, labels, icons and markup against the audit. The baseline is 478 technologies with a named source. After the nine fixes the minimum is 487. Record any additional routes found by the general rules with their IDs and game evidence. Investigate every lost or materially changed baseline source. Check a request with an applicable DLC disabled, a warm read and a derived-data reset followed by rebuilding.
- **Result.** Write the per-technology before/after differences, expected changes and remaining diagnostics to the run reports. Page checks verify the rendering and agreement with scripts. In-game acquisition remains a user check. [Baseline audit](TECHNOLOGY_ACQUISITION_AUDIT_EN.md) · [Browser checks](../../../tests/frontend/conditionPages.mjs)

[Русская версия](TZ_TECHNOLOGY_ACQUISITION_FIXES_1_RU.md)
