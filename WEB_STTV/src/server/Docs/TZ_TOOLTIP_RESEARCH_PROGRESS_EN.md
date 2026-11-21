# Specification. Research progress in technology tooltips and generated data resets

## Contents

- [Card section](#card-section)
- [Data sources](#data-sources)
- [Server index and DLC](#server-index-and-dlc)
- [Resets in system settings](#resets-in-system-settings)
- [Publishing this stage to the test server](#publishing-this-stage-to-the-test-server)
- [Acceptance](#acceptance)

## Card section

Approved on 2026-11-21. This stage covers progress granted to a specific technology by `add_tech_progress`. A **Research progress** section appears at the end of its tooltip, after the weight modifiers. Hide empty sections. Long lists use the existing tooltip scrolling controls. [Base tooltip](../../../Docs/frontend/TZ_TECHNOLOGY_TOOLTIP_CONTENT_EN.md)

Each group describes one gameplay source. Use the localized event or action name as the heading. Explain how to obtain the reward, who receives it, and which option to choose when the choice matters. Show shared conditions once. Give the amount and specific condition for each alternative outcome. Describe random selection, priority order and earlier candidates that must be skipped when these affect the outcome. Use the existing AND/OR phrases with a trailing colon for compound conditions. Display constants as percentages of research progress. Describe variable rewards using a formula with readable terms.

For Crystal-Infused Plating, the sleeping crystal nest group starts with completion of the project to study the unusual asteroid. If the empire can research the technology, the award is **+50%** when it has yet to gain the research option and **+75%** when the option is already available. In the crystal entity study group, include the player's answer about military applications, the condition for choosing it, and its **+50%** reward. The event `grand_archive.2410` has its own group with the preceding candidates in the reward queue. [Special project](E:/SteamLibrary/steamapps/common/Stellaris/common/special_projects/00_projects_3.txt:1547) · [Reward formula](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/00_scripted_effects.txt:4904) · [Event option](E:/SteamLibrary/steamapps/common/Stellaris/events/story_events.txt:2553) · [Reward queue](E:/SteamLibrary/steamapps/common/Stellaris/events/grand_archive_events.txt:2120)

## Data sources

In loader mode `identity = field`, match the identity field name case-insensitively. Preserve the spelling of the ID value and the source tree. Two matching fields in one object raise an ambiguity error.

The installed v4.5.4 (1b4f) survey provides a comparison point. It found 315 technologies, 495 grant sites traced to a calling object and 264 events with direct or nested grants. Other sources include council agendas, traditions, astral actions, resolutions, situations and psionic auras. These counts apply to this snapshot. Rebuild the index from the contents of each new version.

| Purpose | Directories and use |
| --- | --- |
| Already configured | Use expanded documents and their provenance from `events`, `common/traditions`, `common/on_actions` and other existing collections. |
| Missing reward sources | Add `common/council_agendas`, `common/astral_actions`, `common/resolutions`, `common/situations` and `common/patrons/psionic_auras` to parsing and loading profiles. |
| Circumstances leading to a grant | Direct references to reward events include `common/special_projects`, `common/archaeological_site_types`, `common/anomalies` and `common/first_contact`. Include these definitions and follow further references. Document any missing entry point with an example before claiming complete coverage. |
| Astral rifts | Import `common/astral_rifts`. Its `name` and `event` fields link the rift name to its first event. Follow choices to the reward, for example `ancient_battlegrounds → astral_rift.200 → astral_rift.205`. |
| Anomaly outcomes | In `on_success`, recognize a direct event ID and an `anomaly_event` call nested in a weighted block. Identify the DLC required for the anomaly to spawn. For `DISTAR_MERCURY_CAT → distar.150`, verify the Distant Stars label and the 25% grant when Living Metal is already a research option. |

Use the existing object export for new directories. The server reads published MongoDB collections. Count a command once in each expanded execution path and use expansion history to identify its source. Exclude tooltip-only blocks, test events and definitions without a confirmed caller from gameplay rewards. Include executable `hidden_effect` blocks and random branches containing `add_tech_progress`. Other mechanisms, including `add_random_research_option`, `copy_random_tech_from`, `progress_all_researches` and debris, are outside this section. [Parser profile](../../../config/parser_sources.json) · [Loader profile](../../../config/loader.json)

## Server index and DLC

For each published input revision, build one index from technology ID to sources and branches. Build it on first access, publish the complete result and reuse it across RU, EN and DLC profiles. Concurrent requests share one build. A change to the inputs or rules requires a new build. Return preparation failures as errors so clients can distinguish them from technologies with no sources.

For each source, retain the gameplay object, action or option, recipient, branch conditions, amount or expression, confirmed DLC requirements and provenance addresses. Group different outcomes of the same action under one heading. Keep distinct gameplay actions separate even when they call the same effect. If a condition is only partially understood, indicate this in the description and record the details in diagnostics.

Extend `POST /api/trees/technology-tooltip` with a `research_progress` section. The card sends the language, technology ID and the applied DLC selection of the open tree. The server uses its existing localization function for names, options, conditions and DLC titles. The frontend renders the resulting groups.

**Keep sources visible when their required DLC is disabled.** Show the required DLC title next to its source, with an explicit “disabled” / «отключено» label when applicable. Put a branch-specific requirement next to the affected outcome. Preserve compound requirements, including alternatives between expansions. Derive the label from an entry or branch condition. A filename alone is insufficient evidence for a DLC requirement. Draft selection changes take effect after Apply.

## Resets in system settings

Every result the server persists in MongoDB or reuses in memory across requests belongs to a named reset operation and the overall reset. Clear its bookkeeping and dependent caches together with the result. Use an explicit list of server-owned results to define the scope of deletion. Preserve the loader export, localization, images and user settings.

| Button under System settings → Database operations | Result |
| --- | --- |
| Clear generated trees | Remove all generated trees and their registry entries. Release prepared tree inputs and the in-memory card catalog. The client closes the old tree. The next open builds it from scratch. Retain the separate progress index. |
| Reset research progress index | Remove the index and its server caches. Evict tooltip responses for both languages on the client. Preserve the current tree and viewport position. The next tooltip request triggers preparation. |
| Reset all generated data | Run both operations. Include each future type of generated data alongside its own reset operation. |

Finish the reset before any subsequent rebuild. Repeated resets of an empty result succeed. Coordinate resets with active operations using the existing HTTP 409 response for a busy tree as a precedent. A delayed response must not repopulate a cache after a successful reset. Report the outcome in the status panel. [Existing tree cleanup](TZ_REFERENCE_TREE_EN.md) · [Settings view](../../../Docs/frontend/TZ_FRONTEND_STAGE_11_EN.md)

## Publishing this stage to the test server

The next deployment of this stage requires a full reload of the `wiki` test database on `192.168.1.36`.

1. On the workstation with the game installed, prepare the complete loader input using the extended profile. Before dropping the database, check that artifacts exist for every configured source, including the ten additional directories and RU/EN localization with project strings.
2. Suspend requests to the test API and stop its instances. Record the DLC selections of previously built trees from the registry so they can be reopened after the import.
3. From the workstation, connect to MongoDB at `192.168.1.36` over TLS with the administrator’s X.509 certificate from Vault and run `dropDatabase` only on `wiki`. Then use the regular loader account for `sttv-loader create`, `load` and `verify`, passing `--config WEB_STTV/config/loader.json --profile network` each time. Load the entire export. [Loader commands](../../loader/README_EN.md)
4. Start the new API with empty application caches. Before the first request, verify that the old trees and progress index are absent. The database drop removes results persisted in MongoDB, and stopping all instances clears their process caches.
5. Reopen each recorded DLC selection and verify from the log that its tree was built against the new snapshot. If the registry was empty, open the reference tree with its default settings. Use the first tooltip request to verify a fresh index build and a second request to verify reuse.

The full database drop applies to this deployment. The Reset all generated data button continues to preserve the loader export.

## Acceptance

1. Check all base technologies in one snapshot. Compare IDs, sources, branches and amounts against grant sites, including nested calls. Document discrepancies. Check negative cases containing only `add_research_option`, a tooltip-only block or a test event.
2. Check the three Crystal-Infused Plating groups in RU and EN, both sleeping nest awards, the event option and the priority queue in `grand_archive.2410`. Also check a formula, a random branch, a non-event source and a technology with a long list.
3. Toggle a required expansion for a visible technology. The result stays the same until Apply. After applying, both profiles show the source and the label reflects the selection. For alternative requirements, cover the case where one of two DLCs is enabled.
4. Check the initial build, repeated hovers, two concurrent cards and an input revision change. Verify the build count or log and compare first and repeat request times on the same snapshot.
5. Exercise each button, repeated resets and the overall reset on test results. After an index reset, reopen the same card in RU and EN without a page reload. Check a delayed response, deferred rebuilds and the integrity of the source collections. After the overall reset, the tree and the index each rebuild on their next respective request.
