# RB_LE — affected files and functions

## Contents

- [Decision and events](#decision-and-events)
- [Target and navigation](#target-and-navigation)
- [Leader details](#leader-details)

## Decision and events

Version 0.0.2 adds the Personnel Department planetary decision. It checks colony ownership and opens an event for the player’s empire. Every screen uses the vanilla `GFX_evt_galactic_senate` illustration from `interface/eventpictures.gfx`. The decision uses the `decision_politics` icon. The menu runs on Stellaris `v4.6.*` events and ships with RB_LE. [Decision](../../RB_LE/mod/common/decisions/rb_le_personnel.txt) · [Events](../../RB_LE/mod/events/rb_le_dossier_events.txt)

## Target and navigation

The `ruler` scope identifies the current ruler. The register visits other serving leaders with `every_owned_leader` and filters them by `leader_class`. During page preparation, `save_event_target_as` binds each button to a leader object. The button displays that character’s `GetName` and opens the same character’s dossier. Exit clears the temporary variables and the open-register flag. [Page preparation](../../RB_LE/mod/common/scripted_effects/rb_le_register.txt) · [Requirements and acceptance](REQUIREMENTS_0_0_2_EN.md)

## Leader details

Since 0.0.5 the event calls conditional fields on the character, for example `[rb_le_selected_leader.rb_le_job_line]`. Both the `has_background_job` check and the `[GetBackgroundJob]` substitution receive that leader. Vanilla similarly calls `[Actor.GetInviteIdeologyExtra]` and reads `[GetName]` in the selected string. For an ark, the event's conditional string uses the saved target name `[rb_le_home_colony.GetName]`, following `[replacement_leader.GetSubclass]`. Both examples are in `localisation/english/forceofwill_l_english.yml` and `common/scripted_loc/16_scripted_loc_forceofwill.txt`.

In 0.0.4 the dossier reads `GetAge`, `GetYearsOfService`, `Species.GetName`, `Species.GetClass`, `GetBackgroundEthic`, `GetBackgroundPlanet`, `GetHomeWorldBiome`, `GetBackgroundJob`, `GetClass`, and `GetSubclass`. A mobile home colony supplies its name through the `background_colony` scope. The `has_background_job` trigger, the `is_subclass` filter of `num_leader_traits`, and vanilla personal ethic checks control optional lines. Species type uses `is_robotic` and the `BIOLOGICAL` and `LITHOID` archetypes. Other non-robotic species display “Non-robotic”. [Display conditions](../../RB_LE/mod/common/scripted_loc/rb_le_dossier.txt)

The selected leader supplies `has_base_skill`, `has_total_skill`, and `has_experience`. The XP threshold uses `get_leader_exp_to_level` following `common/script_values/09_script_values_forceofwill.txt`. Stellaris 4.6.0 sets the base cap to 10 with `NGameplay.LEADER_BASE_SKILL_CAP` and `LEADER_MAX_SKILL_CAP` in `common/defines/00_defines.txt`. The register owner holds four numeric fields until the dossier closes. [Dossier data](../../RB_LE/mod/common/scripted_effects/rb_le_dossier.txt) · [XP threshold](../../RB_LE/mod/common/script_values/rb_le_dossier.txt)
