# Leader Editor — leaders in Stellaris 4.6.0

## Contents

- [Scope of the study](#scope-of-the-study)
- [Classes and assignments](#classes-and-assignments)
- [Editing an existing leader](#editing-an-existing-leader)
- [Editor scope and character background](#editor-scope-and-character-background)
- [Traits and progression](#traits-and-progression)
- [Opposites and acquisition requirements](#opposites-and-acquisition-requirements)
- [Add Traits menu visibility](#add-traits-menu-visibility)
- [Recruitment and lifecycle](#recruitment-and-lifecycle)
- [Council and special characters](#council-and-special-characters)
- [Selecting a leader in the UI](#selecting-a-leader-in-the-ui)
- [Open in-game checks](#open-in-game-checks)
- [Sources](#sources)

## Scope of the study

This study supports feature selection for the RB_LE cheat mod. The installed vanilla build is **Corona Borealis v4.6.0 (3d1a)**. Its files include DLC definitions. Actual availability depends on enabled content, the empire and the character.

The repository parser read 46 files in `common/traits`. Thirty contain **797 distinct leader trait IDs**, all declaring a `leader_class`. The count includes individual ranks, 12 subclasses and eight Ideologue variants generated from one template. Leader classes, leader tiers, council positions and lifecycle hooks were indexed separately. The search for script usage covered 2,351 files in `common` and `events`. Signatures and supported scopes were checked against the engine's script documentation. The study did not include in-game execution. [Inventory snapshot](../../TMP/RB_LE/vanilla_leaders_4_6_0.json)

## Classes and assignments

| Class | Vanilla assignments |
|---|---|
| Official (`official`) | Govern a colony, represent the empire in a federation or the Galactic Community, serve as an ideology advocate or crew a Cultural Envoy ship. |
| Commander (`commander`) | Command a military fleet or an army, or govern a colony. Admiral and General are commander subclasses. |
| Scientist (`scientist`) | Govern a colony or crew a science ship. Ship activities include surveying, anomalies, special projects, archaeology and astral rifts. |
| Envoy (`envoy`) | Perform diplomatic assignments. The class disables traits, standard recruitment, the normal leader pool and eligibility to rule. Countries can enumerate envoys through `every_envoy`. |

All three main classes can govern colonies. Ruler, heir and councilor describe a character's position. A scientist can therefore be both ruler and a member of a scientist subclass. An official assigned to a Cultural Envoy ship retains the `official` class. [Class and tier definitions](#sources)

Each main class has a base capacity of three leaders. Modifiers and resource calculations determine effective capacity, recruitment costs and upkeep. Ten is the ordinary **skill level cap of an individual character**. These are distinct values if the editor eventually exposes them.

## Editing an existing leader

| Property | Script access in 4.6.0 | Design implications |
|---|---|---|
| Skill and experience | `set_skill`, `add_skill`, `add_experience`, `add_skill_without_trait_selection`. Queries include `has_base_skill`, `has_total_skill`, `has_experience` and `get_leader_exp_to_level`. | Base level and effective level with bonuses can differ. The reference search found no direct setter for an arbitrary absolute XP total. |
| Traits | `has_trait`, `add_trait`, `add_timed_trait`, `remove_trait`, `num_leader_traits`, plus bulk removal effects. | Trait rank, subclass and an unspent trait selection are separate. See the next section. |
| Age, mortality and service | `leader_age`, `leader_lifespan`, `set_age`, `add_age`, `freeze_leader_age`, `is_immortal`, `set_immortal`, `leader_years_of_service`. | Age freeze and immortality have separate controls. Removing scripted immortality preserves species-granted immortality. `set_years_served` copies the duration from another leader. |
| Name, gender, portrait and species | `set_name`, `set_gender`, `change_leader_portrait`, `change_species`. The portrait effect accepts a portrait key or a species target. | A script can set a name. Free text entry in a custom menu needs UI verification. Editing species changes more of the character than editing their portrait. |
| Background | `change_background_job`, `change_background_ethic`, `set_custom_description`. There are links to a background planet or colony. | A custom biography takes a localisation key. Vanilla sets birthplaces, catchphrases and hidden age at creation. General setters for all of these on a living character were not established. |
| Class and leader tier | `change_leader_class`, `set_leader_tier`. The `default`, `renowned` and `legendary` tier definitions control frame presentation. | Vanilla separately applies class-specific starting skill and then traits when it chooses an heir's class. Changing tier alone does not reproduce a legendary character's story. |
| Ownership, assignment and council | `set_owner`, `assign_leader`, `unassign_leader`, `set_council_position`, `remove_from_empire_council`. Manual assignment and council eligibility also have setters. | `assign_leader` runs on the **destination** and takes a leader target. `set_council_position` runs on the leader. Leaving an assignment, dismissal and death have different event chains. |

## Editor scope and character background

**RB_LE decisions.** The character keeps their class. Granting traits and changing the selected leader's personal ethic are required. Planned changes include editing former profession and age. Awarding XP with `add_experience` is the preferred progression option. Replacing an existing subclass remains open. Gender and portrait editing need separate in-game verification. For roleplay, the desired biography feature is free text entry during a campaign.

| Player-facing property | Evidence from vanilla 4.6.0 |
|---|---|
| Former profession | `change_background_job` changes the character's previous job. Vanilla can pick from captain, navigator and other professions. This field is separate from the current assignment. See `common/scripted_effects/paragon_effects.txt`, line 2832. |
| Personal ethic | `change_background_ethic` sets the character's ethic. An official's ethic contributes to eligibility for the corresponding Ideologue trait. The effect that creates such an ideologue explicitly changes the ethic and grants the trait with a separate command. See `common/inline_scripts/forceofwill/leader_trait_ideologue.txt` and `common/scripted_effects/forceofwill_scripted_effects.txt`, line 2734. |
| Biography and homeworld | `set_custom_description` takes a localisation key. Vanilla assigns a homeworld at creation, for example in `events/forceofwill_events.txt`, line 1420. The engine reference search found no dedicated effect to change the birthplace of a living leader. |
| Age | Vanilla can set age and add or subtract years. In `events/astral_rifts_1_events.txt`, line 747, an active leader becomes five years younger. Age affects mortality risk and specific event conditions. In `events/envoy_events.txt`, lines 350 and 511, vanilla checks the age of a Galactic Community representative. |
| Gender | Vanilla uses `set_gender`. Human leader portrait variants are filtered by gender. Event `distar.192` selects its description according to the scientist's gender. Immediate appearance and name updates after manually changing a recruited leader's gender have not been tested in-game. See `gfx/portraits/portraits/07_portraits_human.txt`, line 477, and `events/distant_stars_events_1.txt`, line 6047. |
| Portrait | `change_leader_portrait` updates the same character's image. Each time Azaryn spends a Terraforming Nucleus, the event applies the portrait showing the new bud count. The current trait selects the event branch. A manually selected portrait could misrepresent the current stage and will be replaced on the next such transition. See `events/paragon_events.txt`, lines 2108–2129. |

**Writing a biography during a campaign.** The empire designer's ruler editor includes `leader_bio_edit_box`, a multiline input capped at 1,000 characters (`interface/customize_species_editors.gui`, lines 2169–2177). The native character card declares `leader_background_text` as a display field (`interface/paragon_ui_types.gui`, line 2376). For an existing leader the engine documents `set_custom_description = <loc_key>`. The academy graduation event uses it to assign a description that inserts the character's name (`events/origin_events_forceofwill.txt`, line 3528, and `localisation/english/forceofwill_l_english.yml`, line 3683).

The inspected interfaces and script reference expose no confirmed handler for passing arbitrary player input from a custom field into the selected serving leader's biography. This remains a candidate for a prototype. The acceptance check would enter different biographies for two leaders, including Cyrillic and line breaks, reopen both cards, then verify both texts after reloading the save. Authored text with substitutions is already supported by the vanilla effect. Including templates in RB_LE remains a separate design decision.

## Traits and progression

The 797 IDs in 4.6.0 fall into five `leader_trait_type` groups. There are 254 basic, 355 veteran and 85 destiny IDs, plus 91 negative traits and 12 subclasses. All 254 basic entries use the default type. Each rank with its own ID counts separately. A trait's type alone does not establish eligibility for an ordinary level-up choice.

Type, rank and display rarity can be checked separately. Ranks I and II of an admiral's artillery specialization both have type `veteran`. Tactical Algorithms has type `destiny`, display rarity `RARITY = veteran` and `TIER = none`. See `common/traits/00_admiral_traits.txt` (712, 750, 2147) and `common/traits/000_documentation_leader_traits.txt` (29).

The second and third ranks of `leader_trait_adventurous_spirit` each have an explicit `replace_traits` link to the preceding rank. These links can be read from the individual definitions. Whether removing a higher rank alone restores its predecessor still needs an in-game test.

The table gives the exact ID suffixes after `subclass_<class>_` for the three main classes.

| Class | Four subclasses |
|---|---|
| `commander` | `admiral`, `general`, `governor`, `councilor` |
| `official` | `delegate`, `governor`, `diplomacy_councilor`, `economy_councilor` |
| `scientist` | `explorer`, `scholar`, `governor`, `councilor` |

The default subclass choice is at level **4** and the destiny choice at **8**. Actual offers depend on the enabled DLC and character conditions. Relevant filters include class, species traits, government, technology, conflicting traits, `leader_potential_add` and selection weight. An editor can treat natural eligibility, acquisition effects and the post where a bonus applies as separate questions. A leader can possess a council, governor or fleet trait while serving in a different post.

**Acquisition example.** `leader_trait_army_veteran` is defined for officials and scientists. Natural acquisition checks that the character is in the recruitment pool. Its acquisition handler adds 10% of the calculated lifespan to the leader's age and assigns a commander-related background. The definition supplies no removal handler to restore the previous values. Adding and removing this trait can therefore have different consequences.

With `add_trait`, `consume_selection` controls spending an available selection and defaults to off. `show_message` controls the notification. `num_trait_points` counts points spent. Giving a known trait, raising the character's skill and offering the normal choice of traits are three different potential editor features.

## Opposites and acquisition requirements

The audit covered 797 IDs in 46 files under `common/traits` in build 4.6.0 (3d1a). The repository parser expanded inline templates and nested scripted triggers. Each ranked trait ID counts separately. The scope is acquisition rules in trait definitions. Story events that grant a trait directly may have their own triggers. [Audit results](../../TMP/RB_LE/trait_requirements_4_6_0.json)

| Conflict declaration | Maximum per trait | Example |
|---|---:|---|
| Other IDs in the trait's own `opposites` | 10 | `leader_trait_capitalist` lists both ranks of `private_mines`, `homesteader`, `scrapper`, `entrepreneur` and `venerated`. The first rank of each of those five traits also reaches this maximum. |
| Other traits that list the given ID | 10 | `leader_trait_cyborg` and `leader_trait_synthetic`. |
| Distinct neighbors when both directions are combined | 11 | Cyborg and Synthetic again. Each declares five IDs in its own list. |

132 traits declare a nonempty list. In 74 pairs only one side names the other. For example, Cyborg lists `leader_trait_limited_cyborg`, while the latter lists only `leader_trait_psionic` and `leader_trait_chosen`. The figure of 11 describes the combined data. The effect of one-sided declarations on a direct `add_trait` call has not been tested in-game. Additional exclusions can appear in `leader_potential_add`.

**The literal `prerequisites` field** occurs on 18 traits and references 12 distinct technologies. The research areas are physics (4 technologies), society (3) and engineering (5). Their categories are `computing`, `field_manipulation`, `biology`, `archaeostudies`, `voidcraft` and `propulsion`. Six other traits check technology through `has_technology` in acquisition conditions. A technology in an alternative branch may be one of several ways to qualify.

| What natural selection checks | Examples in the data |
|---|---|
| Character and progression | Class, subclass, presence or absence of another trait, base skill, personal ethic, immortality and character flags. Each of the eight Ideologue variants checks its official's matching ethic. |
| Character role | Ruler, heir, council member or recruitment candidate. A role check may be combined with empire conditions. |
| Species | Archetype, robotic nature, psionic and other traits. Scripts distinguish the leader's species from the empire's founding species. |
| Empire and progression | Country type, authority, Gestalt status, nomadic status, origin, civics, empire ethics, ideology, policies, technologies, traditions, ascension perks and crisis progression. |
| Colonies, economy and fleet | Owned planet classes, active buildings, starbase type, use of bioships or expenditure of a particular resource. |
| Galaxy and game state | Galactic Community membership, communications with space fauna, archaeological sites and their completion, game start and country event flags. |
| DLC and acquisition route | Host DLC. Separate fields and progression rules cover starting ruler creation, random acquisition, subclass selection and destiny choices. |

All 797 traits specify `leader_class`. 310 specify `leader_potential_add`. Ruler creation fields include `allowed_ethics` (30), `forbidden_ethics` (1), `allowed_origins` (27) and `forbidden_origins` (10). The documented fields `requires_traits` and `requires_governments` have no entries in this population. Scripted conditions perform comparable checks. `leader_trait_nuumismatic_priest` separately specifies the species-side field `species_potential_add = { always = no }`.

**Combined example.** The first rank of `leader_trait_carrier_specialization` requires the commander class, the admiral subclass, Galactic Paragons, no existing combat specialty, `tech_strike_craft_1` and either `tech_cruisers` or `tech_harbingers`. The exclusivity check is in `has_any_admiral_speciality`. This trait has no `opposites` list of its own. See `common/traits/00_admiral_traits.txt` (777–803) and `common/scripted_triggers/03_scripted_triggers_paragon.txt` (66).

Three related fields matter for design. `replace_traits` (299 traits) describes what a grant replaces, including the preceding rank. `selectable_weight` (307) controls the chance of being offered and a zero weight can exclude a choice. A condition in `triggered_*_modifier` governs when a particular bonus applies to a character who has the trait.

## Add Traits menu visibility

The editor uses a dynamic menu following PDE's visibility rules. When a screen opens or refreshes, the editor determines which actions are available for the selected leader and their current empire. Selecting another leader or changing the leader's personal ethic refreshes the list. All ranks of a trait share one folder. Visibility is evaluated for each rank individually. [Basic trait table](BASIC_LEADER_TRAITS_4_6_0_RU.csv)

| Scope | Conditions used for button visibility |
|---|---|
| Owning empire | Crisis faction, Wilderness, machine intelligence, nomadic empire and gestalt consciousness. |
| Selected leader | Class, personal ethic, gestalt status and robotic or non-robotic species. A leader-level Wilderness or machine intelligence restriction applies when a check tests the character or their species directly. Owner conditions are evaluated on the empire. |
| Special cases | Preserve recipient restrictions from trait-granting events and the logic of compound conditions. For example, the Shroud-illumination drone variants require a gestalt empire. A gestalt leader qualifies for Politician when serving on the council. |

Game start, recruitment pool membership, level thresholds for random selection, roll weight, event completion, technologies, traditions and buildings belong in the description of the vanilla acquisition method. A button can be visible before the associated event occurs. Conditions that only change a trait's name or bonus also have no effect on visibility.

A folder is visible if any descendant at any depth offers an available add action. This applies up to the Add Traits entry. An empty branch disappears in full. Pagination follows filtering and preserves the order of the entries. Each visible subfolder takes one slot on its parent's page. A page navigation button appears only when the adjacent page exists. [PDE visibility rules](../../docs/PDE/REQUIREMENTS_EN.md)

Each of the 254 basic trait buttons has its own eligibility entry. In a chain only the next rank is eligible. Granting it replaces the previous rank. After the highest rank is granted, the chain disappears from the Add Traits menu. The leader must also lack every direct opposite of the target rank for its button to appear. [Requirements by trait and rank](BASIC_TRAIT_MENU_REQUIREMENTS_4_6_0_EN.md)

## Recruitment and lifecycle

A country can iterate over its employed leaders (`every_owned_leader`), recruitment candidates (`every_pool_leader`) and envoys (`every_envoy`). All three have ordered iterators. The `num_owned_leaders` count includes the ruler and excludes envoys. Base pool settings are three candidates, one external candidate and a 1,800-day refresh interval. `refresh_leader_pool` refreshes the country's entire pool.

A country can create a leader (`create_leader`), prepare and activate a saved candidate (`create_saved_leader`, `activate_saved_leader`), or create a clone. The engine also distinguishes training, exile, return, dismissal and death. `last_created_leader` points to the most recently created leader in the game. The nested `effect` inside `create_leader` already scopes to the specific new character. A Biogenesis cloning script explicitly transfers service duration and handles assignment. Direct setters are available for changing a living character's name or age.

| Transition | Scope used by vanilla | Examples of affected systems |
|---|---|---|
| Spawn, entry into the pool | Country, with the leader in `FROM` | Ascension traits, extra government traits, variation in age and starting skill. |
| Hire | Leader | Notifications and hire-related events. |
| Level up | Country, with the leader in `FROM` | Gestalt node portrait updates and DLC event checks. |
| Assignment and unassignment | Leader | Post checks and handlers associated with portraits and ships. |
| Dismissal, death | Country, with the leader in `FROM` | Separate handlers, including special characters and Ark-related events. |

## Council and special characters

The council files contain **189 potential seat definitions**. The seats actually available depend on the empire and its conditions. Current occupancy, permission to join the council and the character's position as ruler or heir all matter. Appointing a leader to an existing seat, creating a seat on the council, setting an heir and replacing the ruler are separate actions.

Vanilla identifies four Gestalt council nodes (`growth`, `cognitive`, `legion`, `regulatory`) and separately identifies the ruler. The relevant checks are `is_gestalt_node` and `is_gestalt_ruler`. An ordinary commander or scientist employed by a Gestalt empire does not automatically become a node.

The Beholder (`NAME_The_Beholder`) is created with the commander class, legendary tier, level 10, immortality, specific traits and biography, and restrictions on manual and council assignments. The event also saves a global reference, sets flags and puts the character in exile pending further action. Editing this particular leader in place can preserve the object referenced by the quest. Removing their restrictions or creating a copy has separate implications.

## Selecting a leader in the UI

A script can reach a specific character from a known object. A country has `ruler` and `heir` links. A fleet or army can reach its assigned commander through `leader`, and an archaeological site can reach its assigned scientist the same way. This supports actions on a character in a known post. Countries also have a dedicated `every_leader_in_training` iterator.

Vanilla provides a leader list, recruitment pool, character card, selection and assignment widgets, the council and leader-specific event windows. The list includes native assign and dismiss buttons. The country effect `open_leader_tab` opens the leaders tab. The inspected GUI and `button_effects` examples do not establish that a newly inserted button on a leader card would receive that particular character as its script target.

In the 0.0.1 in-game test, the UI Overhaul Dynamic card button received the Commonwealth of Man country. In 0.0.2 the player opens the Personnel Department from an owned colony and selects the character by name. Registers cover the entire empire. [Specification for 0.0.1](REQUIREMENTS_0_0_1_EN.md) · [Specification for 0.0.2](REQUIREMENTS_0_0_2_EN.md)

## Open in-game checks

- For class changes, compare an idle and an assigned leader. Observe the old subclass, an incompatible trait, fleet command and council membership.
- For skill editing, compare normal advancement, direct level setting and demotion with partial XP and a pending trait selection. Record XP, remaining selections and fired events.
- For trait editing, test granting and removing a rank, an incompatible pair and a trait with an acquisition handler. Compare with and without Galactic Paragons wherever the mechanic is available.
- Test an unassigned serving leader, a recruitment candidate, the ruler under their class and returning to page two of the personnel register.
- If special characters are included, test a ruler, an heir, a Gestalt node and a story leader with restricted assignments separately.

## Sources

Paths below are relative to the installation at `E:\SteamLibrary\steamapps\common\Stellaris\`. Line references apply to the build named above.

| Subject | Vanilla source |
|---|---|
| Build, classes and tiers | `launcher-settings.json`, `common/leader_classes/00_base_classes.txt` (5, 116, 220, 303), `common/leader_tiers/00_default.txt` |
| Recruitment, skill and trait choices | `common/defines/00_defines.txt` (820–838), `common/scripted_triggers/03_scripted_triggers_paragon.txt`, `events/paragon_events_2.txt`, `common/traits/00_scientist_traits.txt` |
| Trait format, ranks, restrictions and effects | `common/traits/000_documentation_leader_traits.txt`, `common/traits/00_generic_leader_traits.txt`, `common/traits/00_governor_traits.txt` (101–132), `common/traits/20_leader_subclasses.txt` |
| Parameterised traits | `common/traits/19_forceofwill_leader_traits.txt`, `common/inline_scripts/forceofwill/leader_trait_ideologue.txt` |
| Heir class, council positions and nodes | `events/leader_events_2.txt` (around 706), `common/governments/councilors/`, `common/scripted_triggers/00_scripted_triggers.txt` (4692), `common/scripted_effects/paragon_effects.txt` |
| Lifecycle, story characters and cloning | `common/on_actions/00_on_actions.txt` (2446–2554, 4136–4159), `events/paragon_events.txt` (561), `common/scripted_effects/biogenesis_effects.txt` |
| Native interface | `interface/topbar_leaders_view.gui`, `interface/leader_view.gui`, `interface/leader_pool_view.gui`, `interface/select_leader_widget_view.gui`, `interface/assign_leader_widget_view.gui`, `interface/council_view.gui`, `common/button_effects/example.txt` |

The local engine reference lives under `Documents/Paradox Interactive/Stellaris/logs/script_documentation/`. The files `effects.log`, `triggers.log` and `scopes.log` describe signatures and scopes. The JSON includes selected reference entries, original definition locations and command occurrences. Individual trait definitions remain the source for nested eligibility and selection weights. [Inventory snapshot](../../TMP/RB_LE/vanilla_leaders_4_6_0.json)
