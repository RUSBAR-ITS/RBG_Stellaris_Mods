# Changelog

## 1.0.0
- Release

## 0.1.1

- Renamed capacity preset files to the `000_piz_*` prefix so scripted variable presets load before PIF defaults.
- Updated all active and preset capacity files to use the new `000_piz_*` filenames.
- Added troubleshooting notes for Stellaris cache issues when extra zone rows are visible but zone selection does not update.
- Added documentation for expected duplicate scripted variable warnings.
- Kept the repeated-slot expansion scheme unchanged.

## 0.1.0

- Initial PIF-compatible preset release.
- Added presets for secondary zone slots.
- Added presets for government, main-secondary, and resource/specialized zone building capacity.

## Documentation update

- Clarified that changing secondary zone count is strongly recommended for a new game.
- Documented safe rollback to PIF baseline by deleting `common/inline_scripts/pif/districts/` from this mod.
- Clarified that no vanilla secondary-zone preset is included because PIF already provides the baseline setup.
- Removed any recommendation to use third-party save-fixer tools.
