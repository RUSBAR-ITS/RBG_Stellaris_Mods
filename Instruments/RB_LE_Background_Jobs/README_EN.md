# Leader Editor former occupation catalogue

## Contents

- [Inputs](#inputs)
- [Build and verify](#build-and-verify)

## Inputs

The generator reads the approved [visibility decisions](../../docs/RB_LE/BACKGROUND_JOB_VISIBILITY_4_6_0_EN.csv), the [source registry](../../docs/RB_LE/BACKGROUND_JOB_VISIBILITY_SOURCES_4_6_0_EN.csv) and the installed Stellaris 4.6.0 definitions. The mod ships the resulting selection rules, button labels and occupation assignments. Review both tables against vanilla before generating for a new game version.

## Build and verify

From the repository root, use the Python environment prepared for [Stellaris Parser](../Stellaris_Parser/README_EN.md).

```powershell
python -B Instruments/RB_LE_Background_Jobs/build.py
python -B Instruments/RB_LE_Background_Jobs/build.py --check
python -B Instruments/RB_LE_Background_Jobs/verify.py
```

Both tools accept `--game PATH` and default to `E:/SteamLibrary/steamapps/common/Stellaris`. The `--check` option compares expected game scripts with their current contents. The verifier expands menu templates, matches each button to its assignment, checks navigation and verifies that vanilla supplies both English and Russian names. Worker eligibility and the displayed biography require in-game testing. [Test scenarios](../../docs/RB_LE/DOSSIER_MENU_REQUIREMENTS_EN.md#occupation-visibility-in-460)
