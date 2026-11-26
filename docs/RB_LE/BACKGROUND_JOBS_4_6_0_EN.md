# Leader Editor — former occupations

## Contents

- [Which jobs can be a former occupation](#which-jobs-can-be-a-former-occupation)
- [Catalogue](#catalogue)
- [How vanilla chooses an occupation](#how-vanilla-chooses-an-occupation)
- [Editor proposal](#editor-proposal)
- [Reading and verifying the table](#reading-and-verifying-the-table)

## Which jobs can be a former occupation

**Civilian (`civilian`) can be a former occupation.** If the generator chooses a group of free civilians eligible to supply leaders, it can use their job in the biography. The civilian stratum has a positive base background weight, and the job is uncapped. The `weight = 0` at the end of the job definition governs pop assignment to jobs. Leader generation uses its own weight fields. See `common/pop_categories/02_other_categories.txt:1`, `common/pop_jobs/00_other_jobs.txt:5` and `common/leader_classes/00_README.txt:222`.

In the [English catalogue](BACKGROUND_JOBS_4_6_0_EN.csv), filter **Can be a former occupation (ID) → Yes**. For jobs with an established pop-based generation route, filter **Generated from pops → Yes**. Civilian has **Yes** in both columns. The columns named after script commands cover explicit assignments only.

| Can be a former occupation (ID) | Rows | Basis |
|---|---:|---|
| **Yes** | 102 | The files establish at least one route. There are 86 IDs with a pop-based route and 23 professions explicitly assigned by script. Seven IDs appear in both sets. |
| **No** | 154 | Ordinary generation has an identified obstacle and the scripts reviewed contain no explicit assignment. This includes display names without a job ID. Each row records the reason. |
| **Unverified** | 175 | Job availability, pop rights or leader recruitment in the relevant country still requires verification. The sole identified source of `sand_caretaker` is unavailable to playable empires. |
| **Special value** | 1 | A script assigns `none` (“None”) to the occupation field. |

For example, **Physicist** can come from pops or a script. **Captain** is explicitly assigned by script and its ID is closed to pops. **Priest** (`priest`) is a contextual name without a standalone job ID in this build. A “Yes” for ordinary generation assumes that the job is occupied by a pop group passing `can_generate_leader_from_pop_group` or its military equivalent, and that the generated leader has an individual ethic. These findings are based on vanilla 4.6.0 rules. Frequencies in saved games were not measured.

## Catalogue

The installed Stellaris 4.6.0 (3d1a) build defines **369 job IDs** across 21 files with job definitions. Jobs have **135 distinct contextual names** in `swappable_data`. Of those, 72 also exist as job IDs and 63 exist only as names. The [full CSV catalogue](BACKGROUND_JOBS_4_6_0_EN.csv) contains **432 data rows**, one per key. Two columns link each base job to its display names and each display name to its base jobs.

| Review group | Rows | Contents |
|---|---:|---|
| Scripted profession | 23 | Explicitly assigned to a leader. Examples include Captain, Physicist, Noble and Overseer. |
| Core job candidate | 15 | Additional candidates for the first menu, including Soldier, Miner, Technician and Roboticist. |
| Special job candidate | 115 | Other candidates with a job definition, including Knight, Professor, the Astro-Harvester aboard an ark and Astral Researcher. |
| Drone or unit | 98 | Jobs in drone strata and two Fallen Empire robot occupations. |
| Population status or dependent population | 61 | Includes assimilation, purging, test subjects, pre-sapients, some forms of servitude and deep sleep aboard an ark. |
| Closed to pops | 56 | The definition sets `possible = { always = no }` and the scripts contain no explicit leader assignment. Examples include `researcher` and `duelist`. |
| Display name only | 63 | Appears as another job's `swap_type.name` and has no standalone job definition. Examples include Priest for Bureaucrat and Tourist for Civilian. |
| Special value | 1 | `none` (“None”) is a registered job ID. Vanilla uses it in `paragon_events_4.txt:3180`. |

These groups are an editorial proposal for the menu. Each row belongs to one group, with explicit assignment taking precedence. For example, Angler has its own ID, its pop eligibility is disabled, and it also serves as a display name of Farmer. A vanilla leader trait explicitly assigns Angler as a background. The row records all three facts. Across the catalogue, **71** definitions explicitly close the job to pops, including the special value and several scripted professions.

## How vanilla chooses an occupation

During ordinary generation, the game selects an eligible pop group and then one of its occupied jobs. It considers the number of pops working the job, its background weight and adjustments for the leader class and the empire's ethics. Soldier has an additional commander weight of 100. A job without weight adjustments has a base multiplier of 1. The result also depends on pop rights and available jobs. For a leader with the gestalt background ethic, the generator leaves the stratum and former occupation empty. See Leader Generation Details and Job weight in `common/leader_classes/00_README.txt`. The pop-group rules are `can_generate_leader_from_pop_group` and `can_generate_military_leader_from_pop_group` in `common/game_rules/00_rules.txt`.

Vanilla scripts assign **22 named occupations** using `change_background_job`. One additional occupation, `fe_overseer`, appears in the `background_job` field at leader creation. Captain and Commanding Officer appear in both paths. An event also assigns `none`. The CSV gives the file and line for each assignment. A `has_background_job` check is evidence of a lookup. For example, `common/scripted_triggers/03_scripted_triggers_paragon.txt:330` checks Knight, Ranger and Duelist among other IDs.

## Editor proposal

**Dossier → Background → Change former occupation** uses 101 IDs with an overall Yes and a source in a playable empire. Hide the command for a leader with the gestalt personal ethic. For other leaders, the buttons depend on which occupations are possible in their current empire. [Rules by ID](BACKGROUND_JOB_VISIBILITY_4_6_0_EN.csv) · [Menu requirements](DOSSIER_MENU_REQUIREMENTS_EN.md#former-occupation)

For Soldier, check whether the empire can provide the job. For Captain, vanilla uses a direct assignment in `common/scripted_effects/paragon_effects.txt:2834`.

Overseer (`fe_overseer`) is excluded from the menu for playable empires. The job uses `can_fill_precursor_job`, which requires the owner to satisfy `is_fallen_empire = yes` (`common/pop_jobs/07_fallen_empire_jobs.txt`, `common/game_rules/00_rules.txt:2961`). Its overall catalogue entry remains Yes because vanilla explicitly assigns this background to the leader a patron gifts to its Scion (`common/scripted_effects/federations_event_effects.txt:2702`).

After selecting an available profession, check `has_background_job = <ID>`, the dossier, the vanilla biography and the saved result after reloading. A unique character's authored biography may omit the occupation.

## Reading and verifying the table

- Explicit assignment and predicate columns record literal references in the installed `common/` and `events/` scripts. Scripted localisation predicates have their own column. Pop-based generation also considers job and pop-group eligibility. For capped jobs, “Example job slot source” identifies a positive job grant where one was found. Uncapped jobs require no such grant.
- An empty definition column identifies a name without its own ID. Its display name source gives the parent job and line. “Explicitly closed to pops” records an unconditional `always = no` inside `possible`. Other eligibility checks can also restrict a job.
- Weights come from the project parser's expanded definitions. “Conditional” points to the source file on the same row. Russian names use `job_<ID>` and the project's localisation priority order. Two keys missing from the local reference corpus use the installed vanilla Russian localisation (`professor`, `culture_worker_gestalt`). Dynamic names retain their game substitutions.
- Verification reconciled all expanded job IDs with the installed files, linked the contextual names to their owners and checked the explicit assignment references. Whether every ID can be applied to a particular character still requires an in-game test.
