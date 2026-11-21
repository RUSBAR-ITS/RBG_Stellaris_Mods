# WEB_STTV server. Phrase dictionary for technology tooltips

## Contents

- [Dictionary scope](#dictionary-scope)
- [Game conditions](#game-conditions)
- [Scopes and general checks](#scopes-and-general-checks)
- [Logic, weight and arguments](#logic-weight-and-arguments)
- [Game names](#game-names)
- [Acceptance](#acceptance)

## Dictionary scope

**The game conditions section is implemented.** Published 89 RU/EN string pairs for 70 conditions, including negative forms for origin and authority. For example, `has_technology` uses the key `sttv_tooltip_has_technology` and two templates, «Исследована технология „{technology}“» and “Has researched the technology ‘{technology}’”. The existing localization lookup supplies the name. One entry covers all technologies. [Russian strings](../../../localization/russian/sttv_tooltip_conditions_l_russian.yml) · [English strings](../../../localization/english/sttv_tooltip_conditions_l_english.yml)

Both project directories are in the localization profile. The `tooltip_condition` context forms the key from the construct name. Boolean `no` uses the `_no` suffix. The `has_trait` check has separate `_species` and `_leader` labels. When composing a phrase, the caller selects the relevant variant and fills its named parameters. In numeric templates, `{comparison}` is the comparison operator, `{value}` is the value and `{percentage}` is a formatted percentage including its sign. [Tooltip content specification](../../../Docs/frontend/TZ_TECHNOLOGY_TOOLTIP_CONTENT_EN.md)

**The list below comes from MongoDB.** The survey covered all 679 documents in `wiki.technologies`. It selected all occurrences of the root fields `prerequisites` (505 technologies), `potential` (376), `allow` (0) and `weight_modifier` (555) in each base technology. Recursively traversing their expanded trees produced **121 distinct assignment keys**. Root section names, logical nodes and scalar arguments are counted separately. The sample covers base technologies before DLC filtering.

## Game conditions

The following **70 keys** need wording for what the game checks. Related checks can share a template. For example, `has_seen_any_bypass` describes discovering a bypass, while `owns_any_bypass` describes owning one.

| Group | Game keys |
|---|---|
| Research and progression | `has_technology`, `can_research_technology`, `has_tradition`, `has_ascension_perk`, `has_crisis_level`, `has_menace_perk`, `num_ascension_perk_slots` |
| Empire setup and DLC | `host_has_dlc`, `has_origin`, `has_authority`, `has_civic`, `has_valid_civic`, `has_ethic`, `has_ai_personality`, `is_ai`, `is_country_type`, `is_nomadic`, `uses_ship_category` |
| Species, population and leaders | `has_trait`, `is_archetype`, `has_dna`, `is_same_species`, `is_sapient`, `has_citizenship_type`, `has_slavery_type`, `is_pop_category`, `count_owned_pop_amount`, `is_councilor`, `is_councilor_type`, `is_ruler`, `has_base_skill` |
| Diplomacy, federation and community | `has_communications`, `num_communications`, `perc_communications_with_playable`, `has_federation`, `has_federation_law`, `has_federation_perk`, `is_galactic_community_member`, `is_active_resolution`, `is_subject`, `has_active_specialization` |
| Planets, resources and construction | `num_owned_planets`, `is_planet_class`, `has_deposit`, `has_deposit_for`, `has_district`, `uses_district_set`, `num_districts`, `num_zones`, `num_buildings`, `has_resource`, `resource_expenses_compare`, `has_megastructure`, `has_starbase_size`, `count_starbase_sizes` |
| Time, galaxy exploration and bypasses | `years_passed`, `mid_game_years_passed`, `days_passed`, `num_cosmic_storms_encountered`, `is_astral_scar`, `is_inside_nebula`, `count_archaeological_site`, `is_site_completed`, `has_relic`, `has_seen_any_bypass`, `owns_any_bypass` |
| Flags and modifiers | `has_policy_flag`, `has_country_flag`, `has_global_flag`, `has_modifier` |

## Scopes and general checks

Another **27 keys** determine whose state is checked, how many objects must meet a condition or how to interpret the result. For Titans, `any_neighbor_country` and `has_technology` together read “At least one neighbouring empire has researched Titans.” [Game example](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:236)

This section is implemented. Published **28 string pairs** for all 27 keys, including both forms of `always = yes/no`. Quantifiers and scope changes label groups. Read each label with its child checks in nesting order. For example, `federation → any_member → has_technology` means that at least one member of that federation has researched the technology. Look up `sttv_tooltip_space_owner?` directly, with its question mark, for the owner of the system’s territory if there is one. [Russian strings](../../../localization/russian/sttv_tooltip_scopes_l_russian.yml) · [English strings](../../../localization/english/sttv_tooltip_scopes_l_english.yml)

For `exists` and `is_same_value`, `{target}` names the object being tested. For `calc_true_if`, `amount` supplies `{comparison}` and `{value}`. The other children are the conditions being counted. For example, `tech_fe_affluence_1` requires at least four of the listed conditions to hold. [Game example](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_fallen_empire_tech.txt:157)

| Group | Game keys |
|---|---|
| Object quantifiers | `any_agreement`, `any_country`, `any_member`, `any_neighbor_country`, `any_owned_leader`, `any_owned_nonprimary_starbase`, `any_owned_planet`, `any_owned_pop_group`, `any_owned_species`, `any_planet_within_border`, `any_relation`, `any_system_megastructure`, `any_system_planet`, `any_system_within_border` |
| Scope changes | `federation`, `founder_species`, `owner`, `owner_species`, `prev`, `solar_system`, `space_owner?`, `species`, `this` |
| General and compound checks | `always`, `exists`, `is_same_value`, `calc_true_if` |

## Logic, weight and arguments

Published **27 RU/EN string pairs** for logical groups, branches and operations, bringing the dictionary to **144 pairs**. It distinguishes a direct `weight_modifier.factor`, a conditional `modifier.factor` and a calculation inside a `script_value`. Additive changes keep their sign and a zero multiplier is shown as ×0. Each logical group has a localized heading ending in a colon. [Russian templates](../../../localization/russian/sttv_tooltip_expressions_l_russian.yml) · [English templates](../../../localization/english/sttv_tooltip_expressions_l_english.yml)

Fourteen arguments take their meaning from the enclosing check or operation. For example, `type` fills `{resource}` in `has_resource` and `{building}` in `num_buildings`. The comparison operator comes from the quantity assignment. The councillor-level label for `complex_trigger_modifier` requires `trigger = get_councilor_level`, `trigger_scope = owner`, `mode = add` and a council position in `parameters.type`. Other shapes are reported with their original expression. [Argument and operation mappings](../sttv_server/tooltip_expressions.py)

The remaining **24 keys** help compose expressions. For example, conditional `factor = 0` means “multiply the weight by 0”. The expression `has_resource = { type = minor_artifacts amount > 0 }` describes a single resource amount check. Its `type` identifies a resource. Inside `num_buildings`, the same key identifies a building.

| Group | Game keys |
|---|---|
| Condition structure | `if`, `else`, `limit`, `hidden_trigger` |
| Modifier block and arithmetic | `modifier`, `factor`, `add`, `base`, `mult`, `complex_trigger_modifier` |
| Arguments of a particular check or expression | `amount`, `count`, `country`, `disabled`, `in_construction`, `mode`, `parameters`, `resource`, `ship_category`, `starbase_size`, `trigger`, `trigger_scope`, `type`, `value` |

Account for the following features of the expanded trees when composing phrases.

- **Logic.** Explicit `AND`, `OR`, `NOT` and `NOR` occur in the sample. Adjacent prerequisites imply AND. Preserve nesting and the scope of negation. Exercise `NAND`, included in the content specification, with a synthetic case. The observed assignment operators are `=`, `<`, `>` and `>=`. Preserve the distinction between `yes` and `no`. [Logic and context](../../../Docs/semantics/LOGIC_AND_CONTEXT_EN.md)
- **Conditions and labels.** Checks inside `hidden_trigger` are active. The selected sections contained no `custom_tooltip`. Its text and child conditions are distinguished in the existing description. [Tooltip semantics](../../../Docs/semantics/TOOLTIPS_EN.md)
- **Calculations.** The sample contains 36 `script_value` nodes including nested expressions, and 28 `scripted_trigger_test` nodes that compare a result. The formula `trigger = get_councilor_level` needs wording for the councillor’s level. Show a direct multiplier for the entire block, conditional multiplication and addition with the original values and in source order. Describe a dynamic multiplier by its formula or known dependency. [Game formula](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/technologies/cosmic_storms_technologies_weight_modifiers.txt)

## Game names

- The survey found **316 distinct scalar technology IDs** in `prerequisites`. Resolve their names in the `technology_name` context. Use verified game keys for origins, ethics, traditions and other named objects. Use the DLC title lookup from game settings. [Server localization](TZ_LOCALIZATION_API_EN.md)
- `has_policy_flag` takes three values in the sample, `robots_outlawed`, `ai_outlawed` and `slavery_allowed`. Find the policy and option by `option.policy_flags` in `wiki.policies`. For `gateway`, `lgate`, `relay_bypass` and `wormhole`, read the localization key from `wiki.bypass.name`. [Verified mappings](../../loader/Docs/TZ_POLICIES_AND_BYPASS_EN.md)
- A technical flag can be shown with its full ID, for example “The empire has the `crystal_armor_1_weight` flag”. Preserve the type and ID for a missing label and report candidate matches for an ambiguous reference. Preserve the expression and child conditions for an unknown construct.

## Acceptance

1. Check both languages against the published set and verify that template parameters match. A repeat scan must report new or unhandled constructs with their section and an example technology. Identify technical representations in the report. The current snapshot provides the baseline.
2. For `tech_titans`, check the alternatives, host DLC, inclusive 100-year limit and ×10 for a neighbouring empire. For `tech_mega_engineering`, check the mandatory technology between two OR groups and the direct ×0.25 multiplier. For `tech_synthetic_leaders`, distinguish the Necrophage origin and species trait as two conditions for ×0.33.
3. Check **+5** for a flag in `tech_crystal_armor_1`, and the computed multiplier and **×0** in `tech_storm_manipulation`. Check both languages for the policy and option setting `robots_outlawed` and the name of `relay_bypass`. Exercise root `allow`, an unknown nested node and an ambiguous flag synthetically. HTTP and presentation belong to the tooltip assembly stage.
