# Leader Editor — dossier management menu

## Contents

- [Agreed structure](#agreed-structure)
- [Navigation across all menus](#navigation-across-all-menus)
- [Former occupation](#former-occupation)
  - [Occupation visibility in 4.6.0](#occupation-visibility-in-460)
- [Personal details](#personal-details)
- [Portrait editor prototype](#portrait-editor-prototype)
- [Checks before implementation](#checks-before-implementation)

## Agreed structure

Actions open from the selected character's dossier. The event description continues to show the [leader's details](REQUIREMENTS_0_0_4_EN.md).

```text
Dossier
├─ Personal details
│  ├─ Change personal ethic
│  ├─ Change age
│  │  ├─ Rejuvenate
│  │  └─ Age up
│  ├─ Change gender
│  └─ Change portrait
├─ Background
│  └─ Change former occupation
├─ Experience and level
│  ├─ Grant experience
│  ├─ Remove experience
│  └─ Lower level
├─ Traits
│  ├─ Add Traits
│  └─ Remove Traits
├─ Back
└─ Exit
```

Normally, show a section when it contains at least one action available to this leader. In the first stage, Traits and both of its entries are visible for every selected leader, including a leader with no traits. Back goes up one menu level, or returns from the dossier to the originating register page. Exit closes the Personnel Department.

Grant experience is available below the base level cap. Both XP menus use steps of 10, 100, 1,000, 10,000 and 100,000. Remove experience offers steps covered by the current level’s accumulated XP and “Remove all experience from this level”. At zero XP the removal submenu is hidden. Lower level lists the base levels below the current one. For example, level III offers I and II. XP, specialization and trait selection after a downgrade require an in-game check.

In the first stage, Add Traits and Remove Traits each open an empty catalog. Each screen has exactly two buttons. Back returns to Traits and Exit closes the Personnel Department.

The next stage will populate the catalogs.

- **Add Traits.** Use the previously designed subcategories. Available choices depend on leader class, prerequisites, ranks and direct opposites. [Basic trait requirements](BASIC_TRAIT_MENU_REQUIREMENTS_4_6_0_EN.md)
- **Remove Traits.** Cover all leader traits in the game. List and allow removal of every trait the selected leader actually has, including traits outside the Add Traits catalog. Possession of the trait is the sole condition for listing it.

Former occupation and possible biography text editing belong under Background. In 0.0.7 Background stays hidden until its first editing action is available.

## Navigation across all menus

In 0.0.16 all Leader Editor screens use full navigation labels. After the screen's entries, show the applicable controls in this order from top to bottom: Next, Previous, Back, Exit.

- In leader registers and the former occupation catalogue, both page controls appear on every page when at least two pages are available. Next wraps from the last page to the first. Previous wraps from the first page to the last. Hide both for empty and single-page lists.
- Back opens the parent menu. The dossier returns to the originating register page. The occupation catalogue returns to Background. The department's main menu has Exit as its only navigation control.
- Exit closes the entire Personnel Department from any screen. Reopening the department starts at its main menu.
- The portrait preview uses the full labels Next variant and Previous variant to cycle the selected feature. Back returns from a feature to the same preview, and from the feature list to Personal details without applying it. Accept saves the portrait. Cancel lets the player discard the entire preview directly while cycling a feature.

Check empty, single-page and multi-page lists, wrapping in both directions in a register and the occupation catalogue, return to the originating register page, and Back and Exit with a pending portrait preview. Check both languages.

## Former occupation

1. Hide Change former occupation for a selected leader whose personal ethic is Gestalt Consciousness. Check the leader's own ethic. Hide Background when it has no remaining actions.
2. Start with the IDs marked Yes in the catalogue's overall former occupation column. Source review for 4.6.0 confirms 102 such IDs, including `civilian`. The special value `none` is outside the selection. [Occupation catalogue](BACKGROUND_JOBS_4_6_0_EN.csv)
3. Before displaying the list, check which occupations are possible in the leader's current empire. For an ordinary job, the empire must be able to provide that job under its current conditions. Current staffing is irrelevant. For a scripted occupation, check the requirements of the vanilla source. If there are several routes, any available route suffices. Hide the command when no options remain.

When preparing the buttons, record the vanilla source of each occupation in a playable empire. Fallen empires are outside this selection. The dossier of the leader gifted to a Scion displays their former occupation, Overseer (`fe_overseer`). Receiving that leader does not unlock Overseer for assignment in the editor. [Vanilla requirements for Overseer](BACKGROUND_JOBS_4_6_0_EN.md#editor-proposal)

For in-game verification, use one leader with a gestalt personal ethic and one with an individual ethic. For the latter, compare the list before and after unlocking a restricted occupation, including while nobody holds that job. In both cases IDs marked No or Unverified and the special value `none` must be absent.

In 0.0.15 Background shows the leader's name and former occupation when vanilla supplies it for display. The catalogue presents up to ten alternative occupations per page in vanilla ID order. Choosing one rechecks the leader and the occupation, then opens the updated dossier. Back leaves the list without changing the occupation. Test a choice on the second page and confirm it persists after reloading a save.

For a prospective building, the script can identify an eligible specialization and count free building slots across the colony. If the only free slot belongs to another specialization, the editor may offer the occupation before the building can be constructed. For existing jobs the engine reports capacity directly.

### Occupation visibility in 4.6.0

The [menu table](BACKGROUND_JOB_VISIBILITY_4_6_0_EN.csv) records all 102 original candidates after excluding Overseer. Review identified 101 conditional choices. Sand Caretaker (`sand_caretaker`) has a single job grant with mutually exclusive requirements for a playable empire. The table retains this row with the decision Hide.

**Reading a row.** Check the selected leader's personal ethic, then apply When to show. A profession with two routes requires either its scripted route **or** a job provider. The uncapped jobs are `civilian` and `squire`. For other economic routes, filter the [provider register](BACKGROUND_JOB_VISIBILITY_SOURCES_4_6_0_EN.csv) by occupation ID. Each row identifies one contributing grant, its value, branch conditions and vanilla source lines. A single provider may have several conditional branches. If several grants affect the result, require a positive net job count.

**Colony and provider.** A domestic colony, including an inhabited ark, must qualify. An active provider suffices, as does the ability to construct or upgrade one on a specific owned colony under current technologies, specializations, rights and other vanilla conditions. Occupancy and vacancies are irrelevant. For prospective construction, evaluate compatible district and zone sets, building access and upgrade paths. Disregard the current queue and resource stockpile. For an existing provider, check its active grant. Original construction requirements and random feature spawn weights do not cancel a functioning source. A feature or modifier granted by an event must already exist on an owned colony. A governor bonus requires an active source.

**Residents and holdings.** Job conditions apply to a potential worker on the host colony. A psionic worker requirement therefore tests the local population independently of the leader being edited. For the 17 subject holding professions, the workers belong to the subject. The subject player qualifies if the holding operates or could be built on their colony under the current agreement. Evaluate overlord and subject capital conditions in their respective scopes. Likewise distinguish the branch office owner from the colony owner for `shroud_trader`.

In 0.0.17 the allowed and remaining holding counts start at `base = 0`. Both empire modifiers and the calculated limit enter their respective formulas through `add`. Check a zero limit, an overlord bonus, and a full quota on one colony and across multiple colonies. After a fresh launch, open the occupation catalogue and check `error.log` for parsing errors from either formula.

In diagnostic build 0.0.18, each time the player opens Change former occupation, write `RB_LE occupation trace BEGIN` to `error.log`, followed by each occupation ID immediately before its check and a final `END` marker. Paging does not repeat the trace. During the game test, find `Invalid context switch` and read the adjacent entries in the same log. An error outside the scan cannot be attributed to an individual occupation from this trace.

Since 0.0.19, require `has_branch_office = yes` on the colony before checking the branch office owner for a prospective corporate building. Occupied jobs, free jobs and other sources still count on colonies without a branch office. On a colony with a branch office, eligibility respects its owner's type and the building's requirements.

For the 0.1.0 release, remove the temporary messages written to `error.log` during the occupation scan. Verify the order of all 101 occupations, assignment of the selected option, paging and branch office owner checks.

**Scripted occupations.** In Domestic scripted route, `POOL(class)` refers to one of the three vanilla background lists. A non-gestalt empire has this route through its starting ruler event `paragon_2.2125`. During recruitment, `leader_trait_gifted` can call all three lists with Galactic Paragons if the crisis faction check passes. The traits `leader_trait_army_veteran` and `leader_trait_retired_fleet_officer` call the commander list for official and scientist candidates. Check whether the empire can grant the appropriate background. The edited leader's class, traits and recruitment status impose no additional requirements. A story assignment to a foreign faction alone cannot unlock the profession for the player. [Vanilla lists](<E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/paragon_effects.txt:2832>)

**In-game acceptance.** Verify Civilian with zero civilian employment and Captain without a shipboard job in the economy. With cyberdome access, Spectator appears before `neurocasted_spectacles` and Duelist appears after enacting it. Check both sides of a holding agreement, empires with different psionic worker eligibility, a colony with an academy, and an inhabited ark separately. A leader with the gestalt personal ethic has no editing command in any of these cases.

## Personal details

Each screen shows the leader's name and the current value. After applying a change, the player sees the result and the actions available for the same character.

**Change personal ethic.** Show the individual leader's current ethic in the description. Offer the remaining regular ethics regardless of governing ethics. Hide this command for a leader with the Gestalt Consciousness ethic. Once populated, the trait catalog must use the new personal ethic.

List the ethics in this order on one screen — Egalitarian and Authoritarian, Xenophile and Xenophobe, Militarist and Pacifist, Materialist and Spiritualist.

**Change age.** The player chooses a direction, then a number of years. Each available step shows the resulting age. Recalculate the available steps from the new age after each change.

| Submenu | Steps in years | Visible choices |
|---|---|---|
| Rejuvenate | 1, 5, 10, 50, 100 | The resulting age must be at least 16 for an organic leader or at least 0 for a synthetic leader. A step may reach the minimum exactly. Hide Rejuvenate when no step is available. |
| Age up | 1, 5, 10, 50, 100 | All five steps are available at any current age. |

Use the selected leader's own species type, as shown in the dossier. Special species can appear there as “Non-robotic”. The minimum age for this third type is still open. In 0.0.7 these leaders have access to Age up. [Dossier species type definition](../../RB_LE/mod/common/scripted_loc/rb_le_dossier.txt)

**Change gender.** The command is available for every leader with an editable dossier, including robots, synthetics, gestalt leaders and unique characters. Species, its `species_gender` setting, empire type and portrait impose no restrictions. The description shows the leader's name and current gender. Of the three vanilla values (`male`, `female`, `indeterminable`), show the other two as buttons using the game's labels. A choice applies `set_gender` to the selected leader and refreshes the same screen. Back returns to Personal details and Exit closes the department.

**Change portrait.** Show the command for a recognised ordinary appearance when its set has at least one editable feature. The preview opens on the first available choice for each feature. Arrows change the preview within the current set. Accept saves the displayed appearance to the selected leader. Cancel returns to Personal details with the appearance the leader had when the editor opened. Exit closes the department and discards the selection.

The standard leader card already supports renaming. Species and years of service are proposed as reference fields. [Vanilla commands and constraints](VANILLA_LEADERS_4_6_0_EN.md#editor-scope-and-character-background)

## Portrait editor prototype

**Opening, cancelling and accepting.** The original appearance is the exact appearance of the selected leader when the editor opens. Every visit starts on the first available option for each control in the recognised set, including visits after a previous acceptance. The preview displays that combination. During selection, the leader retains the original portrait. Cancel discards the preview, so the editor does not need to read the original vanilla hairstyle and clothing indices. Only Accept writes the displayed combination, even if the player keeps the first choice for every control.

**Full variant catalogue.** The menu is built from the installed vanilla definitions. For each set, inspect all five controls from the standard editor: phenotype, hairstyle or other attachment, clothing, texture variant and evolution stage. Determine the number of distinct available choices for each parameter of the selected phenotype. Show a 1-to-N control when two or more choices are available. A single eligible choice is used automatically. Changing phenotype recalculates dependent ranges. Keep a selected asset if the new phenotype supports it, otherwise use the first available choice. The existing restrictions for unique and unrecognised appearances still apply.

The Stellaris 4.6.0 (`3d1a`) scan covered 67 set definitions in `common/portrait_sets` and 504 concrete definitions in `gfx/portraits/portraits`, including internal and story portraits. The inventory records phenotype group conditions, textures, hairstyle and clothing selectors with distinct available file counts, evolution rules and texture bindings. The file counts describe the visual assets available to the mod. Vanilla generation applies role-specific rules. For example, an ordinary scientist from the modern human set receives a scientist uniform, although the set contains seven outfits. Repeated references to the same file count once. Five referenced attachment selectors could not be resolved in the installed data. Their counts are marked unknown. [Inventory with counts and sources](../../TMP/RB_LE/portrait_inventory_460.json)

| Human set | Phenotypes | Textures per phenotype | Hair options by phenotype 1–5 | Outfits | Stages |
|---|---:|---:|---|---:|---|
| Modern female | 5 | 5 eye colours | 26 each | 7 | base only |
| Modern male | 5 | 5 eye colours | 86 each | 7 | base only |
| Legacy female | 5 | built-in model appearance | 34, 7, 21, 43, 8 | 7 | base only |
| Legacy male | 5 | built-in model appearance | 81, 20, 20, 96, 20 | 7 | base only |

Legacy humans have no separate list of colour textures. The count of 96 for the fourth legacy male phenotype includes distinct appearance asset files. Other sets may use a mask or hat as their attachment. There are 59 definitions with evolution rules. Of these, 35 define two additional stages, 13 define one, and 11 disable their only rule through `always = no`. Some colour textures are tied to specific evolution variants.

The catalogue is built when preparing the mod. In game the menu looks up the entry for the leader's set and phenotype. The effect and trigger documentation exported by Stellaris 4.6.0 contains no known command to return the sizes of these lists during an event.

| In-game check | Expected result |
|---|---|
| Open the editor, change several controls and cancel. | Controls start on the first choices. After cancellation the standard card matches the original exactly. |
| Accept a combination, reopen the editor, then cancel. | The card matches the accepted preview. The new session starts on the first choices, and cancellation preserves the previously accepted appearance. |
| Accept immediately after opening. Reload the save. | The leader retains the displayed combination of first choices. |
| Switch from legacy male phenotype 4 to phenotype 2. | The hairstyle count changes from 96 to 20. Other controls use the assets available to the new phenotype. |
| Check a regular human portrait and a story-specific one. | The human has no stage control. Unique characters have no edit command. |
| Check `tox2`, `sd_hum_robot` and `cyb1`. | The toxoid has three masks, the robot has four colours, and the cybernetic portrait has three stages including its base appearance. |
| Change the colour and stage of `pro1_f`, accept, then reload the save. | The base colour and the stage overlay match the preview. |

**Portrait controls.** For each editable feature, show Next immediately above Previous. Next on the last choice goes to the first. Previous on the first goes to the last. Both arrows remain visible for two or more choices. After changing phenotype, retain compatible details across these transitions as well.

**Application check.** All five modern female human phenotypes share 26 hair choices. The set contains five styles in five colours plus a separate default texture. On a serving leader and a ruler, change just the hairstyle, accept and compare Personal details and the standard leader card with the preview. Repeat with clothing alone and after loading a save. Preview and acceptance must refer to the same full appearance, including the attachment and clothing. Reopen the editor, step back from 1 to 26 and forward to 1, then cancel. The previously accepted appearance must still be visible.

**0.0.10 menu.** Open Personnel Department → leader dossier → Personal details → Change portrait. Each available control displays its current position and number of choices. Select a control to open its arrows. Back returns to the controls for the same preview. Both screens offer Accept and Cancel. Regular leaders can use the editor directly. The attachment control is hidden for five undefined vanilla selectors. Four colours are available for `bio7`. Its two additional stages lack their mask textures in the game files.

**In-game test for 0.0.8.** In the Personnel Department, open Personal details for two serving leaders of the same species. Compare their faces, hairstyles and clothing with their standard leader cards. This part can be tested in a regular game.

To test the selector, start a separate game as the default United Nations of Earth. Enter `event rb_le.90` in the console. The event creates a Portrait Test Scientist with phenotype `human_female_01` and a separate sample species with no pops. Both objects remain in the test game. Calling the event again reuses that empire's existing test objects.

1. Open Personnel Department → Scientists → Portrait Test Scientist → Personal details. Change portrait appears only when one of the two trial phenotypes is detected. If the screen reports that the phenotype could not be identified, look for `RB_LE portrait probe` in `logs/game.log`. A result of `species group human` means the check returned the generic human set.
2. The first visit should offer “Phenotype 2 >”. Note the hairstyle and clothing, preview the second sample and select Back. Compare the original appearance. Select the second phenotype again and choose Apply. The card should retain every other detail, and reopening the editor should now offer “< Phenotype 1”.
3. To test a story-specific override with Galactic Paragons, close the windows in the test game and enter `effect random_owned_leader = { limit = { has_leader_flag = rb_le_portrait_trial@root } change_leader_portrait = paragon_azaryn_no_buds }` in the console. Reopen the test scientist's personal details. The edit command should be hidden. Other leaders in the regular register support portrait viewing only.

If the initial phenotype cannot be identified, the change itself can still be tested independently. Pause, note the test scientist's face, clothing and hairstyle, and close the windows. In the same test game enter `effect random_owned_leader = { limit = { has_leader_flag = rb_le_portrait_trial@root } change_leader_portrait = human_female_02 }`. Reopen the standard card and Personal details. The face shows the effect of the command, and the next `RB_LE portrait probe` log entry shows whether the script could read the result.

**Repeat selection in 0.0.9.** In 0.0.8 the game recognised the original `human_female_01`. The reverse arrow showed the scientist's original portrait, but selecting phenotype 2 again produced a different appearance. A save that already contains the test scientist can be used for this check.

1. Open the scientist's portrait and select **1 → 2 → 1 → 2** with the arrows. Both views of phenotype 2 should have the same face, hair, clothes and colours. Only the face should change between the two phenotypes.
2. Choose Back without applying and compare the scientist with the original. Open phenotype 2 again, note the preview and select Apply. Compare both Personal details and the standard leader card with that preview.
3. After applying, test the reverse path **2 → 1 → 2 → 1**. An `RB_LE portrait applied from preview` entry in `game.log` confirms that the change was requested. Preserved hair, clothes and colours require a visual check.

## Checks before implementation

1. After changing the personal ethic, compare the dossier and the traits available to grant. Check an individual whose ethic differs from the empire's and a gestalt leader.
2. Rejuvenate a 66-year-old organic leader by 50 years to reach 16, and a 100-year-old synthetic leader by 100 years to reach 0. Rejuvenate should disappear after each change, and Age up should still offer all five steps. A 65-year-old organic leader should have no 50-year decrease, and a 99-year-old synthetic leader should have no 100-year decrease.
3. Lower a level IV leader with a specialization and partial XP to III, then raise them to IV again. Check the XP balance, traits and eligibility for a new selection.
4. In the first stage, open both catalogs for a leader with traits and one without traits. In each catalog, verify that only Back and Exit appear and that both buttons lead to the specified destinations.
5. At 100 XP, verify that removal offers 10, 100 and the entire balance. Remove the entire balance and check the vanilla leader card for zero XP and the original base level. Separately grant 100,000 XP and check the game’s trait choices when crossing multiple levels.
6. Cycle through all three genders on an organic leader and a robot whose species has a fixed gender setting. Each time, check the selected character's name and gender in the dossier, the two available choices, forms of address and appearance on the standard leader card. Check access for a unique leader, return to Personal details and reopen the dossier.
7. In 0.0.14 test the vanilla effect on a modern human with an accepted RB_LE appearance. Open Personal details, change the gender, go back and open Change portrait. Compare the saved RB_LE look number before and after in `game.log`. Zero means the readback did not identify an RB_LE appearance. The first female phenotype has 26 hair choices, the first male phenotype has 86, and the combined human catalogue has ten phenotypes. Cancel the preview before repeating the test in the other direction. The gender command calls only `set_gender` on the leader. The portrait editor uses its existing recognition rules throughout this test.
