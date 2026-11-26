# RB_LE — requirements for adding basic traits

## Contents

- [How to read the tables](#how-to-read-the-tables)
- [Rank progression](#rank-progression)
- [Level-up traits](#level-up-traits)
- [Recruitment pool traits](#recruitment-pool-traits)
- [Starting ruler only](#starting-ruler-only)
- [Species and ascension traits](#species-and-ascension-traits)
  - [Genetics and cloning](#genetics-and-cloning)
  - [Cybernetics](#cybernetics)
  - [Synthetics and virtuality](#synthetics-and-virtuality)
  - [Psionics](#psionics)
- [Origin traits](#origin-traits)
  - [Under One Rule](#under-one-rule)
  - [Fear of the Dark](#fear-of-the-dark)
  - [Golden Generation](#golden-generation)
  - [Clone Army](#clone-army)
  - [Storm Chasers](#storm-chasers)
  - [Scion](#scion)
  - [Hard Reset](#hard-reset)
  - [Cybernetic Creed](#cybernetic-creed)
  - [Synthetic Fertility](#synthetic-fertility)
  - [Shroud-Forged](#shroud-forged)
- [Empire and position traits](#empire-and-position-traits)
  - [Rulers and heirs](#rulers-and-heirs)
  - [Specialist subjects](#specialist-subjects)
  - [Cultural envoys](#cultural-envoys)
  - [Paladins](#paladins)
- [Event traits](#event-traits)
  - [The Shroud](#the-shroud)
  - [Anomalies and exploration](#anomalies-and-exploration)
  - [Astral rifts](#astral-rifts)
  - [Leviathans](#leviathans)
  - [Arkship adventures](#arkship-adventures)
  - [Other story chains](#other-story-chains)
- [Special leader traits](#special-leader-traits)
  - [Unique characters](#unique-characters)
  - [Enclaves and caravaneers](#enclaves-and-caravaneers)
  - [Crises and special factions](#crises-and-special-factions)
- [Direct opposites](#direct-opposites)
- [Special cases and sources](#special-cases-and-sources)

## How to read the tables

The Add Traits → Basic Traits branch in Stellaris 4.6.0 contains 254 game IDs in eight sections. Each row describes one button for the selected leader. Section totals count buttons before filtering.

A button is available when its class, leader, current owner and rank requirements are met. The leader must lack both the target ID and every trait in its direct `opposites` list. A plus sign joins mandatory conditions. A dash means that the column adds no filter. “All three” covers commanders, officials and scientists. Species checks use the leader’s own species. Individualist machines and machine intelligences are distinguished at the empire level.

Folder names identify the vanilla acquisition route. An active leader can receive a trait whose normal source is the recruitment pool, game setup or an event. The menu skips rolls, story progress and economic prerequisites. The table retains recipient checks for event variants. Dynamic names, descriptions and conditions that activate a bonus do not by themselves restrict the button.

Granting a trait, switching leaders or changing the selected leader’s ethic refreshes eligibility. A folder is visible only when at least one descendant action is available. Pagination follows filtering.

## Rank progression

The vanilla basic trait definitions contain 32 chains with 36 `replace_traits` transitions. Twenty-eight chains have two ranks and four have three. Every rank stays in the first rank’s folder.

1. With no rank in the chain, only rank I is eligible, subject to its other filters.
2. In the Rank column the arrow points to the exact ID the leader must currently hold. Granting the next rank replaces that ID. The menu prevents skipping ranks or adding a lower rank over a higher one.
3. At the highest rank the chain has no visible buttons. Class, leader and empire conditions come from the row for the rank being granted.

For Buccaneer, I → II → III stays under Starting ruler only. For Gifted, I → II stays under Recruitment pool traits. Once a leader holds I, the upgrade appears in that same folder even after recruitment.

An icon tier or a number in an ID does not establish a promotion. Altered Metabolism has a tier III icon and can be granted on its own. Azaryn’s nuclei count down from three to one. Hard Reset combat implants change with the situation. Those two families are marked as story states. Shroud illumination variants ending in 01 and 02 are independent outcomes.

## Level-up traits

93 IDs.

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Adaptable<br>`leader_trait_adaptable` [↔](#direct-opposites) | all three | — | — | — |
| Aggressive<br>`leader_trait_aggressive` [↔](#direct-opposites) | commander | — | — | — |
| Archaeologist<br>`leader_trait_archaeologist` | scientist | — | — | I · entry |
| Archaeologist II<br>`leader_trait_archaeologist_2` | scientist | — | — | II ← `leader_trait_archaeologist` |
| Architectural Interest<br>`leader_trait_architectural_interest` [↔](#direct-opposites) | official, scientist | — | no · crisis faction | — |
| Unifier<br>`leader_trait_bureaucrat` | all three | — | no · crisis faction | — |
| Butcher<br>`leader_trait_butcher` [↔](#direct-opposites) | commander | — | no · crisis faction | — |
| Energy Mogul<br>`leader_trait_capitalist` [↔](#direct-opposites) | all three | — | no · crisis faction + no · Wilderness | I · entry |
| Energy Mogul II<br>`leader_trait_capitalist_2` | all three | — | — | II ← `leader_trait_capitalist` |
| Carefree<br>`leader_trait_carefree` [↔](#direct-opposites) | scientist | — | — | I · entry |
| Carefree II<br>`leader_trait_carefree_2` [↔](#direct-opposites) | scientist | — | — | II ← `leader_trait_carefree` |
| Cautious<br>`leader_trait_cautious` [↔](#direct-opposites) | commander | — | — | — |
| Custom AI Assistant<br>`leader_trait_custom_AI_assistant` [↔](#direct-opposites) | scientist | — | — | — |
| Defense Engineer<br>`leader_trait_defence_engineer` | commander | — | no · nomadic empire | — |
| Engineer<br>`leader_trait_engineer` | commander, scientist | — | — | — |
| Enlister<br>`leader_trait_enlister` | commander | — | no · crisis faction | — |
| Entrepreneur<br>`leader_trait_entrepreneur` [↔](#direct-opposites) | all three | — | no · crisis faction | I · entry |
| Entrepreneur II<br>`leader_trait_entrepreneur_2` | all three | — | — | II ← `leader_trait_entrepreneur` |
| Environmental Engineer<br>`leader_trait_environmental_engineer` | all three | — | no · crisis faction + no · nomadic empire | — |
| Fleet Logistician<br>`leader_trait_fleet_logistician` | commander | — | — | — |
| Fleet Organizer<br>`leader_trait_fleet_organizer` [↔](#direct-opposites) | commander | — | — | I · entry |
| Fleet Organizer II<br>`leader_trait_fleet_organizer_2` [↔](#direct-opposites) | commander | — | — | II ← `leader_trait_fleet_organizer` |
| Homesteader<br>`leader_trait_homesteader` [↔](#direct-opposites) | all three | — | no · crisis faction + no · Wilderness | I · entry |
| Homesteader II<br>`leader_trait_homesteader_2` | all three | — | — | II ← `leader_trait_homesteader` |
| Authoritarian Ideologue<br>`leader_trait_ideologue_authoritarian` | official | Authoritarian | — | — |
| Egalitarian Ideologue<br>`leader_trait_ideologue_egalitarian` | official | Egalitarian | — | — |
| Materialist Ideologue<br>`leader_trait_ideologue_materialist` | official | Materialist | — | — |
| Militarist Ideologue<br>`leader_trait_ideologue_militarist` | official | Militarist | — | — |
| Pacifist Ideologue<br>`leader_trait_ideologue_pacifist` | official | Pacifist | — | — |
| Spiritualist Ideologue<br>`leader_trait_ideologue_spiritualist` | official | Spiritualist | — | — |
| Xenophile Ideologue<br>`leader_trait_ideologue_xenophile` | official | Xenophile | — | — |
| Xenophobe Ideologue<br>`leader_trait_ideologue_xenophobe` | official | Xenophobe | — | — |
| Iron Fist<br>`leader_trait_iron_fist` | commander | — | no · crisis faction + no · gestalt | I · entry |
| Iron Fist II<br>`leader_trait_iron_fist_2` | commander | — | — | II ← `leader_trait_iron_fist` |
| Meticulous<br>`leader_trait_meticulous` [↔](#direct-opposites) | scientist | — | — | I · entry |
| Meticulous II<br>`leader_trait_meticulous_2` [↔](#direct-opposites) | scientist | — | — | II ← `leader_trait_meticulous` |
| Planar Theorist<br>`leader_trait_planar_theorist` | scientist | — | — | I · entry |
| Planar Theorist II<br>`leader_trait_planar_theorist_2` | scientist | — | — | II ← `leader_trait_planar_theorist` |
| Politician<br>`leader_trait_politician` | all three | non-gestalt or a council member | — | — |
| Principled<br>`leader_trait_principled` | official | — | — | I · entry |
| Principled II<br>`leader_trait_principled_2` | official | — | — | II ← `leader_trait_principled` |
| Private Mines<br>`leader_trait_private_mines` [↔](#direct-opposites) | all three | — | no · crisis faction + no · Wilderness + no · nomadic empire | I · entry |
| Private Mines II<br>`leader_trait_private_mines_2` | all three | — | — | II ← `leader_trait_private_mines` |
| Resilient<br>`leader_trait_resilient` | all three | — | no · crisis faction | — |
| Careful<br>`leader_trait_restrained` [↔](#direct-opposites) | commander | — | no · crisis faction | — |
| Righteous<br>`leader_trait_righteous` [↔](#direct-opposites) | commander, official | — | no · crisis faction | I · entry |
| Righteous II<br>`leader_trait_righteous_2` [↔](#direct-opposites) | commander, official | — | — | II ← `leader_trait_righteous` |
| Roamer<br>`leader_trait_roamer` [↔](#direct-opposites) | commander, scientist | — | — | I · entry |
| Roamer II<br>`leader_trait_roamer_2` [↔](#direct-opposites) | commander, scientist | — | — | II ← `leader_trait_roamer` |
| Sapient AI Assistant<br>`leader_trait_sapient_AI_assistant` [↔](#direct-opposites) | scientist | — | — | — |
| Scrapper<br>`leader_trait_scrapper` [↔](#direct-opposites) | all three | — | no · crisis faction + no · Wilderness | I · entry |
| Scrapper II<br>`leader_trait_scrapper_2` | all three | — | — | II ← `leader_trait_scrapper` |
| Shipwright<br>`leader_trait_shipwright` [↔](#direct-opposites) | official | — | — | — |
| Skirmisher<br>`leader_trait_skirmisher` | commander | — | — | — |
| Spark of Genius<br>`leader_trait_spark_of_genius` [↔](#direct-opposites) | scientist | — | — | I · entry |
| Spark of Genius II<br>`leader_trait_spark_of_genius_2` [↔](#direct-opposites) | scientist | — | — | II ← `leader_trait_spark_of_genius` |
| Spycraft<br>`leader_trait_spycraft` | official | — | — | I · entry |
| Spycraft II<br>`leader_trait_spycraft_2` | official | — | — | II ← `leader_trait_spycraft` |
| Trade Focused<br>`leader_trait_trade_focus` [↔](#direct-opposites) | official | — | no · crisis faction + no · gestalt | I · entry |
| Trade Focused II<br>`leader_trait_trade_focus_2` [↔](#direct-opposites) | official | — | — | II ← `leader_trait_trade_focus` |
| Trickster<br>`leader_trait_trickster` [↔](#direct-opposites) | commander | — | — | — |
| Unyielding<br>`leader_trait_unyielding` [↔](#direct-opposites) | commander | — | — | — |
| Celebrity<br>`leader_trait_venerated` [↔](#direct-opposites) | all three | — | no · crisis faction | I · entry |
| Celebrity II<br>`leader_trait_venerated_2` | all three | — | — | II ← `leader_trait_venerated` |
| Void Hunter<br>`leader_trait_void_hunter` | commander | — | — | I · entry |
| Void Hunter II<br>`leader_trait_void_hunter_2` | commander | — | — | II ← `leader_trait_void_hunter` |
| Void Tracker<br>`leader_trait_void_tracker` | scientist | — | — | I · entry |
| Void Tracker II<br>`leader_trait_void_tracker_2` | scientist | — | — | II ← `leader_trait_void_tracker` |
| Whispering Mind<br>`leader_trait_whispering_mind` | all three | — | — | I · entry |
| Whispering Mind II<br>`leader_trait_whispering_mind_2` | all three | — | — | II ← `leader_trait_whispering_mind` |
| Whispering Mind III<br>`leader_trait_whispering_mind_3` | all three | — | — | III ← `leader_trait_whispering_mind_2` |
| Battleship Production Focus<br>`trait_ruler_battleship_focus` [↔](#direct-opposites) | commander | — | — | — |
| Champion of the People<br>`trait_ruler_champion_of_the_people` [↔](#direct-opposites) | all three | any personal ethic except gestalt | — | I · entry |
| Champion of the People II<br>`trait_ruler_champion_of_the_people_2` [↔](#direct-opposites) | all three | — | — | II ← `trait_ruler_champion_of_the_people` |
| Charismatic<br>`trait_ruler_charismatic` | all three | — | — | I · entry |
| Charismatic II<br>`trait_ruler_charismatic_2` | all three | — | — | II ← `trait_ruler_charismatic` |
| Corvette Production Focus<br>`trait_ruler_corvette_focus` [↔](#direct-opposites) | commander | — | — | — |
| Cruiser Production Focus<br>`trait_ruler_cruiser_focus` [↔](#direct-opposites) | commander | — | — | — |
| Destroyer Production Focus<br>`trait_ruler_destroyer_focus` [↔](#direct-opposites) | commander | — | — | — |
| Eye for Talent<br>`trait_ruler_eye_for_talent` | all three | — | — | I · entry |
| Eye for Talent II<br>`trait_ruler_eye_for_talent_2` | all three | — | — | II ← `trait_ruler_eye_for_talent` |
| Feedback Loop<br>`trait_ruler_feedback_loop` [↔](#direct-opposites) | all three | personal gestalt ethic | — | I · entry |
| Feedback Loop II<br>`trait_ruler_feedback_loop_2` [↔](#direct-opposites) | all three | — | — | II ← `trait_ruler_feedback_loop` |
| Fertility Preacher<br>`trait_ruler_fertility_preacher` | official | — | no · crisis faction + no · Wilderness | — |
| Frontier Spirit<br>`trait_ruler_frontier_spirit` | official | — | no · Wilderness | — |
| Home in the Sky<br>`trait_ruler_home_in_the_sky` | scientist | — | — | — |
| Mining Rush<br>`trait_ruler_industrialist` | official, scientist | — | — | I · entry |
| Mining Rush II<br>`trait_ruler_industrialist_2` | official, scientist | — | — | II ← `trait_ruler_industrialist` |
| Logistic Understanding<br>`trait_ruler_logistic_understanding` | all three | — | — | I · entry |
| Logistic Understanding II<br>`trait_ruler_logistic_understanding_2` | all three | — | — | II ← `trait_ruler_logistic_understanding` |
| Space Miner<br>`trait_ruler_space_miner` | scientist | — | — | — |
| Warlike<br>`trait_ruler_warlike` | commander | — | — | I · entry |
| Warlike II<br>`trait_ruler_warlike_2` | commander | — | — | II ← `trait_ruler_warlike` |

## Recruitment pool traits

7 IDs.

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Agrarian Upbringing<br>`leader_trait_agrarian_upbringing` | all three | — | no · crisis faction + no · Wilderness | — |
| Army Veteran<br>`leader_trait_army_veteran` [↔](#direct-opposites) | official, scientist | — | — | — |
| Eager<br>`leader_trait_eager` | all three | — | no · crisis faction | — |
| Emotional Support Pet<br>`leader_trait_emotional_support_pet` | all three | — | no · machine intelligence | — |
| Gifted / Upgraded<br>`leader_trait_gifted` | all three | — | no · crisis faction | I · entry |
| Gifted II / Upgraded II<br>`leader_trait_gifted_2` | all three | — | — | II ← `leader_trait_gifted` |
| Retired Fleet Officer<br>`leader_trait_retired_fleet_officer` [↔](#direct-opposites) | official, scientist | — | — | — |

## Starting ruler only

9 IDs.

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Buccaneer<br>`leader_trait_buccaneer` | all three | — | — | I · entry |
| Buccaneer II<br>`leader_trait_buccaneer_2` | all three | — | — | II ← `leader_trait_buccaneer` |
| Buccaneer III<br>`leader_trait_buccaneer_3` | all three | — | — | III ← `leader_trait_buccaneer_2` |
| Trailblazer<br>`leader_trait_trailblazer` | all three | — | — | I · entry |
| Trailblazer II<br>`leader_trait_trailblazer_2` | all three | — | — | II ← `leader_trait_trailblazer` |
| Trailblazer III<br>`leader_trait_trailblazer_3` | all three | — | — | III ← `leader_trait_trailblazer_2` |
| Treasure Hoarder<br>`leader_trait_treasure_hoarder` | all three | — | — | I · entry |
| Treasure Hoarder II<br>`leader_trait_treasure_hoarder_2` | all three | — | — | II ← `leader_trait_treasure_hoarder` |
| Treasure Hoarder III<br>`leader_trait_treasure_hoarder_3` | all three | — | — | III ← `leader_trait_treasure_hoarder_2` |

## Species and ascension traits

10 IDs.

### Genetics and cloning

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Erudite<br>`leader_trait_erudite` [↔](#direct-opposites) | all three | — | no · Wilderness | — |
| Backup Clone<br>`leader_trait_has_backup_clone` | all three | non-robotic species | — | — |
| Genetic Purist<br>`trait_leader_genetic_purist` | all three | non-robotic species | hive mind excluded | — |
| Second Chance<br>`trait_leader_second_chanced` | all three | non-robotic species | — | — |

### Cybernetics

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Cyborg<br>`leader_trait_cyborg` [↔](#direct-opposites) | all three | — | — | — |
| Neurological Firewall<br>`leader_trait_firewalled` | all three | cybernetic species or the Cyborg leader trait | — | — |
| Limited Cyborg<br>`leader_trait_limited_cyborg` [↔](#direct-opposites) | all three | personal Spiritualist ethic | — | — |

### Synthetics and virtuality

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Synthetic<br>`leader_trait_synthetic` [↔](#direct-opposites) | all three | — | — | — |
| Virtual Leader<br>`leader_trait_virtual` | all three | robotic species | — | — |

### Psionics

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Psychic<br>`leader_trait_psionic` [↔](#direct-opposites) | all three | — | — | — |

## Origin traits

42 IDs.

### Under One Rule

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Elitist<br>`leader_trait_legendary_bad_meritocracy` [↔](#direct-opposites) | all three | ruler | — | — |
| Paranoid Tyrant<br>`leader_trait_legendary_delusional` | all three | ruler | — | — |
| Absent-Minded<br>`leader_trait_legendary_dreamlike` [↔](#direct-opposites) | all three | ruler | — | — |
| Brutal<br>`leader_trait_legendary_harsh_ruler` [↔](#direct-opposites) | all three | ruler | — | — |
| Fearful<br>`leader_trait_legendary_hoplofobia` [↔](#direct-opposites) | all three | ruler | — | — |
| Luminary<br>`leader_trait_legendary_leader` | all three | ruler | — | — |
| Luminary Bloodline<br>`leader_trait_legendary_offspring` | all three | heir | — | — |
| Naive<br>`leader_trait_legendary_too_open` [↔](#direct-opposites) | all three | ruler | — | — |
| Blunt<br>`leader_trait_legendary_unfriendly` [↔](#direct-opposites) | all three | ruler | — | — |
| Warmonger<br>`leader_trait_legendary_warmonger` [↔](#direct-opposites) | all three | ruler | — | — |
| Apparatus Bound<br>`leader_trait_the_apparatus_luminary` | all three | ruler | — | — |
| Endless Upgrades<br>`leader_trait_the_cybernetic_luminary` | all three | ruler | — | — |
| Genetic Perfection<br>`leader_trait_the_genetic_luminary` | all three | ruler | — | — |
| The Passenger<br>`leader_trait_the_psionic_luminary` | all three | ruler | — | — |
| Synthetic Awareness<br>`leader_trait_the_synth_luminary` | all three | ruler | — | — |

### Fear of the Dark

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Cunning<br>`leader_trait_fotd_commander` | commander | — | — | — |
| Cunning<br>`leader_trait_fotd_scientist` | scientist | — | — | — |

### Golden Generation

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Defense Engineer<br>`leader_trait_defence_engineer_scientist` | scientist | — | no · nomadic empire | — |
| Elite Alumnus<br>`leader_trait_elite_alumnus` | all three | — | — | — |
| Fleet Organizer<br>`leader_trait_fleet_organizer_official` [↔](#direct-opposites) | official | — | — | — |
| Golden Cooperator<br>`leader_trait_golden_cooperator` | all three | — | — | — |
| Golden Exclusivist<br>`leader_trait_golden_exclusivist` | all three | — | — | — |
| Golden Generation<br>`leader_trait_golden_generation` | all three | — | — | — |
| Organ Transplant<br>`leader_trait_organ_transplant` | all three | — | — | — |
| Shipwright<br>`leader_trait_shipwright_scientist` [↔](#direct-opposites) | scientist | — | — | — |
| Spark of Genius<br>`leader_trait_spark_of_genius_other_classes` [↔](#direct-opposites) | commander, official | — | — | — |
| Spycraft<br>`leader_trait_spycraft_commander` | commander | — | — | — |
| Warlike<br>`trait_ruler_warlike_all_classes` | all three | — | — | — |

### Clone Army

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Clone Army Commander<br>`leader_trait_clone_army_commander` | commander | non-robotic species | — | — |
| Descendant Clone Army Commander<br>`leader_trait_clone_army_fertile_commander` | commander | non-robotic species | — | — |
| Ascendant Clone Army Commander<br>`leader_trait_clone_army_full_commander` | commander | non-robotic species | — | — |

### Storm Chasers

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Storm Rider<br>`leader_trait_storm_rider_commander` | commander | — | — | — |
| Storm Rider<br>`leader_trait_storm_rider_official` | official | — | — | — |
| Storm Rider<br>`leader_trait_storm_rider_scientist` | scientist | — | — | — |

### Scion

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Ancient Knowledge<br>`leader_trait_ancient_knowledge` | all three | — | — | — |

### Hard Reset

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Cyborg Soldier<br>`leader_trait_unplugged_cybernetic_positives_1` | commander | — | — | story state |
| Cyber Shock Troop<br>`leader_trait_unplugged_cybernetic_positives_2` | commander | — | — | story state |
| Cyber Commando<br>`leader_trait_unplugged_cybernetic_positives_3` | commander | — | — | story state |

### Cybernetic Creed

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Ritualistic Implants<br>`leader_trait_ritualistic_implants_cyborg` [↔](#direct-opposites) | all three | non-robotic species | — | — |

### Synthetic Fertility

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Robotic Surrogate<br>`leader_trait_robotic_surrogate` | all three | robotic species | — | — |

### Shroud-Forged

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Guided<br>`leader_trait_guided` | scientist | — | — | — |
| Shroud Prophet<br>`leader_trait_shroud_prophet` | official | robotic species | — | — |

## Empire and position traits

24 IDs.

### Rulers and heirs

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| ⟨Empire ruler title⟩<br>`leader_trait_ruler_hive_mind` | all three | ruler | hive mind | — |
| Machine Intelligence<br>`leader_trait_ruler_machine_intelligence` | all three | ruler | machine intelligence | — |
| Imperial Ruler / Imperial Heir / Imperial Bloodline<br>`trait_imperial_heir` | all three | — | — | — |

### Specialist subjects

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Bulwark Retaliator<br>`leader_trait_bulwark_retaliator` | commander | — | — | — |
| Bulwark Sentinel<br>`leader_trait_bulwark_sentinel` | commander | — | — | — |
| Bulwark Watcher<br>`leader_trait_bulwark_watcher` | commander | — | — | — |
| Prospectorium Extractor<br>`leader_trait_prospectorium_extractor` | official | — | — | — |
| Prospectorium Optimizer<br>`leader_trait_prospectorium_optimizer` | official | — | — | — |
| Prospectorium Refiner<br>`leader_trait_prospectorium_refiner` | official | — | — | — |
| Scholarium Explorer<br>`leader_trait_scholarium_explorer` | scientist | — | — | — |
| Scholarium Investigator<br>`leader_trait_scholarium_investigator` | scientist | — | — | — |
| Scholarium Observer<br>`leader_trait_scholarium_observer` | scientist | — | — | — |

### Cultural envoys

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Indoctrinator<br>`leader_trait_cultural_envoy_indoctrinator` | official | — | — | — |
| Negotiator<br>`leader_trait_cultural_envoy_negotiator` | official | — | — | — |
| Persuasive Luminary<br>`leader_trait_cultural_envoy_persuasive_luminary` | official | — | — | — |
| Zealot<br>`leader_trait_cultural_envoy_zealot` | official | — | — | — |

### Paladins

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Paladin<br>`leader_trait_paladin` | commander | — | — | — |
| Ace Pilot<br>`leader_trait_paladin_ace` | commander | — | — | — |
| Ranger<br>`leader_trait_paladin_ambusher` | commander | — | — | — |
| Defender<br>`leader_trait_paladin_defender` | commander | — | — | — |
| Knight<br>`leader_trait_paladin_knight` | commander | — | — | — |
| Architech<br>`leader_trait_paladin_logistician` | commander | — | — | — |
| Spearhead<br>`leader_trait_paladin_spearhead` | commander | — | — | — |
| Mastermind<br>`leader_trait_paladin_strategist` | commander | — | — | — |

## Event traits

43 IDs.

### The Shroud

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Shroud-Touched Naval Drone<br>`gestalt_trait_commander_mind_wipe_01` | commander | — | gestalt | — |
| Shroud-Touched Naval Drone<br>`gestalt_trait_commander_mind_wipe_02` | commander | — | gestalt | — |
| Shroud-Touched Assault Drone<br>`gestalt_trait_general_mind_wipe_01` | commander | — | gestalt | — |
| Shroud-Touched Assault Drone<br>`gestalt_trait_general_mind_wipe_02` | commander | — | gestalt | — |
| Shroud-Touched Command Drone<br>`gestalt_trait_ruler_mind_wipe_01` | all three | grant unconfirmed¹ | gestalt | — |
| Shroud-Touched Command Drone<br>`gestalt_trait_ruler_mind_wipe_02` | all three | grant unconfirmed¹ | gestalt | — |
| Shroud-Touched Research Drone<br>`gestalt_trait_scientist_mind_wipe_02` | scientist | — | gestalt | — |
| Shroud-Touched Commander<br>`leader_trait_admiral_mind_wipe_01` | commander | — | non-gestalt | — |
| Shroud-Touched Commander<br>`leader_trait_admiral_mind_wipe_02` | commander | — | non-gestalt | — |
| Chosen One / Chosen Vessel<br>`leader_trait_chosen` [↔](#direct-opposites) | all three | — | — | — |
| Chosen of the Composer<br>`leader_trait_composer_chosen` [↔](#direct-opposites) | all three | — | — | — |
| Chosen of the Cradle<br>`leader_trait_cradle_chosen` [↔](#direct-opposites) | all three | — | — | — |
| Chosen of the Eater<br>`leader_trait_eater_chosen` [↔](#direct-opposites) | all three | — | — | — |
| Shroud-Touched Commander<br>`leader_trait_general_mind_wipe_01` | commander | — | non-gestalt | — |
| Shroud-Touched Commander<br>`leader_trait_general_mind_wipe_02` | commander | — | non-gestalt | — |
| Chosen of the Instrument<br>`leader_trait_instrument_chosen` [↔](#direct-opposites) | all three | — | — | — |
| Shroud-Touched Architect<br>`leader_trait_ruler_mind_wipe_01` | commander, scientist | — | non-gestalt | — |
| Shroud-Touched Logistician<br>`leader_trait_ruler_mind_wipe_02` | commander, scientist | — | non-gestalt | — |
| Shroud-Touched Scientist<br>`leader_trait_scientist_mind_wipe_01` | scientist | — | non-gestalt | — |
| Shroud-Touched Scientist<br>`leader_trait_scientist_mind_wipe_02` | scientist | — | non-gestalt | — |
| Increased Lifespan<br>`leader_trait_shroud_age` | all three | — | — | — |
| Shroud-Warped<br>`leader_trait_shroud_warped` | all three | — | — | — |
| Shroudshaper<br>`leader_trait_shroudshaper` | all three | — | — | — |
| Chosen of the Whisperers<br>`leader_trait_whisperers_chosen` [↔](#direct-opposites) | all three | — | — | — |

### Anomalies and exploration

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Altered Metabolism<br>`leader_trait_altered_metabolism` | scientist | — | — | — |
| Brain Slug Host<br>`leader_trait_brainslug` | all three | — | — | — |
| Inspired Archaeologist<br>`leader_trait_inspired_archaeologist` | scientist | grant unconfirmed¹ | — | — |
| Inspired Researcher<br>`leader_trait_inspired_researcher` | scientist | grant unconfirmed¹ | — | — |
| Inspired Surveyor<br>`leader_trait_inspired_surveyor` | scientist | grant unconfirmed¹ | — | — |
| Intemporal<br>`leader_trait_intemporal` | all three | — | — | — |
| Percussive Maintainer<br>`leader_trait_percussive_maintainer` | scientist | — | — | — |
| Towel-bearer<br>`leader_trait_towel` | scientist | — | — | — |

### Astral rifts

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Rift Warped<br>`leader_trait_rift_warped` | all three | — | — | — |
| Sanitary Drone Assistant<br>`leader_trait_sanitary_drone` | scientist | — | — | — |

### Leviathans

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Dragonslayer<br>`leader_trait_dragonslayer` | commander | — | — | — |

### Arkship adventures

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Circuit Champion<br>`leader_trait_circuit_champion` | all three | — | — | — |
| Sable Pilot<br>`leader_trait_sable_pilot` | commander | — | — | — |

### Other story chains

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Caravan Counter<br>`leader_trait_caravan_counter` | commander | — | — | — |
| Foredoomed to a Rendezvous<br>`leader_trait_foredoomed_to_a_rendezvous` | commander | — | — | — |
| Intellectual<br>`leader_trait_intellectual` | official | — | — | — |
| Plague-Hardened Commander<br>`leader_trait_plague_hardened` | commander | — | — | — |
| Business Mind<br>`leader_trait_preftl_haggler` | official | — | — | — |
| Fervent Believer<br>`leader_trait_zealot` | official | — | — | — |

## Special leader traits

26 IDs.

### Unique characters

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| AI Assistant 'Gorky'<br>`leader_trait_gorky` | scientist | — | — | — |
| Nanite Entity<br>`leader_trait_governor_gray` | official | — | — | — |
| Oracle<br>`leader_trait_governor_oracle` | official | — | — | — |
| Psionic Communion<br>`leader_trait_governor_psionic_communion` [↔](#direct-opposites) | official | — | — | — |
| Ancestral Inheritance<br>`leader_trait_legendary_ancestors_knowledge` | all three | — | — | — |
| Nebulous Past<br>`leader_trait_legendary_far_from_home` | scientist | — | — | — |
| Terraformation Nucleus<br>`leader_trait_legendary_terraformation_nucleus_1_bud` | scientist | — | — | story state |
| Terraformation Nuclei<br>`leader_trait_legendary_terraformation_nucleus_2_buds` | scientist | — | — | story state |
| Terraformation Nuclei<br>`leader_trait_legendary_terraformation_nucleus_3_buds` | scientist | — | — | story state |

### Enclaves and caravaneers

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Curator<br>`leader_trait_curator` | scientist | — | — | — |
| Enclave Trader<br>`leader_trait_enclave_trader` | official | grant unconfirmed¹ | — | — |
| Master Salvager<br>`leader_trait_master_salvager` | scientist | — | — | — |
| Mercenary Warrior<br>`leader_trait_mercenary_warrior` | commander | — | — | — |
| Muutagan Liaison<br>`leader_trait_muutagan_liaison` | official | — | — | — |
| Merchant of Numa<br>`leader_trait_nuumismatic_priest` | official | — | — | — |
| Riggan Liaison<br>`leader_trait_riggan_liaison` | official | — | — | — |
| Shroudwalker Teacher<br>`leader_trait_shroudwalker` | official | — | — | — |
| Waste Management Specialist<br>`leader_trait_waste_management_specialist` | official | — | — | — |
| XuraCorp Liaison<br>`leader_trait_xuracorp_liaison` | official | — | — | — |

### Crises and special factions

| Trait and ID | Class | Leader | Empire | Rank |
|---|---|---|---|---|
| Cybrex Databases<br>`leader_trait_cybrex` | commander | robotic species | gestalt | — |
| Dimensional Stutter<br>`leader_trait_dimensional_stutter` | commander | — | crisis faction | — |
| Ethereal<br>`leader_trait_ethereal` | commander | — | crisis faction | — |
| Hive Affinity<br>`leader_trait_hive_affinity` | commander | — | crisis faction | — |
| The Great Khan<br>`leader_trait_ruler_great_khan` | all three | ruler | — | — |
| Sentinel Training<br>`leader_trait_sentinel` | commander | — | — | — |
| Void Hunter<br>`leader_trait_void_swimmer` | commander | — | crisis faction | — |

## Direct opposites

The button is hidden when the leader holds any ID listed in its row below. The check uses the direct `opposites` list of the target rank. Sixty-four buttons have entries and are marked ↔ above.

| Target ID | Direct opposites of this ID |
|---|---|
| `leader_trait_adaptable` | `leader_trait_stubborn`, `leader_trait_stubborn_2` |
| `leader_trait_aggressive` | `leader_trait_cautious` |
| `leader_trait_architectural_interest` | `leader_trait_procrastinator`, `leader_trait_procrastinator_2` |
| `leader_trait_army_veteran` | `leader_trait_retired_fleet_officer` |
| `leader_trait_butcher` | `leader_trait_armchair_commander`, `leader_trait_armchair_commander_2`, `leader_trait_restrained` |
| `leader_trait_capitalist` | `leader_trait_private_mines`, `leader_trait_private_mines_2`, `leader_trait_homesteader`, `leader_trait_homesteader_2`, `leader_trait_scrapper`, `leader_trait_scrapper_2`, `leader_trait_entrepreneur`, `leader_trait_entrepreneur_2`, `leader_trait_venerated`, `leader_trait_venerated_2` |
| `leader_trait_carefree` | `leader_trait_meticulous`, `leader_trait_meticulous_2`, `leader_trait_neurotic`, `leader_trait_neurotic_2` |
| `leader_trait_carefree_2` | `leader_trait_meticulous`, `leader_trait_meticulous_2`, `leader_trait_neurotic`, `leader_trait_neurotic_2` |
| `leader_trait_cautious` | `leader_trait_aggressive` |
| `leader_trait_chosen` | `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_synthetic` |
| `leader_trait_composer_chosen` | `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_synthetic` |
| `leader_trait_cradle_chosen` | `leader_trait_cyborg`, `leader_trait_synthetic` |
| `leader_trait_custom_AI_assistant` | `leader_trait_sapient_AI_assistant` |
| `leader_trait_cyborg` | `leader_trait_erudite`, `leader_trait_chosen`, `leader_trait_limited_cyborg`, `leader_trait_psionic`, `leader_trait_synthetic` |
| `leader_trait_eater_chosen` | `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_synthetic` |
| `leader_trait_entrepreneur` | `leader_trait_capitalist`, `leader_trait_capitalist_2`, `leader_trait_private_mines`, `leader_trait_private_mines_2`, `leader_trait_homesteader`, `leader_trait_homesteader_2`, `leader_trait_scrapper`, `leader_trait_scrapper_2`, `leader_trait_venerated`, `leader_trait_venerated_2` |
| `leader_trait_erudite` | `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_synthetic` |
| `leader_trait_fleet_organizer` | `leader_trait_nervous`, `leader_trait_nervous_2` |
| `leader_trait_fleet_organizer_2` | `leader_trait_nervous`, `leader_trait_nervous_2` |
| `leader_trait_fleet_organizer_official` | `leader_trait_nervous`, `leader_trait_nervous_2` |
| `leader_trait_governor_psionic_communion` | `leader_trait_cyborg`, `leader_trait_synthetic` |
| `leader_trait_homesteader` | `leader_trait_capitalist`, `leader_trait_capitalist_2`, `leader_trait_private_mines`, `leader_trait_private_mines_2`, `leader_trait_scrapper`, `leader_trait_scrapper_2`, `leader_trait_entrepreneur`, `leader_trait_entrepreneur_2`, `leader_trait_venerated`, `leader_trait_venerated_2` |
| `leader_trait_instrument_chosen` | `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_synthetic` |
| `leader_trait_legendary_bad_meritocracy` | `leader_trait_legendary_unfriendly`, `leader_trait_legendary_warmonger`, `leader_trait_legendary_dreamlike`, `leader_trait_legendary_harsh_ruler`, `leader_trait_legendary_too_open`, `leader_trait_legendary_hoplofobia` |
| `leader_trait_legendary_dreamlike` | `leader_trait_legendary_unfriendly`, `leader_trait_legendary_warmonger`, `leader_trait_legendary_harsh_ruler`, `leader_trait_legendary_too_open`, `leader_trait_legendary_hoplofobia`, `leader_trait_legendary_bad_meritocracy` |
| `leader_trait_legendary_harsh_ruler` | `leader_trait_legendary_unfriendly`, `leader_trait_legendary_warmonger`, `leader_trait_legendary_dreamlike`, `leader_trait_legendary_too_open`, `leader_trait_legendary_hoplofobia`, `leader_trait_legendary_bad_meritocracy` |
| `leader_trait_legendary_hoplofobia` | `leader_trait_legendary_unfriendly`, `leader_trait_legendary_warmonger`, `leader_trait_legendary_dreamlike`, `leader_trait_legendary_harsh_ruler`, `leader_trait_legendary_too_open`, `leader_trait_legendary_bad_meritocracy` |
| `leader_trait_legendary_too_open` | `leader_trait_legendary_unfriendly`, `leader_trait_legendary_warmonger`, `leader_trait_legendary_dreamlike`, `leader_trait_legendary_harsh_ruler`, `leader_trait_legendary_hoplofobia`, `leader_trait_legendary_bad_meritocracy` |
| `leader_trait_legendary_unfriendly` | `leader_trait_legendary_warmonger`, `leader_trait_legendary_dreamlike`, `leader_trait_legendary_harsh_ruler`, `leader_trait_legendary_too_open`, `leader_trait_legendary_hoplofobia`, `leader_trait_legendary_bad_meritocracy` |
| `leader_trait_legendary_warmonger` | `leader_trait_legendary_unfriendly`, `leader_trait_legendary_dreamlike`, `leader_trait_legendary_harsh_ruler`, `leader_trait_legendary_too_open`, `leader_trait_legendary_hoplofobia`, `leader_trait_legendary_bad_meritocracy` |
| `leader_trait_limited_cyborg` | `leader_trait_psionic`, `leader_trait_chosen` |
| `leader_trait_meticulous` | `leader_trait_carefree`, `leader_trait_carefree_2` |
| `leader_trait_meticulous_2` | `leader_trait_carefree`, `leader_trait_carefree_2` |
| `leader_trait_private_mines` | `leader_trait_capitalist`, `leader_trait_capitalist_2`, `leader_trait_homesteader`, `leader_trait_homesteader_2`, `leader_trait_scrapper`, `leader_trait_scrapper_2`, `leader_trait_entrepreneur`, `leader_trait_entrepreneur_2`, `leader_trait_venerated`, `leader_trait_venerated_2` |
| `leader_trait_psionic` | `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_synthetic` |
| `leader_trait_restrained` | `leader_trait_victory_or_death`, `leader_trait_victory_or_death_2`, `leader_trait_butcher` |
| `leader_trait_retired_fleet_officer` | `leader_trait_army_veteran` |
| `leader_trait_righteous` | `leader_trait_corrupt`, `leader_trait_corrupt_2` |
| `leader_trait_righteous_2` | `leader_trait_corrupt`, `leader_trait_corrupt_2` |
| `leader_trait_ritualistic_implants_cyborg` | `leader_trait_psionic`, `leader_trait_chosen` |
| `leader_trait_roamer` | `leader_trait_neurotic`, `leader_trait_neurotic_2` |
| `leader_trait_roamer_2` | `leader_trait_neurotic`, `leader_trait_neurotic_2` |
| `leader_trait_sapient_AI_assistant` | `leader_trait_custom_AI_assistant` |
| `leader_trait_scrapper` | `leader_trait_capitalist`, `leader_trait_capitalist_2`, `leader_trait_private_mines`, `leader_trait_private_mines_2`, `leader_trait_homesteader`, `leader_trait_homesteader_2`, `leader_trait_entrepreneur`, `leader_trait_entrepreneur_2`, `leader_trait_venerated`, `leader_trait_venerated_2` |
| `leader_trait_shipwright` | `leader_trait_irenic`, `leader_trait_irenic_2` |
| `leader_trait_shipwright_scientist` | `leader_trait_irenic`, `leader_trait_irenic_2` |
| `leader_trait_spark_of_genius` | `leader_trait_paranoid`, `leader_trait_paranoid_2` |
| `leader_trait_spark_of_genius_2` | `leader_trait_paranoid`, `leader_trait_paranoid_2` |
| `leader_trait_spark_of_genius_other_classes` | `leader_trait_paranoid`, `leader_trait_paranoid_2` |
| `leader_trait_synthetic` | `leader_trait_erudite`, `leader_trait_chosen`, `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_psionic` |
| `leader_trait_trade_focus` | `leader_trait_insider_trading`, `leader_trait_insider_trading_2` |
| `leader_trait_trade_focus_2` | `leader_trait_insider_trading`, `leader_trait_insider_trading_2` |
| `leader_trait_trickster` | `leader_trait_unyielding`, `leader_trait_reckless`, `leader_trait_reckless_2` |
| `leader_trait_unyielding` | `leader_trait_nervous`, `leader_trait_nervous_2`, `leader_trait_slipshod`, `leader_trait_slipshod_2`, `leader_trait_trickster` |
| `leader_trait_venerated` | `leader_trait_capitalist`, `leader_trait_capitalist_2`, `leader_trait_private_mines`, `leader_trait_private_mines_2`, `leader_trait_homesteader`, `leader_trait_homesteader_2`, `leader_trait_scrapper`, `leader_trait_scrapper_2`, `leader_trait_entrepreneur`, `leader_trait_entrepreneur_2` |
| `leader_trait_whisperers_chosen` | `leader_trait_cyborg`, `leader_trait_limited_cyborg`, `leader_trait_synthetic` |
| `trait_ruler_battleship_focus` | `trait_ruler_corvette_focus`, `trait_ruler_destroyer_focus`, `trait_ruler_cruiser_focus` |
| `trait_ruler_champion_of_the_people` | `leader_trait_tyrannical`, `leader_trait_tyrannical_2` |
| `trait_ruler_champion_of_the_people_2` | `leader_trait_tyrannical`, `leader_trait_tyrannical_2` |
| `trait_ruler_corvette_focus` | `trait_ruler_destroyer_focus`, `trait_ruler_cruiser_focus`, `trait_ruler_battleship_focus` |
| `trait_ruler_cruiser_focus` | `trait_ruler_corvette_focus`, `trait_ruler_destroyer_focus`, `trait_ruler_battleship_focus` |
| `trait_ruler_destroyer_focus` | `trait_ruler_corvette_focus`, `trait_ruler_cruiser_focus`, `trait_ruler_battleship_focus` |
| `trait_ruler_feedback_loop` | `leader_trait_tyrannical`, `leader_trait_tyrannical_2` |
| `trait_ruler_feedback_loop_2` | `leader_trait_tyrannical`, `leader_trait_tyrannical_2` |

## Special cases and sources

- Politician checks the leader’s personal ethic. A gestalt leader qualifies while serving on the council. The owner being a machine intelligence does not settle that check.
- `enclave.6010` selects the Shroud illumination variant by owner and class. Commanders and scientists can both receive the two individual variants with `ruler` in their IDs. Officials are absent from that grant. ¹ The two gestalt ruler variants appear only in the gestalt possession check. Their menu rows retain this empire filter and all three classes from their definitions. No direct vanilla grant was identified for the three Inspired traits or Enclave Trader either. All six entries use the classes from the trait definitions.
- The Eternal Chorus contract (`arkship.145`) can grant Erudite, so the editor does not require the species’ Erudite trait. `update_leader_after_modification` explicitly allows robotic psionics. Limited Cybernetics requires a personal Spiritualist ethic. `bio.765` checks for the Spare Organs species trait, whose allowed archetypes are Biological and Lithoid.
- For Brain Slug Host, `distar.173` filters newly generated leaders by species. `distar.172` can also grant the trait directly to the expedition leader. The late roll’s species gate is not universal. Sanitary Drone (`astral_rift.2675`) is granted to the expedition scientist without a gestalt check.
- The crisis folder covers several different factions. The extradimensional invaders and the Prethoryn are included in `is_crisis_faction`. The Cybrex are created as `cybrex_empire` with the gestalt ethic and a robotic species. A separate nomadic Great Khan grant targets the current ruler.

The source table identifies each rank, its definition, grant sites and vanilla acquisition conditions. File references and line numbers are relative to the Stellaris 4.6.0 installation. [Source table (Russian)](BASIC_LEADER_TRAITS_4_6_0_RU.csv) · [Leader research](VANILLA_LEADERS_4_6_0_EN.md#add-traits-menu-visibility)
