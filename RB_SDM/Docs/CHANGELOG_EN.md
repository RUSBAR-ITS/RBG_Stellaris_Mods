# RB_SDM changelog

## Contents

- [Version 0.0.1](#version-001)
- [Design draft of 22 November 2026](#design-draft-of-22-november-2026)

## Version 0.0.1

22 November 2026. Implemented the approved specification as a standalone mod for Stellaris v4.5.*. The planetary decision opens a demo catalog of 21 entries. Pages are packed after filtering and refreshed after selection. Each country has one session that retains its target and temporary selections until closed. Added the decision's AI switch and a hidden handler that selects the first available action. Added RU/EN localization and updated the author guide and navigation glossary.

Stellaris Parser expanded the packaged decision and events. Checks on the expanded scripts covered page boundaries, movement between pages, target loss, re-entry, cleanup, isolation between two countries and both AI modes. In a temporary 200-entry catalog, 89 available even IDs occupied 9 pages. In-game acceptance is pending. [Game package](../mod/) · [Acceptance cases](TZ_EN.md#acceptance)

## Design draft of 22 November 2026

Created the standalone RUSBAR Stellaris Dynamic Menu project. Added the specification and the guide to adding sections and entries. Documented packing pages after filtering, returning to the last remaining page, the 21-entry demonstration and acceptance cases for a 200-entry catalog. Started the vanilla change record. This iteration covers design documents. [Specification](TZ_EN.md) · [Author guide](../README_EN.md)

Added per-decision AI access to the design. The mod author selects the mode with a single trigger. Clarified how another event can open the same menu, described AI execution of the decision and added verification for both settings.
