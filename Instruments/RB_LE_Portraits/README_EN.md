# Leader Editor portrait catalogue

## Contents

- [Build](#build)
- [Verification](#verification)

## Build

Run these commands from the repository root in the [Stellaris parser environment](../Stellaris_Parser/README_EN.md). The build targets Stellaris 4.6.0. It reads the installed game and writes four text files to `RB_LE/mod`. Players only need the generated definitions, menu scripts and localization.

```powershell
python -B Instruments/RB_LE_Portraits/build.py --game E:/SteamLibrary/steamapps/common/Stellaris
python -B Instruments/RB_LE_Portraits/build.py --game E:/SteamLibrary/steamapps/common/Stellaris --check
python -B Instruments/RB_LE_Portraits/verify.py --game E:/SteamLibrary/steamapps/common/Stellaris
```

The mod’s portrait definitions and layer selectors live under `gfx/portraits`. In `common/scripted_effects`, `rb_le_portrait_lookup.txt` identifies appearances and `rb_le_portrait_choices.txt` sets the sample parameters. The catalogue draws from vanilla species designer sets, regular robots and uplifted presapients. Leader and ruler rules determine the phenotypes for each gender. Controls list distinct DDS files in declaration order. Switching phenotype preserves shared assets and the selected eye colour for modern humans.

## Verification

Each full appearance has a separate graphics key. Its attachment and clothing selectors each provide one default DDS. The verifier compares these files with the installed game's ordered choices for every phenotype. It also checks the full-key readback and cyclic menu navigation.

The check expands button templates and counts nested scripted effects from each portrait screen. The initialization limit in Stellaris 4.6.0 is five. Selecting the phenotype and rendering it must each appear once across all expanded events, both in `rb_le.27`. This checks for the 0.0.10 startup regression. A game launch is a separate check.

`--check` compares all four files against a new in-memory build. `verify.py` parses the shipped definitions, checks references and ranges, and locates DDS files in the game and its archives. Vanilla lacks the attachment selectors for `mammalian_ar_02`, `_03`, `_07`, `_09` and `_10` with the `_hair` suffix. Two additional `bio7` stage masks are also missing. The [editor specification](../../docs/RB_LE/DOSSIER_MENU_REQUIREMENTS_EN.md#portrait-editor-prototype) includes the in-game checks.
