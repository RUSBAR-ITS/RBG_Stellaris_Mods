# RB_LE 0.0.1 — opening a dossier from a leader card

## Contents

- [Prototype objective](#prototype-objective)
- [Leader card and event](#leader-card-and-event)
- [Passing the selected leader](#passing-the-selected-leader)
- [Verification and acceptance](#verification-and-acceptance)

## Prototype objective

Approved for implementation. Target Stellaris version — `v4.6.*`. The interface targets UI Overhaul Dynamic, Workshop ID `1623423360`.

Version 0.0.1 tests one interaction. The player opens a leader’s card on the right of the Leaders window, clicks Edit Dossier and sees that character’s name. The event is read-only. The interaction uses the card directly, without a planetary decision or a second leader picker.

## Leader card and event

Center Edit Dossier on its own row below the native assign and dismiss buttons. Extend the bottom edge of the card background to fit the row. Keep the portrait, biography and native controls at their existing sizes and positions. The ruler’s dossier can be opened independently of whether the ruler can be dismissed.

Use UI Overhaul Dynamic’s `interface/topbar_leaders_view.gui` as the layout baseline. For the inspected layout, the proposed height of `leader_portrait_background` increases from 705 to 770. The proposed button measures 300 × 60 at (87, 795), anchored to the `upper_right` of `topbar_leaders_view`. These are GUI units. Acceptance is based on placement on the player’s screen.

| Element | English text | Russian text |
|---|---|---|
| Card button | Edit Dossier | Редактировать личное дело |
| Event title | Dossier | Личное дело |
| Entire event description | `Name: <Selected leader’s name>` | `Имя: <Имя выбранного лидера>` |
| Only event option | Exit | Выход |

The description is a single line. Replace the angle-bracket placeholder with the character’s current display name. Exit closes the event in one click.

## Passing the selected leader

The click target is the actual leader object shown on the card at the time of the click. The hypothesis to test is whether an `effectButtonType` receives `leader` scope here. If confirmed, the handler passes that character reference to the event shown to the player. Event localization resolves the name, for example through `$NAME$: [event_target:rb_le_selected_leader.GetName]`. The Russian option must read «Выход» with vanilla Russian localization alone as well.

Vanilla’s `common/button_effects/example.txt` omits leaders from its documented list of button targets. The engine handles the native assign and dismiss buttons. If the script receives a country or a previously selected map object, record that as the test outcome. Substituting the ruler, using the selected fleet’s commander or looking up a leader by name fails the requirement. [Leader selection research](VANILLA_LEADERS_4_6_0_EN.md#selecting-a-leader-in-the-ui)

## Verification and acceptance

| Check | Expected result |
|---|---|
| Before launching the game | The GUI button is wired to its handler, the event has one option, and both localizations reference the same target. |
| Open the card of a non-ruler leader A and click Edit Dossier | One event opens. Its entire description reads `Name: <A’s name>`. Exit closes it. |
| Open another leader B, then return to A, opening the event each time | The event shows B and then A. |
| Select a fleet commanded by A on the map, then open the dossier of a different leader B | The event shows B despite the earlier fleet selection. |
| Open the ruler’s card | The event shows the ruler’s name and can open even when Dismiss Leader is disabled. |
| Inspect the card with UI Overhaul Dynamic at the player’s UI scale | The new button fits inside the background, sits below the native row and clears the biography. |

The binding is confirmed after the user verifies these cases in game. A matching name on the ruler’s card alone is insufficient for acceptance.
