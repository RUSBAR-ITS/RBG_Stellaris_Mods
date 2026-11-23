# RB_SDM mod author guide

## Contents

- [What the template does](#what-the-template-does)
- [Try the menu](#try-the-menu)
- [Let the AI take a decision](#let-the-ai-take-a-decision)
- [Copy a section into your mod](#copy-a-section-into-your-mod)
- [Add an entry](#add-an-entry)
- [Check your catalog](#check-your-catalog)

## What the template does

RUSBAR Stellaris Dynamic Menu shows actions available for a selected object in the order specified by the author. If 89 out of 200 actions qualify and the page size is 10, the player gets eight full pages and a final page with nine actions. To place a new action between two existing ones, insert a single catalog entry between them.

**Version 0.0.1 for Stellaris v4.5.*.** The game package is in [mod/](mod/). Synthetic checks used v4.5.4 data. In-game verification is pending. [Technical specification](Docs/TZ_EN.md) · [Changelog](Docs/CHANGELOG_EN.md) · [Vanilla changes](Docs/VANILLA_CHANGES_EN.md)

## Try the menu

The demo targets the base game and can run with all DLC disabled.

1. Point a local mod entry at `RB_SDM/mod/` and enable it in the playset. Open the decisions on a colony you own and select “Open dynamic menu”.
2. Open the demo section. Page 1 shows examples 1–10 of 21. Choose Next twice to reach example 21.
3. Select example 21. It disappears for the rest of this session, and the menu opens page 2 of 2 with examples 11–20.
4. Go to the first page and select example 1. Example 11 fills the vacant place, leaving 12–20 on page 2.
5. Choose Back and re-enter the section. It opens at page 1 with the previously selected examples still hidden. Choose Close and reopen the decision to restore the original 21 entries.

## Let the AI take a decision

The author sets the switch in the [decision settings file](mod/common/scripted_triggers/rb_sdm_decision_settings.txt). To give access only to humans, keep the default definition.

```text
rb_sdm_open_menu_ai_enabled = { always = no }
```

Change `always = no` to `always = yes` to allow the AI to take this decision on an eligible owned colony. The decision uses that trigger for country eligibility and AI weight. Human players open the usual menu in either mode. When an AI takes the decision, its handler receives the colony and runs the action specified by the author. The demo selects the first available entry. When copying the decision, give the new switch its own name if you need independent settings.

The demo comes with a planetary decision as its entry point. To open the menu from another event, save the planet as `event_target:rb_sdm_target` and invoke the parent event for the human player's country. That entry point has its own eligibility rules. When changing the target type, check the scope of the catalog's triggers and effects. [Entry point and AI access](Docs/TZ_EN.md#entry-point-and-ai-access)

## Copy a section into your mod

1. From the game package, copy the templates in `common/inline_scripts/rb_sdm/`, the supporting `scripted_effects` and `scripted_triggers`, the parent and list events, and the shared RU/EN text. Replace the `rb_sdm_` prefix, the `rb_sdm` event namespace and include paths consistently throughout the copies. Use the receiving mod's descriptor.
2. Connect your mod's entry point to the parent event. In the planet example the decision saves `event_target:rb_sdm_target` and opens an event for the player's country. Call the public event `rb_sdm.1`. It checks the country, target and session lock. After changing the prefix, use the new target name throughout the chain.
3. Following the demo section, specify the title and description keys, parent event, ordered catalog and a positive integer page size. For a second section, create a separate catalog and list event. In the parent event `rb_sdm.2`, have the section button set the initial page to 1 and open its list. In `rb_sdm_end_session`, add a cleanup pass for the new catalog to remove its ranks and temporary entry state.
4. The list event includes the same catalog in its `immediate` block in `rank` mode and in the event body in `option` mode. The first pass assigns ranks for the selected target. The second inclusion declares buttons. Shared navigation uses the same page size. To change capacity from 10 to 6, replace `SIZE = 10` with `SIZE = 6` in the `rb_sdm_begin_count` call inside the list event `rb_sdm.3`. [Events](mod/events/rb_sdm_events.txt) · [Menu effects](mod/common/scripted_effects/rb_sdm_menu_effects.txt)

## Add an entry

This is the declaration for example 7. To add an entry, supply a unique ID and reference existing trigger, effect and localization definitions. Place the entry where it belongs relative to its neighbors. The `PASS` parameter selects the operation and `SCREEN` supplies the list event to reopen. [Demo catalog](mod/common/inline_scripts/rb_sdm/rb_sdm_catalog_demo.txt)

```text
inline_script = {
    script = "rb_sdm/rb_sdm_$PASS$"
    ID = rb_sdm_demo_07
    LABEL = rb_sdm_demo_07_label
    TIP = rb_sdm_demo_tip
    VISIBLE = rb_sdm_demo_07_visible
    ACTION = rb_sdm_demo_07_select
    SCREEN = $SCREEN$
}
```

| Field | What the author supplies |
|---|---|
| `ID` | A key unique within the mod. Keep it when moving an entry. |
| `LABEL`, `TIP` | Label and tooltip keys. Supply both strings for RU and EN. Reference existing game names by localization key. |
| `VISIBLE` | The name of a scripted trigger. It receives the selected planet and determines whether the action is currently available. Demo entry 7 checks whether it has already been selected in this session. |
| `ACTION` | The name of a scripted effect in the same planet scope. Example 7 marks itself as selected for the player's current country session. The template refreshes the page. |

If this entry originally ranked eleventh, removing an available entry above it moves it to the first page. Its key, tooltip and action still belong to the same declaration. The same catalog structure can describe commands, choices or deposit types.

## Check your catalog

Check a full list, a sparse list and an empty selection on one target. A particularly useful case is when only the last 10 of 200 entries are available. They should all appear on the first page in their original order. To check action identity, select an entry that just moved from another page and verify that its own effect ran.

If the section is unexpectedly empty, check the saved target and the scope of `VISIBLE`. If the label is correct but the effect receives a different object, check the scope of `ACTION`. If the count is correct but gaps appear, check the catalog path and order in both inclusions. The [acceptance cases](Docs/TZ_EN.md#acceptance) list the expected results.
