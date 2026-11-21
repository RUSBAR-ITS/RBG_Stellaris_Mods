# Technology acquisition in Stellaris 4.5.4 (1b4f)

## Contents

- [Audit results](#audit-results)
- [Test server](#test-server)
- [Page caption audit](#page-caption-audit)
- [Limits of verification](#limits-of-verification)

## Audit results

| Area | Findings |
|---|---|
| Named rewards | The index identifies 17 reward sites for the seven precursor secrets, the Boarding Cables grant and the Materiality Engine research option. Each command records the branch, outcome, recipient and any stated progress. |
| Debris | Of the 110 candidates in the original audit, 109 have a confirmed path from a component to a ship design and its creation. Mining Drone Lasers now show this route under research progress. The outstanding case for tier-one torpedoes is described below. |
| Starting research | Of 42 starting technologies, 19 have conditions for the starting grant. The other 23 have no starting-conditions section. |
| Entry and recipient | The index tracks 14 Scion gifts and 26 executions of pre-FTL rewards for 13 technologies. The register distinguishes confirmed player paths, new countries, unreachable branches and transitions with an unresolved recipient. |
| Ordinary and indirect research | Omega Theory links to both mandatory prerequisite technologies. The event source belongs to the preceding research step. Conditional weight additions and alternative prerequisites are preserved. |
| Random and general effects | The audit covers 79 random research-option sites, 14 random technology copies, 34 bulk copies and one grant of progress to current research. A general effect can have a known outcome type while the technology selected depends on the campaign. |
| Flags | Known setters carry the owner, source, option and stage. The fourth crisis project distinguishes the Nemesis and BioGenesis branches. The register counts a visible generic caption separately from a missing dedicated flag translation. |
| Operands and objects | Conditions include pre-FTL awareness, portraits, resources, counters and technology-dependent switches. The register lists outstanding operands and object references for each language. |
| Source names | Sources have types. The three arkship agendas carry their respective roles. Hidden stages use confirmed entries where available. The register lists coinciding visible titles by source ID. |
| Long branches | The card and page show the reward summary first. Details open by mouse or keyboard. The browser check expands the branches and looks for each condition delivered by the API. |
| Conflicting weights | Dyson Swarm and Orbital Arc Furnace retain 0 and 70. Dyson Gun retains 0 and 50. The values follow source order. The engine's effective value remains an open question. |

## Test server

The live test database `wiki` was dropped, recreated, imported and verified against the input documents. Its final 110 input collections contain 346,641 documents, including 304,812 localization records, 28 minor artifact actions and 436 ship designs. After final publication the loader verified the entire localization collection against the configured input directory. The other 109 collections retained their UUIDs from the full verification.

The baseline covers 1,084 direct commands naming a technology. The comparison found executions for 1,078. The remaining six belong to two test events. A further 128 sites use dynamic effects. The audit found callers for 127. The example caravan deal has no caller in this game snapshot.

The number of technologies with a confirmed named reward increased from 478 to 490. There is a research option for 290 technologies, a full grant for 261 and partial progress for 305. These groups overlap. The comparison preserved the addresses of previously displayed rewards. Random effects and debris are counted separately.

All 97 technologies with a single explicit base weight of zero now show at least one route. Ninety have a named reward, another six have a debris analysis route and one has a conditional starting grant. The per-ID list with overlapping methods is in `zero-weight.json`.

The 37 local server checks and three checks against the test server passed. The live checks cover localization lookup, invalid input, and concurrent tree publication using isolated test collections. The reference UI was checked after combined and individual resets, on repeat opening, and with a reward source requiring disabled DLC. The tree contains 678 technologies with 36 DLCs and 464 with none. Individual pages are checked for all 679 IDs.

On the final release, the browser opened and expanded 1,358 pages. The checks found zero rendering failures, lost baseline reward addresses or unrecognized condition operators in this snapshot. Blue Lasers showed identical card and page content before and after keyboard expansion. MongoDB contained all 679 tooltip documents. The largest was 3,925,771 bytes.

The run writes results to `TMP/WEB_STTV/acquisition-fixes/reports/`. The file `source-comparison.json` links the game source line to its execution. The file `player-paths.json` records recipients and branch conditions. The file `dynamic-sites.json` covers dynamic effects. Look up a technology ID in `register.json` to compare results across languages. The file `wording-limits.json` lists the operands and technologies affected by remaining generic captions. The browser results for each page are in `release/pages.json`. [Comparison program](../tests/acquisition_review.py) · [Specification](TZ_TECHNOLOGY_ACQUISITION_FIXES_EN.md)

To repeat acceptance, collect command sites from the installed game and DLC archives, then collect execution paths from the parser snapshot. Run the browser checks in both languages and pass the captures and baseline audit to `acquisition_review.py`. For flags with identical or generic captions, `flag-limits.json` includes the setters, scopes and branches found in the imported data. [Game source scan](../tests/acquisition_vanilla_sites.py) · [Parser snapshot scan](../tests/acquisition_acceptance.py) · [Browser check](../../../tests/frontend/conditionPages.mjs)

## Page caption audit

The audit reads the title, description, reward summaries and expanded conditions of all 679 technologies in each language. It uses the application's own dictionaries to identify missing names, generic target labels, unidentified operands, empty logical groups and campaign-dependent values. Each finding records the section, source, sample text and technology IDs. [Wording audit](../tests/audit_visible_wording.py)

The test browser expanded all 1,358 pages. Each count is the number of technologies with a match in that language. A technology can occur in more than one row.

| Caption type | Before, RU / EN | After, RU / EN |
|---|---:|---:|
| Missing source name | 538 / 538 | 0 / 0 |
| Other messages about an unavailable name, unidentified module or missing translation | 188 / 488 | 0 / 0 |
| Generic saved-target or saved-object label | 166 / 166 | 0 / 0 |
| Empty logical group heading | 33 / 33 | 0 / 0 |

All previous reward addresses and sources remained present. The collapsed and expanded Blue Lasers card matched its standalone page. The wording reports are `TMP/WEB_STTV/condition-targets/reports/visible-before.json` and `visible-final.json`. The browser results are in `TMP/WEB_STTV/condition-targets-final/reports/release/pages.json`. Run the wording audit with `--check` to fail the check if a tracked placeholder or empty group reappears.

| Technology | What the page shows | Script evidence |
|---|---|---|
| Gravity Snares | Contact with any of five named kinds of space fauna or one of four active civics. Both alternatives require Grand Archive. | Each fauna branch checks the existence of the same target and communications with it. |
| Rift Sphere | Stage four of the Ancient Crater excavation checks that a science ship has an assigned leader. The empire controlling the fleet receives 50% research progress if it has yet to research the technology. | The fourth stage block, the ship class, the assigned leader and the technology check in the `controller` scope of `astral_planes.2140`. |
| Trinary Computing | The monthly event can run if an empire has built an observation post over a pre-FTL world, or a nomadic empire has a qualifying station. Each empire that passes its own branch conditions can receive the research option. | Building a post sets the flag in `fircon.5`. The outer event check and individual recipient checks are at different levels in `fircon.10`. |

The server assembles each block from game checks, calls and rewards. A hidden event can be described by its scripted action, its caller or the subject of its event chain. Individual names assigned during a campaign retain a description of their role. The `Story41` flag blocks the pre-sapient contact event. Its setter could not be established in the inspected scripts.

## Limits of verification

In the execution register, 224 entries across 85 technologies have no confirmed chain entry. The recipient is unresolved for 685 entries across 52 technologies and for a further 624 initializer entries across 12 technologies. The same technology can also have an independently confirmed route. Each disputed command retains its source address and scope sequence.

Names of rulers, planets and saved targets can depend on the campaign. A technical object may lack a localization entry. These cases are reported separately. Caption counts cover all expanded branches, including the conditions of shared rewards. The same flag in a shared event can affect hundreds of technology pages.

| Caption in the original acceptance run before the name fixes | RU pages | EN pages |
|---|---:|---:|
| At least one unavailable object or source name | 545 | 547 |
| Generic flag caption | 133 | 133 |
| Distinct flags share a caption at least once | 478 | 478 |
| Generic saved-target caption | 79 | 79 |
| Hidden intermediate step | 121 | 121 |
| Different reward sources share a title | 25 | 22 |

Among flags with generic or coinciding captions, 263 check/flag pairs have recorded setting operations. For 67 pairs, the imported inputs contain no setter matching the flag key and scope.

For `tech_torpedoes_1`, a confirmed frigate design carries a combat computer with two prerequisite technologies. The scripts do not identify which technology would receive research progress. Inax's fleet separately prohibits debris. The 10% figure for confirmed carriers comes from the game define for debris analysis. Debris generated after combat, the outcome of a random selection in a particular campaign and precedence for duplicate weight declarations require in-game checks.

[Русская версия](TECHNOLOGY_ACQUISITION_RESULTS_RU.md)
