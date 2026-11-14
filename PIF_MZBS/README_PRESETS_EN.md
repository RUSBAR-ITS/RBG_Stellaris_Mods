# PIF - More Secondary Zones and Building Slots

Version: `1.0.0`  
Supported Stellaris version: `v4.3.7`  
Category: `Gameplay`

This is a PIF-compatible preset mod for increasing secondary zones and zone building capacity.

## Load order

```txt
Planetary Infrastructure Framework
PIF - More Secondary Zones and Building Slots
Optional UI compatibility mod
```

The mod must load after PIF so its PIF inline-script hook files replace the default PIF hook files.

## Default active configuration

| Preset type | Active default |
|---|---:|
| Secondary zone slots | 5 |
| Government zone building capacity | 24 |
| Main secondary zone building capacity | 12 |
| Resource / specialized zone building capacity | 24 |

## Preset categories

| Folder | Controls | Active target file(s) |
|---|---|---|
| `_presets/01_secondary_zone_slots/` | Number of secondary zone slots in supported main-like districts | `common/inline_scripts/pif/districts/<district>/zone_slots.txt` |
| `_presets/02_government_zone_capacity/` | `zone_default` building capacity | `common/scripted_variables/000_piz_01_government_zone_capacity_variables.txt` |
| `_presets/03_main_secondary_zone_capacity/` | Building capacity of main-district secondary zones | `common/scripted_variables/000_piz_02_main_secondary_zone_capacity_variables.txt` |
| `_presets/04_resource_zone_capacity/` | Building capacity of resource / specialized zones | `common/scripted_variables/000_piz_03_resource_zone_capacity_variables.txt` |

## How to switch presets

1. Open the mod folder.
2. Open `_presets/`.
3. Choose one preset from the category you want to change.
4. Copy the preset's `common` folder into the mod root.
5. Confirm file replacement.
6. Repeat for other preset categories if needed.
7. Restart the game.

Copy order between different categories does not matter because each category writes to different target files. Within the same category, the last copied preset is active.

## Example

To use 10 secondary zones, 48 buildings in the government zone, 18 buildings in main secondary zones, and 24 buildings in resource zones, copy these folders into the mod root:

```txt
_presets/01_secondary_zone_slots/10_secondary_zones/common
_presets/02_government_zone_capacity/048_buildings/common
_presets/03_main_secondary_zone_capacity/018_buildings/common
_presets/04_resource_zone_capacity/024_buildings_default/common
```

## Scripted variable load order

This mod intentionally stores capacity presets in files starting with `000_piz_`.

Stellaris scripted variables use the first declaration that is loaded. The preset files must be loaded before PIF's `pif_zones_building_capacity_variables.txt`, so the PIF variables are already taken when PIF reads its default values.

Expected duplicate-variable warnings, if present, must point to PIF files. If duplicate-variable warnings point to `000_piz_*` files, the preset did not load early enough.

## Zone slot behavior

Additional secondary zone slots reuse the existing final secondary slot type:

```txt
slot_city_02
slot_habitat_02
slot_resort_02
```

This follows the same pattern as existing working zone-slot expansion mods. These additional slots inherit the normal unlock rules of the repeated slot type.

## Troubleshooting


```txt
Documents/Paradox Interactive/Stellaris/cache
```

Manual preset changes may be overwritten by Workshop updates. For a permanent custom configuration, make a local copy of the mod and switch presets inside that copy.

## Existing saves and secondary zone count

Changing the number of secondary zones is strongly recommended for a new game.

Existing saves can keep old district-instance state. In such saves, already-built districts may show additional zone positions in the UI but may not allow selecting new zone specializations correctly. This is a Stellaris 4.x save-state limitation for already-created districts.

This mod does not recommend third-party save-fixer tools.

To return secondary zone behavior to the PIF baseline, delete this folder from this mod:

```txt
common/inline_scripts/pif/districts/
```

This removes only the secondary-zone-count override. Building-slot capacity presets remain active.

A separate vanilla preset for secondary zones is intentionally not included because the PIF baseline already provides the vanilla-style zone-slot setup.
