# Changelog

## 1.1.0

### Added

- Added 500 generated visual presets for **PIF - More Secondary Zones and Building Slots**.
- Added `_presets/PIF_More_Secondary_Zones_and_Building_Slots/` with one complete `interface/zz_bpv_planet_view.gui` per gameplay preset combination.
- Added `PIF_PRESET_INDEX.md` with naming rules, formulas, and all generated preset values.
- Added `VALIDATION_REPORT.json` for generated preset verification.

### Changed

- Updated `descriptor.mod` version to `1.1.0`.
- Updated `README.md` with PIF gameplay preset compatibility instructions.

### Preserved

- The active root `interface/zz_bpv_planet_view.gui` is intentionally unchanged from the previous active configuration.

## Unreleased

### Changed

- Updated visual spacing values in `zz_bpv_planet_view.gui`:
  - `@BPV_SECONDARY_ZONE_ENTRY_BOTTOM_PADDING = 2`
  - `@BPV_SECONDARY_ZONE_ENTRY_VERTICAL_GAP = 10`
  - `@BPV_MAIN_DISTRICTS_VIEWPORT_HEIGHT = 264`
  - `@BPV_MAIN_TO_LOWER_DISTRICTS_GAP = 10`
- Recalculated default derived geometry values:
  - `@BPV_MAIN_DISTRICT_CARD_HEIGHT = 891`
  - `@BPV_MAIN_DISTRICTS_SCROLL_CONTENT_HEIGHT = 891`
  - `@BPV_LOWER_DISTRICT_CARD_HEIGHT = 897`
  - `@BPV_LOWER_DISTRICTS_GRID_ROW_HEIGHT = 907`
  - `@BPV_LOWER_DISTRICTS_SCROLL_CONTENT_HEIGHT = 907`
- Updated every README calculation and preset block to use the new visual spacing values.
- Added a table of contents to `README.md`.
- Replaced incomplete preset starting values with full Vanilla, Expanded, and Huge preset calculation blocks in `README.md`.
- Added the layout safety rule that presets should scale vertically by rows and keep column counts fixed.
- Restored the detailed variable reference and default value descriptions in `README.md`.
- Reorganized `zz_bpv_planet_view.gui` header and active layout parameters.
- Removed the large in-code variable documentation block from the GUI file.
- Kept only short local notes near non-obvious derived layout values.
- Moved the full configuration guide and manual layout calculations to `README.md`.
- Added a testing checklist to `README.md`.
- Added a maintenance note explaining why `planet_district_entry_width_3` is intentionally not overridden.

### Preserved

- Existing UOD dependency model.
- Existing override scope: `planet_view`, `planet_district_entry_width_1`, `planet_district_entry_width_2`, and `zone_entry`.
