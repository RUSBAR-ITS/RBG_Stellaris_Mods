# RB_SDM technical specification

## Contents

- [Purpose and distribution](#purpose-and-distribution)
- [Entry point and AI access](#entry-point-and-ai-access)
- [Menu behavior](#menu-behavior)
- [Catalog and refresh](#catalog-and-refresh)
- [Session and selection](#session-and-selection)
- [Demo section](#demo-section)
- [Acceptance](#acceptance)

## Purpose and distribution

**Approved on 22 November 2026. Implemented in 0.0.1.** RUSBAR Stellaris Dynamic Menu is a standalone template mod. A mod author can copy its event menu into another mod. The reference installation is vanilla Stellaris v4.5.4. The first game package has version `0.0.1` and declares `supported_version="v4.5.*"`. Custom game identifiers use the `rb_sdm_` prefix and events use the `rb_sdm` namespace.

The `RB_SDM/mod/` directory holds `descriptor.mod`, game scripts and RU/EN localization. The guide at the project root and the documents in `Docs/` live outside the game package. The template runs standalone, including with all DLC disabled. Porting the menu to PDE is a separate task. [Author guide](../README_EN.md)

## Entry point and AI access

The demo starts from a planetary decision on an owned colony. The decision supplies the planet and the initiating country (`from`). To open the event menu, a caller supplies the country and the saved target `event_target:rb_sdm_target`. Another event can supply both. Filtering, ordering and pagination are shared. The first release's demo entry triggers and effects expect a planet. For a catalog targeting another type of object, the author provides triggers and effects for that scope.

**The mod author controls access per decision.** The demo decision has one switch, the country-scoped scripted trigger `rb_sdm_open_menu_ai_enabled`. Its default is `always = no`. The author changes it to `always = yes` to allow the AI to take the decision. The setting lives in the mod files. A copied decision with its own switch can be configured independently.

| Initiator | Eligibility and result |
|---|---|
| Human, either setting | When the usual conditions pass, the decision opens the menu for the selected colony. |
| AI, disabled | The decision's `potential` excludes it for that country and its `ai_weight` is zero. |
| AI, enabled | On an eligible owned colony, the decision has a positive `ai_weight` and the engine may select it. Taking the decision runs the AI action. |

Both decision checks use the same switch on the initiating country. The colony conditions apply in both modes. At execution the decision rechecks the initiator type and AI permission. It opens the parent window for a human or calls a separate handler with the same target for an AI. The demo handler is a hidden country event that picks the first available catalog entry, checks its `VISIBLE`, runs its `ACTION` once and clears working data. If the selection is empty, the call ends without applying an action. Authors porting the template supply their own AI action. Windows and navigation belong to the human session.

## Menu behavior

Each section has an ordered catalog and a positive integer page size `S`. The demo uses `S = 10`. On entry the menu evaluates availability for the selected target, skips unavailable entries and preserves the relative order of available entries. Let `N` be the number available. For `N > 0` the menu has `ceil(N / S)` pages. Page `p` shows available entries numbered from `(p − 1) × S + 1` through `min(p × S, N)`, inclusive. Numbering starts at one.

Entering from the parent menu opens page 1. Previous and Next appear only when a neighboring page exists. Back returns to the parent menu and Close ends the session. All four navigation controls follow the entries and sit outside the page size limit `S`. The title or description displays the current page and total page count through localization substitutions.

Selecting an action refreshes the current page. If that page disappears, the menu opens the last remaining page. At `N = 0` the section displays “No entries available”, Back and Close. The page counter and paging controls are hidden in this state.

## Catalog and refresh

The author maintains one catalog per section. An entry has a stable identifier, a label key, a tooltip key, an availability trigger name and an effect name. Declaration order determines display order. An entry keeps its label, tooltip and action on every page.

The section's single `country_event` includes the same parameterized `inline_script` catalog in two places. In the window's `immediate` block, entries expand into ordered availability checks. In the event body they expand into standard `option` blocks, each with its own display condition. The section defines the page size once. This removes the need for a manually maintained map of entries to pages.

1. On entry, page navigation and refresh after an action, reset the count. Walk the catalog once. Assign consecutive ranks starting at 1 to available entries. Give each unavailable entry rank 0, including entries that were previously available.
2. Use the final count to calculate the number of pages, clamp the requested page and calculate its first and last ranks.
3. Each `option` tests its saved rank against those bounds. Hide all entry buttons when the result is empty. Menu events initiate refreshes. A separate check on selection is described below.

With 200 candidates, each refresh performs 200 availability checks. The event itself declares 200 entry buttons with simple rank checks. Actual time to open the window is measured in game. The design draws on vanilla's parameterized `option` in `common/inline_scripts/grand_archive/collection/stage_3_reward_option.txt` and the variable operations described in `events/000_how_to_use_variables_in_script.txt`.

## Session and selection

The design allows one open session per country. The player's country is the window's `ROOT` and holds the session marker, requested page, counters and entry ranks. The entry decision saves its planet as `event_target:rb_sdm_target` in the event chain. Entry conditions and actions execute in that planet's scope. Different countries have independent sessions.

While a session is open, invoking the decision again cannot create another window for the same country. Back preserves the session. Re-entering a section starts on its first page. Close releases the session and clears its working data. If the target disappears, the next transition ends the session. Verify the same result for normal engine dismissal, including the ability to use the decision again.

Before running an effect, check that the target still exists and that **the entry the player selected** is still available. If availability changed while the window was open, skip the action and refresh. The row's display position never determines which effect runs.

## Demo section

The entry point is a free, instant decision on a colony owned by the initiating country. For a human it opens a parent menu containing one demo section. The section has 21 numbered examples and a page size of 10. Selecting an example hides it for the rest of the session. Opening a new session through the decision restores all 21. This demonstrates entries moving between pages while preserving the colony's deposits and economy.

## Acceptance

| Synthetic case at S = 10 | Expected result |
|---|---|
| 0, 1, 10 and 11 entries available | The empty state, followed by page sizes `[1]`, `[10]` and `[10, 1]` respectively. |
| Of 200 entries, only even IDs from 2 through 178 are available | 89 entries on 9 pages. Page 1 contains 2, 4, …, 20. Page 9 contains 162, 164, …, 178. Concatenating the pages returns all 89 exactly once. |
| Only 191–200 of 200 entries are available | One full page with no paging controls. |
| All 200 are available | 20 full pages. The first and last page each offer only their existing neighbor. |
| Entry 1 is removed from entries 1–21 | Page 1 now holds 2–11. The former third page disappears. |
| Entry 21 is removed from page 3 of entries 1–21 | Page 2 opens with entries 11–20. Removing the last remaining entry opens the empty state. |
| Page size is changed to 3 with 7 entries available | Page sizes are `[3, 3, 1]`. Navigation still sits outside the limit. |

For the implementation, synthetic checks also cover unique IDs, each button's trigger and effect, both localization languages, event links and the contents of the game package. Check the actual catalog and expanded scripts alongside the expected page calculations.

For the decision, check all four combinations of initiator (human or AI) and switch value. Inspect country scope, eligibility, weight and execution branch in the scripts. In game the user checks human access in both configurations, absence of AI calls when disabled, and actual AI enactment when enabled. On enactment, verify the target colony, one action when an entry is available, and absence of an AI menu session. Positive weight makes the decision eligible for AI selection. The engine determines when it takes the decision.

In the installed game the user checks the decision, entry order and labels, tooltips, paging in both directions, movement between pages after selection, the empty state, Back, Close and reopening. Also check country isolation, a second invocation during a session, a change in availability and loss of the target while the window is open. Record in-game results after running those checks.
