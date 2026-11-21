# Specification. Technology acquisition, card actions and technology pages

## Contents

- [Scope](#scope)
- [Three acquisition sections](#three-acquisition-sections)
- [Installed game survey](#installed-game-survey)
- [Card actions](#card-actions)
- [Technology page](#technology-page)
- [Data and acceptance](#data-and-acceptance)
- [Verification results](#verification-results)

## Scope

Approved. The three sections describe one base technology. The existing tree rules govern card order, parents and connections. Selection of a `technology_swap` is deferred. [Card specification](elements/TZ_TECHNOLOGY_CARD_EN.md) · [Tooltip content specification](TZ_TECHNOLOGY_TOOLTIP_CONTENT_EN.md)

## Three acquisition sections

Display the following sections after weight modifiers, in the order shown. Include a heading when the technology has a confirmed source for that section. A technology can have any combination of sections. Zero or missing weight, a starting-technology flag, regular research or a missing source do not establish a scripted reward.

| English heading | Russian heading | Evidence and content |
| --- | --- | --- |
| Unlocks the research option | Открывает технологию для исследования | `add_research_option` opens a research option. Identify the source, action and conditions that let the player choose the research. |
| Grants the researched technology | Сразу выдаёт изученную технологию | `give_technology` grants ownership. Identify the recipient and circumstances. |
| Grants research progress | Начисляет часть прогресса исследования | `add_tech_progress`. Reuse the existing groups, percentages, formulas, conditions and DLC labels. This heading replaces “Research progress”. |

Put each outcome in its respective section. An event can open an option on first discovery or grant progress if the option is already available. Preserve the condition for each branch. Describe a random selection as a possible outcome. A grant to another empire or a newly created NPC must not read as a reward for the player. Trace the definition to its caller and check the scope of the command. Exclude display-only effects, test events and cases with an unresolved target or recipient from confirmed player rewards. Record the reason for unresolved cases in diagnostics. [Source and DLC rules](../../src/server/Docs/TZ_TOOLTIP_RESEARCH_PROGRESS_EN.md)

## Installed game survey

The survey covers all 679 base IDs in snapshot 4.5.4 (1b4f), including hidden technologies. Named option commands target 301 technologies and direct grants target 339. The previous verification confirmed 1,359 progress branches across 315 technologies. All three mechanisms occur for 134 IDs. No matching command was found for 153. Counts for the two new sections include scripted grants to other empires. Eligibility for a player reward depends on the entry conditions and recipient.

The survey checked expanded objects in the current export. To identify additional sources, it searched 2,222 script files across `common`, `events`, `prescripted_countries` and `map`. Commands and references to libraries containing them identified 18 further files outside the export. Expanding these found named commands in seven additional directories:

- `common/country_focus/focus_rewards`, `common/federation_perks`, `common/specialist_subject_perks`, `common/tradable_actions`;
- `common/patrons` (patron definitions), `common/fallen_empires`, `common/solar_system_initializers`.

The 32 DLC ZIP archives checked contained no gameplay TXT files under the surveyed roots. The per-technology lists and command locations are in the reports for this run. [All technologies](../../../TMP/WEB_STTV/technology-acquisition-tooltips/reports/TECHNOLOGIES_EN.md) · [Command locations](../../../TMP/WEB_STTV/technology-acquisition-tooltips/reports/technology-acquisition.json)

## Card actions

| Action | Result |
| --- | --- |
| Hover or focus | Highlight connections according to the existing rules. Load details on an explicit open action. |
| Left click, Enter or Space | Open the base technology tooltip anchored to the card. The action also applies to base technologies with in-game variants. |
| Right click or keyboard context menu | Open the card menu with “Open technology page”. Selecting it opens the page in the current tab. The browser handles its usual context menu elsewhere. |
| Middle click | Open a direct link to the same technology in a new browser tab. Preserve the tree position in the original tab. |

The tooltip stays open as the pointer moves and supports scrolling long text. Escape, clicking outside or clicking the same card again dismisses it. Opening another card replaces the current tooltip. The menu and tooltip are mutually exclusive. Escape returns keyboard focus to the card. Other UI controls keep their respective tooltip interactions.

## Technology page

The base technology page is a standalone view in `views/`. Its content and navigation are defined in the [technology page specification](elements/TZ_TECHNOLOGY_PAGE_EN.md).

## Data and acceptance

The server maps sources to technologies, checks the recipient and provides localization. The page and tooltip use the same API response and shared rendering components. Opening a page by ID requires only the base technology details. Tree coordinates are unnecessary for that request.

Extend the existing progress index to cover all three commands. Track the revision of all relevant source collections. Apply the individual index reset and the global reset in system settings to all three sections. If a confirmed source is outside the MongoDB import profile, add the corresponding definitions to the parser and loader profiles first. The server reads published MongoDB documents.

1. Check every base ID, including those hidden in the selected tree. Count command occurrences, confirmed player paths and unresolved cases separately. Keep the source object, file and call site for every path. Recipient and condition checks can reduce the number of confirmed paths.
2. Check Ordered Retreat and Trinary Computing as random pre-FTL observation options. For Thruster Bio-Integration, check both the option after two research completions and the starting grant to beastmaster empires. Check the excavation and special project for the frozen-world and fossilization technologies. Distinguish the Living Metal option from its 25% grant. Compare RU and EN for a case with three sections and one with no sources.
3. Test all three mouse buttons, keyboard actions, dismissal and scrolling. Check that hover makes no detail request. Compare page and tooltip data with matching language and DLC settings. Test a direct link refresh, new tab, return to the previous tree position, unknown ID and reopening after reset. Confirm source collections remain intact.

## Verification results

The survey covers all 679 base technologies in snapshot 4.5.4. Each command occurrence has a file, source object and script branch. At least one source was confirmed for 478 technologies. All three sections appear for 92.

| Outcome | Command occurrences | Confirmed branches | Technologies with section |
| --- | ---: | ---: | ---: |
| Research option | 2,944 | 2,476 | 289 |
| Researched technology | 1,949 | 410 | 248 |
| Partial research progress | 1,359 | 1,259 | 298 |

Each confirmed branch retains its immediate source and conditions. When several earlier events lead to a call, each immediate caller is displayed with one verified path back to an entry point. The report records why a grant to another empire or an unresolved path was excluded. An absent section means that the survey confirmed no scripted reward of that type.

[Per-technology audit](../../../TMP/WEB_STTV/technology-acquisition-tooltips/reports/player-paths.json) · [Snapshot check](../../src/server/tests/acquisition_acceptance.py) · [Published API check](../../src/server/tests/acquisition_http_acceptance.py)

The deployment check compared the API sections for all 679 IDs after an index reset. Selected technologies were also checked in RU and EN with all DLCs explicitly disabled. The browser check compared the Living Metal page and tooltip, including both anomaly outcomes. [API results](../../../TMP/WEB_STTV/technology-acquisition-tooltips/reports/published-verification.json)
