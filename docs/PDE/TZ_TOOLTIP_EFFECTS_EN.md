# PDE deposit effects in tooltips

## Contents

- [Scope and presentation](#scope-and-presentation)
- [Effect sources](#effect-sources)
- [First verification](#first-verification)

## Scope and presentation

Approved supplement to the [PDE 2.0.0 specification](TZ_EN.md) for vanilla Stellaris 4.5.4. PDE 2.0.2 applies the verified pilot format throughout the menu. Direct production, resource upkeep, districts, jobs and conditional modifiers come from the vanilla definitions. The habitat bonus on an orbital deposit is labeled separately. A feature which only has clearance effects explicitly states that it has no direct production or persistent modifier.

On placement and removal buttons, display a **Feature effects** block after the name and full description. For an action in the [warning register](QUEST_TOOLTIP_WARNINGS_EN.md), keep the red warning on the first line, followed by a blank line. Describe what the feature provides while present on the selected body, keeping the sign of each effect in both menus. State the condition for a conditional bonus, including when the selected body does not meet it. For a modifier shared by multiple instances, explain how many times it applies.

## Effect sources

- For placement, preview the vanilla effect inside a `tooltip` block scoped to the saved PDE target. Use `add_deposit` for a regular feature and `add_blocker` with the real action’s blocking mode for a blocker. Vanilla uses both patterns in event options. [Feature example](E:/SteamLibrary/steamapps/common/Stellaris/events/colony_events_2.txt:2410) · [Blocker example](E:/SteamLibrary/steamapps/common/Stellaris/events/shroud_events.txt:3125)
- For removal, read feature properties from the vanilla definitions using the existing parser catalog. Where the native placement preview omits a condition or external modifier, use the same property line. Check the result against the definition, including inline scripts. Vanilla clearance rewards belong to `on_cleared` and are outside the instance’s properties.
- Use game localization keys for districts, resources, jobs and existing effect descriptions in both languages wherever their scope is available. Use supported substitutions for variable values. Take constants from the corresponding effect definition.

## First verification

| Deposit | What to verify on both buttons |
| --- | --- |
| `d_buzzing_plains` | The maximum number of generator districts increases by 1. [Definition](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_planetary_deposits.txt:1627) |
| `d_deep_sinkhole` | Total district cap −1. Also explain the conditional energy output bonus from biologists when `biologist_is_ranger_trigger` applies and check the bonuses from included scripts. Check display with and without the condition. [Definition](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_blocker_deposits.txt:451) |
| `d_titanic_life_blocker` | +8 monthly society research and −1 district capacity per instance. A separate shared modifier grants +25% society research from jobs. Check the wording with one and two instances. [Feature](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_blocker_deposits.txt:879) · [Modifier](E:/SteamLibrary/steamapps/common/Stellaris/common/static_modifiers/00_static_modifiers.txt:499) |

Use synthetic checks for RU/EN localization references, source values and isolation of the preview from the executed action. In game, compare both tooltips with the planet’s feature list. The removal button must describe the selected deposit’s properties. Check that it does not promise placement or clearance rewards and that each click still affects one instance.
