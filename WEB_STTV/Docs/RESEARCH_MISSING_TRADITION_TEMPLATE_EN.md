# Investigation of tr_purity_imperfection_remediation_wilderness

## Contents

- [Finding](#finding)
- [Reference chains](#reference-chains)
- [Diagnostic cause](#diagnostic-cause)
- [Verification boundaries](#verification-boundaries)

## Finding

Installed-game inspection dated 2026-11-15: the template file exists **without an extension** at [common/inline_scripts/traditions/tr_purity_imperfection_remediation_wilderness](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/traditions/tr_purity_imperfection_remediation_wilderness:1). No neighboring `.txt` version exists.

Complete contents:

```text
custom_tooltip_with_modifiers = tr_purity_imperfection_remediation_wilderness_tt
```

The reference is included in the definitions of three genetic tradition trees. Source code confirms these static connections; no basis was found to treat the path as merely an unused remnant. The earlier missing-template report refers to the requested `.txt` name, rather than the absence of any corresponding text.

## Reference chains

| Tree | Category membership | Tradition including the shared template |
| --- | --- | --- |
| Purity | [01_purity.txt:27](/E:/SteamLibrary/steamapps/common/Stellaris/common/tradition_categories/01_purity.txt:27) | [tr_purity_stage_3_swap:112](/E:/SteamLibrary/steamapps/common/Stellaris/common/traditions/01_purity.txt:112), call on line 118 |
| Cloning | [01_cloning.txt:25](/E:/SteamLibrary/steamapps/common/Stellaris/common/tradition_categories/01_cloning.txt:25) | [tr_cloning_stage_3_swap:172](/E:/SteamLibrary/steamapps/common/Stellaris/common/traditions/01_cloning.txt:172), call on line 178 |
| Mutation | [01_mutation.txt:26](/E:/SteamLibrary/steamapps/common/Stellaris/common/tradition_categories/01_mutation.txt:26) | [tr_mutation_stage_3_swap:95](/E:/SteamLibrary/steamapps/common/Stellaris/common/traditions/01_mutation.txt:95), call on line 100 |

All three include `traditions/tr_stage_3_tradition_swaps`. Its [lines 42–54](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/traditions/tr_stage_3_tradition_swaps.txt:42) contain:

```text
tradition_swap = {
    name = tr_purity_imperfection_remediation_wilderness
    inherit_name = no
    inherit_icon = no
    trigger = {
        is_wilderness_empire = yes
    }
    inline_script = {
        script = traditions/tr_purity_imperfection_remediation_wilderness
    }
    weight = {
        factor = 1
    }
}
```

The [is_wilderness_empire trigger:1804](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:1804) checks `has_origin = origin_wilderness`. An additional direct reference appears in [01_purity.txt:198](/E:/SteamLibrary/steamapps/common/Stellaris/common/traditions/01_purity.txt:198), inside a separate helper tradition with `possible = { always = no }`. That helper's restriction does not remove the three category chains above.

The tooltip key exists in [English localization:1375](/E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/biogenesis_l_english.yml:1375) and [Russian localization:1097](/E:/SteamLibrary/steamapps/common/Stellaris/localisation/russian/biogenesis_l_russian.yml:1097). Its text describes a `+5` maximum planet-size increase for `decision_wilderness_expand`; the discovered file only includes the tooltip, not the implementation of that increase.

## Diagnostic cause

During the initial check, our [loader](../src/backend/sttv/script/inlining/loader.py) appended the `.txt` extension from [inline_scripts.json](../config/parser/inline_scripts.json). It therefore requested the absent name and reported `missing_inline_template`. Following the next user request, a [separate exception configuration](../config/parser/exceptions.json) explicitly permits reading the discovered extensionless file. Other calls retain the `.txt` rule.

The vanilla [00_README.txt:33](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/00_README.txt:33) describes calls without an extension and maps its example to a `.txt` file. That example does not establish engine behavior for extensionless files. Alternative-name lookup and file renaming were not added in this iteration.

## Verification boundaries

Inspected category definitions, traditions, the shared template, origin trigger, the extensionless file itself, and corresponding localization keys. The discovered template contents also parsed successfully on their own. Game sources were not modified.

The investigation confirms static references and the cause of the previous loader failure. After connecting the explicit exception, all three tradition files parsed successfully: 75 calls expanded, four using the extensionless file. History and JSON checks passed. This changes reading behavior in WEB_STTV; engine loading and actual in-game tooltip display remain separately unverified.
