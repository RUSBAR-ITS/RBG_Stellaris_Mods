# RB_LE — affected files and functions

## Contents

- [Decision and events](#decision-and-events)
- [Target and navigation](#target-and-navigation)
- [Leader details](#leader-details)
- [Editing a leader](#editing-a-leader)

## Decision and events

Version 0.0.2 adds the Personnel Department planetary decision. It checks colony ownership and opens an event for the player’s empire. Every screen uses the vanilla `GFX_evt_galactic_senate` illustration from `interface/eventpictures.gfx`. The decision uses the `decision_politics` icon. The menu runs on Stellaris `v4.6.*` events and ships with RB_LE. [Decision](../../RB_LE/mod/common/decisions/rb_le_personnel.txt) · [Events](../../RB_LE/mod/events/rb_le_dossier_events.txt)

## Target and navigation

Since 0.0.16 the registers and occupation catalogue share a paging template using vanilla `check_variable`, `set_variable`, `change_variable` and `country_event`. The menu uses `BACK` in both languages, `QUIT` for «Выход» in Russian and `EXIT` for Exit in English. These keys come from `main_1`. RB_LE supplies the full Russian paging labels. [Paging template](../../RB_LE/mod/common/inline_scripts/rb_le/page_navigation.txt)

The `ruler` scope identifies the current ruler. The register visits other serving leaders with `every_owned_leader` and filters them by `leader_class`. During page preparation, `save_event_target_as` binds each button to a leader object. The button displays that character’s `GetName` and opens the same character’s dossier. Exit clears the temporary variables and the open-register flag. [Page preparation](../../RB_LE/mod/common/scripted_effects/rb_le_register.txt) · [Requirements and acceptance](REQUIREMENTS_0_0_2_EN.md)

## Leader details

As of 0.0.8, Personal details uses `diplomatic = yes` and passes the saved leader object to `picture_event_data.portrait`. Vanilla event `distar.158` in `events/distant_stars_events_1.txt` uses this pattern with the `ethic_spaceship_room` background. [Personal details screen](../../RB_LE/mod/events/rb_le_editor_events.txt)

The gender line in 0.0.6 uses the leader trigger `gender` and the `GENDER`, `male`, `female`, and `indeterminable` keys from the `main_3` localization. Vanilla explicitly assigns `indeterminable` to the leader `NAME_Mercedes` in `events/astral_planes_events.txt`.

Since 0.0.5 the event calls conditional fields on the character, for example `[rb_le_selected_leader.rb_le_job_line]`. Both the `has_background_job` check and the `[GetBackgroundJob]` substitution receive that leader. Vanilla similarly calls `[Actor.GetInviteIdeologyExtra]` and reads `[GetName]` in the selected string. For an ark, the event's conditional string uses the saved target name `[rb_le_home_colony.GetName]`, following `[replacement_leader.GetSubclass]`. Both examples are in `localisation/english/forceofwill_l_english.yml` and `common/scripted_loc/16_scripted_loc_forceofwill.txt`.

In 0.0.4 the dossier reads `GetAge`, `GetYearsOfService`, `Species.GetName`, `Species.GetClass`, `GetBackgroundEthic`, `GetBackgroundPlanet`, `GetHomeWorldBiome`, `GetBackgroundJob`, `GetClass`, and `GetSubclass`. A mobile home colony supplies its name through the `background_colony` scope. The `has_background_job` trigger, the `is_subclass` filter of `num_leader_traits`, and vanilla personal ethic checks control optional lines. Species type uses `is_robotic` and the `BIOLOGICAL` and `LITHOID` archetypes. Other non-robotic species display “Non-robotic”. [Display conditions](../../RB_LE/mod/common/scripted_loc/rb_le_dossier.txt)

The selected leader supplies `has_base_skill`, `has_total_skill`, and `has_experience`. The XP threshold uses `get_leader_exp_to_level` following `common/script_values/09_script_values_forceofwill.txt`. Stellaris 4.6.0 sets the base cap to 10 with `NGameplay.LEADER_BASE_SKILL_CAP` and `LEADER_MAX_SKILL_CAP` in `common/defines/00_defines.txt`. Exiting the department clears the open register’s variables. [Dossier data](../../RB_LE/mod/common/scripted_effects/rb_le_dossier.txt) · [XP threshold](../../RB_LE/mod/common/script_values/rb_le_dossier.txt)

## Editing a leader

In 0.0.19 the generator checks the vanilla building requirement `has_branch_office = yes` before reading `branch_office_owner` in a branch office building's job grants. For example, `building_private_security` in `common/buildings/14_branch_office_buildings.txt` checks for an office in `potential` and checks the owner's type in `triggered_planet_modifier`. [Catalogue generator](../../Instruments/RB_LE_Background_Jobs/build.py)

Builds 0.0.18 and 0.0.19 used the vanilla `log_error` effect to trace the former occupation catalogue. Version 0.1.0 removes those calls. [Occupation list preparation](../../RB_LE/mod/common/scripted_effects/rb_le_occupation_page.txt)

Version 0.0.15 reads former occupations with `has_background_job` and calls `change_background_job` on the selected leader. Choices use the vanilla `job_<ID>` localization keys. The leader's personal ethic is checked with `has_ethic = ethic_gestalt_consciousness`. [Background events](../../RB_LE/mod/events/rb_le_background_events.txt)

The economic routes use `any_owned_colony` to include inhabited arks. Existing capacity comes from `num_assigned_jobs` and `free_jobs_of_type`. The editor tests `can_work_specific_job` on a pop group on the same colony. Prospective construction uses vanilla buildings, districts, zones, holdings and starbase components. Each registry row identifies the source file and grant branch. [Stellaris 4.6.0 source registry](BACKGROUND_JOB_VISIBILITY_SOURCES_4_6_0_EN.csv)

Version 0.0.14 runs `set_gender` on the selected leader, as vanilla does in `events/distant_stars_events_2.txt`. The menu reads back the leader's `gender` and uses the existing localization keys `GENDER`, `male`, `female` and `indeterminable`. The modern human group in `gfx/portraits/portraits/07_portraits_human.txt` lists five female and five male phenotypes for leaders and rulers. Both lists include the indeterminate gender. [Gender command](../../RB_LE/mod/common/inline_scripts/rb_le/gender_option.txt)

Version 0.0.13 uses single-texture attachment and clothing selectors following the default-only selector in vanilla `gfx/portraits/asset_selectors/aquatic_clothes_01.txt`. Preview and leader assignment share the same complete portrait definition. The native `species_portrait` readback now distinguishes changes to a single layer. [Catalogue generator](../../Instruments/RB_LE_Portraits/build.py)

Since 0.0.12 the editor uses `change_leader_portrait = <portrait key>` in the selected leader's scope, following Azaryn's appearance changes in `events/paragon_events.txt`. To verify the write, the editor clears the sample species portrait, copies the leader's appearance back through `change_species_characteristics`, and compares the resulting key with the preview. [Application and verification](../../RB_LE/mod/common/scripted_effects/rb_le_portrait.txt)

Stellaris 4.6.0 limits nested scripted-effect initialization to five passes. Vanilla accounts for this in `common/scripted_effects/shroud_shadows_scripted_effects.txt`. In 0.0.11 the buttons pass control to one hidden `country_event` (`rb_le.27`), which reads the catalogue and applies the preview. [Preview event](../../RB_LE/mod/events/rb_le_portrait_events.txt)

Version 0.0.10 reads the selected character’s appearance through a separate sample species following `clones.1` in `events/clone_army_events.txt`. The event displays that species through `picture_event_data.portrait`, as in `origin.4015` in `events/origin_events_4.txt`. Accept passes the species reference to `change_leader_portrait` following `events/origin_events_machine_age.txt`. The selected leader retains the clothing and attachment indices. The event requests `refresh_portraits = character`. [Preview session](../../RB_LE/mod/common/scripted_effects/rb_le_portrait.txt)

The generator reads `common/portrait_categories`, `common/portrait_sets`, `gfx/portraits/portraits` and `gfx/portraits/asset_selectors`. Definitions under the `rb_le_` prefix reference vanilla models and textures. The original random selection rules continue to apply to other leaders. [Sources and catalogue generation](../../Instruments/RB_LE_Portraits/README_EN.md)

In 0.0.9, `create_saved_leader` creates a temporary character for the preview. The event displays that character through its saved reference. When the editor discards the preview, `remove_saved_leader` removes the character. Vanilla documents this lifecycle in `localisation/99_README_SAVED_LEADERS.txt` and uses it in `events/origin_events_forceofwill.txt`. Apply copies the preview to the sample species and passes that species to `change_leader_portrait` on the selected scientist, following `events/origin_events_machine_age.txt`. [Preview setup](../../RB_LE/mod/common/scripted_effects/rb_le_portrait.txt)

The 0.0.8 prototype passes a leader target to `change_species_characteristics` following `clones.1` in `events/clone_army_events.txt`. Only the dedicated sample species receives the copy. The `species_portrait` trigger checks the result. Keys `human_female_01` and `human_female_02` come from `gfx/portraits/portraits/07_portraits_human.txt`. Apply uses `change_leader_portrait` following Azaryn's events in `events/paragon_events.txt`. [Phenotype probe](../../RB_LE/mod/common/scripted_effects/rb_le_portrait.txt) · [Trial events](../../RB_LE/mod/events/rb_le_portrait_events.txt)

Version 0.0.7 applies `change_background_ethic` to the selected leader as in `events/paragon_events_3.txt`. Eligibility uses the vanilla `is_gestalt` and `is_egalitarian` triggers and their counterparts for the other personal ethics. The editor reads `leader_age` and uses `add_age` to change it. Vanilla uses a negative delta in `events/astral_rifts_1_events.txt`. The minimum ages of 16 and 0 are editor rules. [Action conditions](../../RB_LE/mod/common/scripted_triggers/rb_le_editor.txt)

XP actions use `add_experience`. Vanilla passes a negative script value to this command in `common/council_agendas/00_council_agendas.txt`. Removing all current-level XP uses the negative of `has_experience` evaluated at the time of the click. Lowering the base level uses `set_skill`. [Editor events](../../RB_LE/mod/events/rb_le_editor_events.txt) · [Script values](../../RB_LE/mod/common/script_values/rb_le_editor.txt)
