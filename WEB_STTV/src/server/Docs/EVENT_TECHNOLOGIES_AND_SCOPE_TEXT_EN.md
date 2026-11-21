# Event technologies and participants in conditions

## Contents

- [Technology acquisition](#technology-acquisition)
- [Tree settings](#tree-settings)
- [Conditions and rewards](#conditions-and-rewards)
- [Acceptance](#acceptance)

## Technology acquisition

Of 679 technologies in the Stellaris 4.5.4 snapshot, 97 have an unambiguous explicit base weight of zero. Two can gain positive weight. Of the other 95, 55 have only event rewards or researchable debris and 40 have an independent acquisition method. Ten technologies joined the event group in this revision.

| Technologies | How the reward becomes available |
|---|---|
| Materiality Engine | Origin setup starts the chain. The situation outcome and successful reintegration project lead to the research option. |
| Frequency Tuning | First contact with the Tiyanki or completion of the Fruitful Partnership project. |
| Seven precursor secrets technologies | The artifact action opens a project. Research progress follows its outcome. This group includes Irassian Naval Yards. |
| Rift Sphere | Two sources are confirmed, including a situation outcome. |

Subspace Drives retain their starting path. Engine Bio-Integration has both a starting path and an event path. The Colossus retains its ascension perk path. An unknown weight, an unresolved additive modifier or a material uncertainty about acquisition keeps a technology visible to this filter. The server records the source, reward and game definition address of confirmed paths. [Specification](TZ_EVENT_TECHNOLOGIES_AND_SCOPE_TEXT_EN.md)

All ten reclassified technologies have zero base weight and no positive additive weight modifier. The events listed below execute the reward commands.

| Technology | Events executing the reward commands |
|---|---|
| `tech_secrets_cybrex` | [ancrel.10250](E:/SteamLibrary/steamapps/common/Stellaris/events/ancient_relics_arcsite_events_2.txt:6915) |
| `tech_secrets_league` | [ancrel.10200](E:/SteamLibrary/steamapps/common/Stellaris/events/ancient_relics_arcsite_events_2.txt:6773) |
| `tech_secrets_irassian` | [ancrel.9001](E:/SteamLibrary/steamapps/common/Stellaris/events/ancient_relics_arcsite_events_2.txt:6543) |
| `tech_secrets_vultaum` | [ancrel.10100](E:/SteamLibrary/steamapps/common/Stellaris/events/ancient_relics_arcsite_events_2.txt:7016) |
| `tech_secrets_yuht` | [ancrel.10050](E:/SteamLibrary/steamapps/common/Stellaris/events/ancient_relics_arcsite_events_2.txt:6659) |
| `tech_secrets_baol` | [ancrel.10300](E:/SteamLibrary/steamapps/common/Stellaris/events/ancient_relics_arcsite_events_2.txt:7487) |
| `tech_secrets_zroni` | [ancrel.10350](E:/SteamLibrary/steamapps/common/Stellaris/events/ancient_relics_arcsite_events_2.txt:7635) |
| `tech_rift_sphere` | [astral_situation.20](E:/SteamLibrary/steamapps/common/Stellaris/events/astral_planes_situation_events.txt:172) · [astral_planes.2140](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_astral_planes.txt:232) |
| `tech_materiality_engine` | [shroud_forged.30](E:/SteamLibrary/steamapps/common/Stellaris/events/shroud_forged_events.txt:201) |
| `tech_space_whale_weapon_1` | [first_contact_critters.15](E:/SteamLibrary/steamapps/common/Stellaris/events/first_contact_NPC_country_types_events.txt:139) · [origin.7005](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_5.txt:57) |

## Tree settings

| DLC selection | Visible with filter off | Visible with filter on |
|---|---:|---:|
| All enabled | 678 | 623 |
| All disabled | 464 | 443 |

Counts agree in regular and mixed trees. Each pair is checked for matching parents, children, RU/EN coordinates, reserved cells and repeat opening with the same ID. With all DLC enabled the mixed tree links Gravity Snares to Artificial Breeding. Regular trees display them in Physics and Society respectively.

## Conditions and rewards

The server resolves participants at the point of use. An event’s recipient, the previous lexical scope and scopes supplied by a caller have separate roles. Battle subscribers retain the original combatants and fleets. Special projects use their outcome stage and anomalies use their event dispatch form. Ambiguous entry paths retain their alternatives and diagnostic addresses.

The Paradox Titan shows the required DLC and a condition excluding empires using bioships. Its reward identifies the empire reaching Cosmogenesis level four. The Something Waiting excavation identifies the assigned scientist. The Irassian homeworld discovery flag has a dedicated condition. For flags with unresolved meaning the UI identifies the known participant and setting actions. Diagnostic records retain the flag ID and script addresses.

## Acceptance

The MongoDB documents on the test server matched the independent run for all eight combinations in the table. Every technology matched on availability, parent, children and both coordinate pairs. Following a rules update the same tree ID received a new revision. Tests also covered clearing trees and tooltips and reading the rebuilt result a second time.

Of 54 local server tests, 51 passed. Three tests with separate environment requirements were skipped. Cases covered a cycle with a reachable reward, two distinct causes for the same event, positive and negative bioship checks and testing the existence of an optional owner. Anomaly spawn checks operate on the celestial body, and outcome selection operates on the survey ship. Counting systems in a storm preserves both the original system and each system being counted.

Two dialogue checks used the original option keys. The Advanced Afterburners page identifies the system offered as a gift. The Alien Topography page describes leaving the abducted scientist with their pre-FTL people. The system’s name and the scientist’s identity depend on the running campaign.

The browser opened each of the 679 technology pages in Russian and English, expanded reward sections and compared page contents with API responses and reward addresses in the previous snapshot. For Blue Lasers it also compared the card tooltip with the standalone page, including opening reward details by keyboard. Only the Zro extraction page referenced the last three additions to the dictionary. Both versions passed a second browser check with names for the starting deposit, the newly formed deposit and the astral scar. [Browser checks](../../../tests/frontend/conditionPages.mjs) · [Wording checks](../tests/audit_participant_text.py)

Counts are technologies containing the wording or condition in each row. One technology can contribute to several rows.

| Case | Before RU / EN | After RU / EN |
|---|---:|---:|
| “Current object being checked” | 125 / 125 | 0 / 0 |
| Generic relative role such as “Previous object being checked” | 611 / 611 | 0 / 0 |
| Quoted literal ROOT, FROM, PREV or THIS | 107 / 107 | 0 / 0 |
| Generic object leader existence check | 144 / 144 | 0 / 0 |
| Generic owner existence check | 282 / 282 | 0 / 0 |
| Unspecified empire applying the effect | 117 / 117 | 0 / 0 |
| Generic hidden-condition header | 166 / 166 | 0 / 0 |
| “Name/value from the current game” embedded in a phrase | 512 / 511 | 0 / 0 |
| Previous flag description listing setting actions | 638 / 638 | 0 / 0 |
| Participant existence and biological ship checks together | 106 / 106 | 46 / 46 |

The last row counts pairs of checks in the condition itself. These remain where the participant can be absent. Armor Hardening, for example, checks whether the fleet has an owning empire. The researching empire already exists when the game checks the Paradox Titan’s availability.

On 83 technology pages at least one participant varies by caller or is only partially defined by the script. Different routes to discovering Zro deposits, for example, pass different celestial bodies. For 526 flags appearing on 521 pages, an independent meaning has not been established. The text gives the supported actions and participants, and diagnostics retain the keys and script addresses. The counts agree in both languages.

The final pass found zero pages in either language with missing names, unnamed saved objects, empty groups, technical placeholders or unresolved localization markers. All 1,358 views retained their original reward and source addresses.

After updating the dictionary, the live API served all 1,358 views again. Every complete response matched its browser capture. All 679 MongoDB tooltip documents used the current source and rules revisions.
