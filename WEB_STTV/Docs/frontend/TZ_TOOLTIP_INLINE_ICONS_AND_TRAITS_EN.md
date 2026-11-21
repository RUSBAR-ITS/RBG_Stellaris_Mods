# Specification. Inline icons and trait names in technology tooltips

## Contents

- [Icons in game text](#icons-in-game-text)
- [Leader trait names](#leader-trait-names)
- [Acceptance](#acceptance)

## Icons in game text

Across the test server responses for 679 base technologies in Stellaris v4.5.4, 18 technologies use seven distinct `£…£` markers. Deposit names contain icons in weight conditions. The Dyson Sphere and Matter Decompressor descriptions use resource icons within sentences.

Add the seven DDS files below to the loader configuration. The existing loader converts them to PNG and publishes them under their game-relative paths. For example, Rare Crystals uses `gfx/interface/icons/resources/rare_crystals.png`. [Loader configuration](../../config/loader_images.json) · [Publication rules](../../src/loader/Docs/TZ_IMAGE_UPLOAD_EN.md)

| Marker | Source relative to `gfx/interface/icons/` |
|---|---|
| `£energy£` | `resources/energy.dds` |
| `£minerals£` | `resources/minerals.dds` |
| `£rare_crystals£` | `resources/rare_crystals.dds` |
| `£exotic_gases£` | `resources/exotic_gases.dds` |
| `£volatile_motes£` | `resources/volatile_motes.dds` |
| `£sr_living_metal£` | `resources/sr_living_metal.dds` |
| `£blocker£` | `text_icons/text_icon_tile_blocker.dds` |

The game maps six of these markers explicitly in `interface/texticons.gfx`. For Living Metal, use the existing small resource DDS at the listed path. [Rare Crystals](E:/SteamLibrary/steamapps/common/Stellaris/interface/texticons.gfx:478) · [Planetary blocker](E:/SteamLibrary/steamapps/common/Stellaris/interface/texticons.gfx:578)

The shared game-text component replaces each recognized marker with an inline icon at its position in the string. Its size follows the font size. Preserve whitespace, numbers and nested text colors. For example, `£rare_crystals£ §Y+1§!` renders as the crystal icon followed by a yellow `+1`. The same rule applies to descriptions without color codes. Unknown or unclosed markers remain visible as written. [Game deposit string](E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/megacorp_l_english.yml:2899) · [Game-text component](../../src/frontend/ui/base/GameText.tsx)

## Leader trait names

Of the 36 distinct traits in base technology conditions, four have definitions in `wiki.traits` and lack dedicated RU and EN strings. They occur in 82 weight checks across 53 technologies. Add each of the four game IDs to both project localization directories using the reference and Roman numeral below. The server resolves the reference through the existing lookup in `wiki.localization` for the selected language. The trait's `TIER` parameter confirms the level. The game uses the same naming pattern for `leader_trait_maniacal_2`. [Game localization](E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/main_1_l_english.yml:4925) · [Localization sources](../../config/parser_sources.json)

| Game ID | Source string in both languages | Expected RU | Expected EN |
|---|---|---|---|
| `leader_trait_maniacal_3` | `$leader_trait_maniacal$ III` | Одержимость III | Maniacal III |
| `leader_trait_spark_of_genius_2` | `$leader_trait_spark_of_genius$ II` | Гениальность II | Spark of Genius II |
| `leader_trait_expertise_psionics_2` | `$leader_trait_expertise_psionics$ II` | Талант: псионика II | Expertise: Psionics II |
| `leader_trait_expertise_psionics_3` | `$leader_trait_expertise_psionics$ III` | Талант: псионика III | Expertise: Psionics III |

## Acceptance

1. Verify that all seven published PNGs decode. In the browser, open the conditions for `tech_mine_rare_crystals` and `tech_mountain_range`, then the description of `tech_dyson_sphere`. Check the crystal, blocker and energy icons, inline positioning, number color and scaling.
2. Exercise the shared component with text containing no color codes, multiple icons in one line, nested colors, and unknown or unclosed markers.
3. Compare API responses for the four IDs with the table in RU and EN. On the same dataset repeat the check for all 391 occurrences of `has_trait` across 98 technologies. In the browser, check both psionics traits on `tech_psionic_theory` and the Maniacal III and Spark of Genius II traits on `tech_arkship_exodus_jump` with DLC enabled.

[Русская версия](TZ_TOOLTIP_INLINE_ICONS_AND_TRAITS_RU.md)
