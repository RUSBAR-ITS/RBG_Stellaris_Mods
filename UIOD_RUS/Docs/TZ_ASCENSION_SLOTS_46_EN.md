# UIOD_RUS — Ascension Slots patch for Stellaris 4.6

## Contents

- [Scope](#scope)
- [Instrument of Desire aura](#instrument-of-desire-aura)
- [Repeatable technology](#repeatable-technology)
- [Files and load order](#files-and-load-order)
- [Verification and acceptance](#verification-and-acceptance)
- [Optional second phase — colony ascension tier badges](#optional-second-phase--colony-ascension-tier-badges)

## Scope

Phase one is approved for UIOD_RUS 0.0.4. It covers the Instrument of Desire aura and the Ascension Slots repeatable technology (Workshop `1890399946`), based on the Stellaris 4.6.0 scripts and game log. Both fixes apply in every interface language. The [localization specification](TZ_EN.md) covers the Russian strings.

## Instrument of Desire aura

Use the single `desire_aura_max_intensity_effect` definition from the vanilla `common/scripted_effects/psionic_auras_scripted_effects.txt` as the baseline. Preserve the separate 4.6 branches for planets and ship colonies, their ownership and occupation checks, and the ground combat check in the branch where it applies. Each affected colony receives its own ten-year `recent_colony_aura_effect_triggered` flag. Preserve the count of successful increases, the message target and delivery to the aura owner via `recipient = root.aura_owner`, including in systems where the owner has no starbase.

In both branches, check the limit in `event_target:global_event_country.uiod_ascension_limit`. The existing Ascension Slots events calculate this variable. For each eligible colony below that limit, increase its current tier by exactly one. A colony at or above the limit keeps its tier, receives no flag and is excluded from the count.

Use a dedicated `script_value` with the `uiod_rus_` prefix, called only by this aura. The vanilla `add_planet_ascension_tier` formula in `common/script_values/01_script_values_paragon.txt` caps the result with `max = 10` and uses `trigger_scope = planet`. The `uiod_rus_next_ascension_tier` value reads the current object’s tier (`has_planetary_ascension_tier` in `this` scope) and adds one. Verify the tier readout in game on a planet and an arkship separately. The check before the increase enforces the limit. Other vanilla events continue using the original formula.

## Repeatable technology

Remove the `ai_update_type = all` line from `ui_tech_ascension_theory_repeatable`. The Stellaris 4.6.0 parser rejects this field. Preserve the original costs, prerequisites, research and AI weights, repeat limit, and the bonus of one ascension perk slot per completed level. Keep the submod’s existing slot settings and events.

## Files and load order

The following phase-one files are relative to UIOD_RUS.

| File | Purpose |
|---|---|
| `common/scripted_effects/uiod_psionic_auras_scripted_effects.txt` | Replaces the identically named Ascension Slots file containing the single aura definition. |
| `common/script_values/uiod_rus_ascension_values.txt` | Calculates the next tier for this aura. |
| `common/technology/ui_tech_ascension_theory_repeatable.txt` | Replaces the identically named Ascension Slots file with the corrected technology. |

Launcher order from top to bottom: UI Overhaul Dynamic → UI Overhaul Dynamic - Ascension Slots → UIOD_RUS. The two matching paths replace the submod’s files. The full vanilla file containing the other auras still loads. During implementation, update the UIOD_RUS target version to `v4.6.*`, its manifest, package file list, instructions and vanilla function inventory. When Ascension Slots updates, compare both overridden files with the author’s new versions.

## Verification and acceptance

1. Statically check the effective definitions under the specified load order. Diff the technology against the upstream file, compare the aura against both vanilla branches, resolve the new value reference, and verify that the package includes both existing Russian localization files.
2. In game, verify that `Unexpected token: ai_update_type` disappears from `error.log` and the game uses the patched effect. A duplicate vanilla aura key warning may still appear with a working patch.
3. Read the actual tier with `has_planetary_ascension_tier`. With a limit above 10, check 9 → 10 and 10 → 11 on a planet and an arkship separately. Verify that the increase stops at the configured limit, including a limit below 10. A colony already above the limit keeps its tier.
4. Test a second activation during the ten-year flag and an increase after it expires. Check the affected colony count, exclusion of foreign and occupied colonies, and delivery of the notification to a nomadic empire in a system where it has no starbase.
5. Test the technology with the Ascension Slots option enabled and disabled. When enabled, a completed level grants one slot. The user performs the in-game checks after implementation.

## Optional second phase — colony ascension tier badges

The UI Overhaul Dynamic colony window uses the vanilla `GFX_ascension_tier` sprite for its `ascension_tier_icon` widget. The sprite in `interface/icons.gfx` declares 11 frames in `gfx/interface/icons/leaders/leader_skill.dds`. The 209 × 22 pixel texture contains an empty outline followed by badges I–X. The window also has a separate `ascension_tier` label. Its `PLANET_ASCENSION_TIER` localization accepts the number via `$TIER|Y$`. The substitution alone does not establish whether the engine displays the label for tiers 11–100.

Phase two requires a separate decision. If work resumes, first test two distinct frames for tiers 11 and 100 in a dedicated atlas. This will establish whether the widget can select them and whether three digits are legible at 19 × 22 pixels while preserving the shared leader icon atlas.
