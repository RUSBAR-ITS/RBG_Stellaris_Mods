# Leader Editor 0.0.4 — leader dossier

## Contents

- [Dossier fields](#dossier-fields)
- [In-game checks](#in-game-checks)

## Dossier fields

All four Personnel Department registers open the same dossier for the selected leader. The agreed screen supports English and Russian in Stellaris `v4.6.*`. Viewing a dossier preserves the character's data.

| Section | Details |
|---|---|
| Personal details | Name, age, years of service, the leader's own species and species class, type used by trait conditions, and current personal ethic. The character's species determines the organic or synthetic classification. |
| Background | Homeworld and its type when available, or the name of the mobile home colony. Former occupation has its own line. Hide the section if both entries are absent. |
| Training | Class, acquired specialization, base level, effective skill level when different, and current XP against the threshold for the next level. At the cap, display the standard maximum-level message. |

Optional fields appear when a value exists. Back returns to the originating register page. Exit closes the menu. The dossier is read-only.

Addition in 0.0.6. A separate line immediately after the name shows the selected leader's gender. The label and all three values use the active game localization.

## In-game checks

1. Compare the ruler's dossier from both registers with the vanilla leader card. Select a different character and check that their background, species, and ethic follow them.
2. For a leader partway through a level, compare both XP values with the vanilla tooltip. Check a leader with an effective skill bonus, one with equal levels, and one at the base level cap.
3. Check a synthetic, a gestalt leader without a profession, leaders with and without a specialization, and a leader from an ark if available. Check both languages, scrolling a long dossier, returning to the second register page, and exiting.
4. Open dossiers for leaders of different genders in succession. Check the line between name and age, including a character with `gender = indeterminable`.
