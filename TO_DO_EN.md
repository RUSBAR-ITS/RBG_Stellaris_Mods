# RBG_Stellaris_Mods shared task list

## Contents

- [VANILLA-001 — CLASS arguments in trait templates](#vanilla-001--class-arguments-in-trait-templates)
- [VANILLA-002 — RELIC parameter in Grand Archive rewards](#vanilla-002--relic-parameter-in-grand-archive-rewards)

## VANILLA-001 — CLASS arguments in trait templates

- [ ] Prepare and agree on a fix for passing `CLASS` through leader-trait inline chains.

Game-fix status: deferred. WEB_STTV import has an approved and implemented targeted exception under [stage 19](WEB_STTV/Docs/TZ_BACKEND_STAGE_19_EN.md#7-dlc-source-exception): preserve explicit CLASS from the call chain, otherwise use the sole leader_class or leader for multiple classes. Game sources are unchanged; this import correction does not complete the game-fix task.

Found during the WEB_STTV audit of the installed game on 2026-11-15. The original audit affected 14 files under common/traits: 10 stopped in trait/icon_element/council_no.txt and another four in trait/icon.txt.

Confirmed examples:

- The `trait/icon_negative` call in [00_admiral_traits.txt:1836](/E:/SteamLibrary/steamapps/common/Stellaris/common/traits/00_admiral_traits.txt:1836) supplies `ICON`, `COUNCIL`, and `TIER`. Nested [council_no.txt:1](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/trait/icon_element/council_no.txt:1) uses `$CLASS$`, which is absent from this chain.
- The `trait/icon` call in [06_distant_stars_traits.txt:8](/E:/SteamLibrary/steamapps/common/Stellaris/common/traits/06_distant_stars_traits.txt:8) also omits `CLASS`, used by the [template:4](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/trait/icon.txt:4).

When preparing the fix, determine the correct value for each case, including traits shared by multiple leader classes; check argument forwarding to nested calls. Do not choose an arbitrary class merely to satisfy the parser. Specify delivery in a separate specification; the installed game remains read-only.

Future verification: all 14 files expand without `CLASS` errors; the user checks trait icons and subtitles in-game. Missing arguments are confirmed in source code; the engine's behavior when arguments are omitted has not been separately verified.

## VANILLA-002 — RELIC parameter in Grand Archive rewards

- [ ] Verify the suspected `$RELIC$` typo and prepare an agreed reward-template fix.

Status: deferred; implementation has not started. Affects chains originating in `events/grand_archive_events.txt` and `events/leviathans_events_1.txt`.

[stage_3_reward_option.txt:15](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/grand_archive/collection/stage_3_reward_option.txt:15) uses `gave_relic_$RELIC$`, but the [calling template:1](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/grand_archive/collection/stage_3_reward_options_by_category.txt:1) supplies `SELECTED_RELIC` and `OTHER_RELIC_1`–`OTHER_RELIC_4`. It does not supply `RELIC`. Other checks and the selected relic award use `SELECTED_RELIC`.

The proposed fix is `$RELIC$` → `$SELECTED_RELIC$`; confirm the check's purpose throughout the template and its callers before implementation. Deliver the fix separately without modifying the installed game.

Future verification: both event chains expand without the `RELIC` error; the user checks reward availability, the selected relic award, and duplicate-award prevention in-game.
