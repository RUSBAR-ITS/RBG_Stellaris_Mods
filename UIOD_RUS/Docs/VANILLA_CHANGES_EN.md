# UIOD_RUS — affected vanilla files and functions

## Contents

- [Version 0.0.4](#version-004)
- [Version 0.0.3](#version-003)
- [Overridden mod strings](#overridden-mod-strings)

## Version 0.0.4

- `common/scripted_effects/psionic_auras_scripted_effects.txt` (Stellaris 4.6.0). The patch overrides `desire_aura_max_intensity_effect` through the submod path `common/scripted_effects/uiod_psionic_auras_scripted_effects.txt`. Planets and arkships use `uiod_ascension_limit` as the limit and `uiod_rus_next_ascension_tier` for the new tier.
- `common/script_values/01_script_values_paragon.txt`. The vanilla `add_planet_ascension_tier` serves as the baseline for comparison. Its other callers use the original formula. The system cooldown remains defined in `common/inline_scripts/shroud/psionic_aura_definition.txt`.
- `common/technology/ui_tech_ascension_theory_repeatable.txt` belongs to Ascension Slots. UIOD_RUS replaces this file to remove the rejected `ai_update_type` field. The technology and the tier limit variable originate in submod `1890399946`.

## Version 0.0.3

No vanilla files, functions, or localization keys are affected. Vanilla game definitions, interfaces, and mechanics are not overridden.

Vanilla English localization and the prepared Russian texts are used only as terminology references. References to them are preserved in the shared glossary.

## Overridden mod strings

| Source | Original Russian file | Key count |
| --- | --- | ---: |
| UI Overhaul Dynamic (`1623423360`) | `localisation/ui_overhaul_qhd_l_russian.yml` | 12 |
| UI Overhaul Dynamic - Ascension Slots (`1890399946`) | `localisation/ui_overhaul_qhd-technology_l_russian.yml` | 7 |

The full list of keys and approved translations is in the [specification](TZ_EN.md#6-approved-translations). Overrides are stored in UIOD_RUS's own files; the Workshop originals are unchanged.
