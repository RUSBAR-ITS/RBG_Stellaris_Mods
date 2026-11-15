# Stellaris — script syntax description

## Contents

- [Status and evidence](#status-and-evidence)
- [Text, comments and strings](#text-comments-and-strings)
- [Operators](#operators)
- [Special symbols](#special-symbols)
- [Values and variables](#values-and-variables)
- [Construct types](#construct-types)
- [Includes, templates and calls](#includes-templates-and-calls)
- [References and scopes](#references-and-scopes)
- [Order and context](#order-and-context)
- [Structural overview](#structural-overview)
- [Unestablished boundaries](#unestablished-boundaries)
- [Sources](#sources)

## Status and evidence

Date: 2026-11-15. Source version: **Stellaris Cygnus v4.5.4 (1b4f)**. This document builds on the [complete `common/` and `events/` research](RESEARCH_SCRIPT_PATTERNS_EN.md), covering 2,238 `.txt` files, and documentation shipped inside those directories.

This is a reference for discussion, not a parser specification or a change to the active profile. Examples illustrate forms; demonstration identifiers are not proposed as new game commands. Completeness for the closed-source engine language is not claimed.

Evidence statuses:

- **Code**: the construct occurs outside comments and prose instructions.
- **Documentation**: shipped instructions describe the capability; actual usage or all execution details may remain unconfirmed in script.
- **Unestablished**: observations do not justify a general rule; the occurrence is kept separate from established forms.

Documentation helps explain constructs but is not an exhaustive list. Absence of a mention is not a prohibition. Disagreements with code are recorded; commentary does not replace implementation evidence. Object and scripted-function names belong to extracted catalogs, not the grammar.

## Text, comments and strings

| Element | Rule and observation |
|---|---|
| Encoding | All researched `.txt` files decode as UTF-8, with or without a BOM. This characterizes the corpus, not all encodings accepted by the engine. |
| Separators | Spaces, tabs and line breaks separate elements outside strings. Brackets determine nesting; indentation does not. |
| Comment | `#` begins a comment to the end of the line outside a string. Comments may contain arbitrary bracket and command examples. |
| String | Double quotes: `"text"`. Preserve the complete content, including spaces and line breaks. The corpus contains 21 multiline strings and quoted keys. |
| Apostrophe | Can occur in an unquoted name, such as `TOX1_FLEET_Avogadro's_Moles`; observations do not identify it as an alternative string delimiter. |
| Case | Preserve source spelling. The coexistence of `root`, `ROOT` and `This` in different contexts does not establish universal case insensitivity. |
| Entry termination | Observed forms require no `;` or commas between elements. Multiple entries can occupy one line. |

Brackets and operator-like symbols inside a string do not form the outer script structure. A string can contain a name, path, text or deferred code fragment. Finding `{ ... }` inside it is not sufficient reason to convert it into a block.

Escaping depends on the processing layer. Code contains `log = "... \\[This.GetName]"`; scripted effect/trigger documentation separately describes escaping text substitutions (S2, S8). This does not justify automatically decoding every string according to JSON or Python rules. Preserve the original backslashes.

## Operators

**Key/value association and comparisons: the complete set found in active corpus text:**

| Form | Purpose | Status |
|---|---|---|
| `=` | Associates a key with a value or block; its precise meaning in a condition depends on the command | Code |
| `<` | Less-than comparison in a supporting context | Code |
| `>` | Greater-than comparison | Code |
| `<=` | Less-than-or-equal comparison | Code |
| `>=` | Greater-than-or-equal comparison | Code |
| `!=` | Inequality check in a supporting context | Code |

`=` cannot universally mean mathematical equality: `name = value`, `has_trait = trait_x` and a numerical condition are different domain operations. An operator's presence in the grammar does not make it valid for every field.

**Inside `@[ ... ]` and `@\[ ... ]` formulas:**

| Form | Purpose | Evidence |
|---|---|---|
| `+`, `-` | Addition and subtraction | Code and S2 |
| `*`, `/` | Multiplication and division | Code and S2 |
| `%` | Remainder | S2; absent from the 74 active formulas |
| `( ... )` | Expression grouping | Code and S2 |
| `\| ... \|` | Absolute value | Form observed in code; meaning documented in S2 |

S2 describes ordinary mathematical precedence, including multiplication before addition. Exact engine precision and all edge cases were not established. Outside a formula, `-` can belong to a negative number or name, and `/` to a path; the character alone does not establish arithmetic.

**Named operations:** `AND`, `OR`, `NOT`, `NOR` and `NAND` occur as logical block names. They use `NAME = { ... }`, rather than distinct lexical punctuation. `if`, `else_if`, `else`, `switch`, `while`, `limit` and `random_list` are also named constructs whose meaning depends on their location.

S4 lists numerical commands `set`, `weight`, `add`, `subtract`, `factor`, `mult`, `multiply`, `divide`, `modulo`, `round_to`, `max`, `min`, `pow`, `round`, `ceiling`, `floor`, `abs`, `square`, `square_root`. They use ordinary entry syntax. This documented list is neither another set of syntax operators nor a universally available command set.

Standalone `==`, `&&`, `||` operators and a single `?=` operator were not found. Observed `owner? = { ... }` consists of a name ending in `?` followed by a separate `=`. The `!` in `[[!PARAM]` belongs to conditional fragments, not a universal prefix-negation operator.

## Special symbols

| Symbol or wrapper | Role | Context |
|---|---|---|
| `{ ... }` | Nested container | Block, list or anonymous record |
| `" ... "` | String token | Value or key |
| `#` | Comment | Outside a string |
| `@NAME` | Script constant definition or reference | Left or right side of `=` |
| `@[ ... ]` | Formula | One value |
| `@\[ ... ]` | Formula spelling in parameterized scripts | Code and S2 explanation |
| `$NAME$` | Parameter substitution | Key, value, part of a name, string or fragment |
| `$NAME\|fallback$` | Parameter with a default | Parameterized text |
| `[[NAME] ... ]` | Conditionally included fragment | Parameterized script |
| `[[!NAME] ... ]` | Negative condition variant | Parameterized script |
| `.` | Part of a scope chain or identifier | `root.owner`, `assimilation.40`; also part of `0.5` |
| `:` | Reference prefix separator | `event_target:target`, `value:formula` |
| `?` | Observed scope-transition suffix | `owner?`, `colony.controller?` |
| `\|` | Argument/default separator or absolute-value delimiter | Meaning depends on the wrapper |
| `@` inside a name | Part of a composite name associated with a scope | `violation_of_equal_standing@prev.owner` |
| `/` | Path separator or division | Inline-file path or formula |
| `\` | Escaping at the relevant processing layer | Formulas and text substitutions; preserve literally |
| `[This.GetName]` | Text substitution | String content, not a script list |

A character has no single meaning independent of its enclosing construct. For example, `@cost` and `flag@root` belong to different families; formula `|` and `$PARAM|0$` need different handling.

## Values and variables

A scalar is one token or an entire formula. The corpus contains integers, decimals, negative values, `yes/no`, unquoted names and strings. Token category does not always establish domain type: `1` may be a weight, tier or numerical branch key; `name = some_key` may reference localization.

Distinguish three mechanisms:

| Mechanism | Example | Meaning |
|---|---|---|
| Script value with `@` | `@cost = 100`, then `cost = @cost` | A value declared in files; shared declarations also reside in `common/scripted_variables/` |
| Template parameter | `$COST$`, `$COST\|100$` | Substitution from a call or the specified default |
| Game-state variable | `set_variable = { which = progress value = 10 }` | An effect sets a value in game context; this does not declare `@progress` |

Inside a formula, a script constant can be referenced without `@`: `@[ count * 2 ]` (S2 and code). Game-state variable references can use `owner.capital_scope.my_variable` (S3). An arbitrary unquoted name cannot automatically be treated as an unknown constant or evaluated from one file.

If a declaration is unavailable, preserve the reference and its source. Precedence between conflicting declarations in different files and exact resolution timing were not established by this research.

## Construct types

| Form | Example |
|---|---|
| Scalar entry | `tier = 3` |
| Nested named block | `potential = { is_machine_empire = yes }` |
| Scalar list | `category = { biology }` |
| List of anonymous records | `entries = { { key = a value = b } { key = c value = d } }` |
| Mixed container | `prerequisites = { tech_stingers OR = { tech_mauler_growth_1 tech_weaver_growth_1 } }` |
| Empty block | `potential = { }` |
| Numerical key | `random_list = { 10 = { ... } 90 = { ... } }` |
| Tagged color value | `atmosphere_color = hsv { 0.50 0.2 0.8 }` |
| Color entry in a list | `rgb { 142 188 241 }` |
| Standalone marker | `optimize_memory` inside a scripted effect/trigger |
| Standalone parameter | `$TRIGGER$` between ordinary entries |
| Conditional fragment | `[[PARAM] add_resource = { energy = $PARAM$ } ]` |

Braces alone do not distinguish objects, lists and condition groups. Lists may contain named nested groups. Color blocks have three or four components; a universal three-value restriction would contradict this corpus.

A file root is a sequence. Technologies are usually named by definition keys; events may repeat `country_event = { id = ... }`; tag files contain bare names; anonymous root blocks also occur. A `.txt` extension does not guarantee a script: prose documentation exists.

## Includes, templates and calls

**`inline_script` includes file content.** Preserve the code spelling, `inline_script`. S1 describes paths relative to `common/inline_scripts/`, without the `.txt` extension.

```text
inline_script = "ai/hull_preference_weight"

inline_script = {
    script = ai/weapon_preference_weight
    WEAPON_TYPE = weapon_type_energy
}
```

Both forms occur in `common/technology/00_eng_tech.txt` (lines 497 and 333). In block form, `script` identifies the included file; other fields supply parameters. S1 warns that inclusion is not supported in every context. This commentary does not automatically establish a complete allowed-context table.

**Scripted triggers and scripted effects call named definitions.** The name comes from `common/scripted_triggers/` or `common/scripted_effects/`, not the calling file's path. S2 describes `example_effect = yes` and `example_effect = { PARAM = value }`. Code also calls scripted triggers with `no`, such as `species_rights_robot_full_rights_check = no` in S8. This is a condition value, not a parameter named `no`.

**Script values reference computed definitions.** S4 describes `value:my_value` and its argument form:

```text
value:my_value|PARAM1|value1|PARAM2|value2|
```

Preserve name/value pairs, including the trailing `|`. An actual example occurs in `common/artifact_actions/artifact_actions.txt:1052`. Script values use the same parameter and conditional-fragment family; they do not include a file by path.

**Text substitution and conditional inclusion.** `$PARAM$` can replace part of a name (`"$PARAM$_flag"`), a key, value or multiple entries. S1 explicitly describes code passed as a string, confirmed by multiline parameters in `common/buildings/01_pop_assembly_buildings.txt:1131`.

According to S2, `[[PARAM] ... ]` includes its fragment when the parameter is supplied and not `no`; `[[!PARAM] ... ]` applies when absent or `no`. Both forms occur in source code. This is a parameter-substitution condition and cannot automatically be replaced with game-state `if = { limit = ... }`.

**Similar names with different purposes:**

| Form | Established context |
|---|---|
| `include`, `included_building_sets`, `included_zone_sets` | Allowed buildings/zones and their sets, not file-reading directives. S5 and `common/zones/00_zones.txt:34`. |
| `scripted_action = some_id` | Reference to an action definition from a ship component; S6. |
| `injected_modifier = { ... }` | Weapon-component field containing a modifier, duration and stacking settings; `common/component_templates/00_weapons_energy.txt:1280`. |

One explicit general script-file inclusion command is confirmed in this corpus: `inline_script`. Other reuse mechanisms are described separately; this is not a claim that the entire engine has no other capabilities.

## References and scopes

| Kind | Example | Distinction |
|---|---|---|
| Object identifier | `has_technology = tech_synthetic_workers` | The field/command determines the destination catalog; no prefix is required |
| Event identifier | `id = assimilation.40`, `namespace = assimilation` | The dot belongs to an event identifier and need not be a scope transition |
| Scope chain | `root.owner`, `prev.owner`, `owner.capital_scope` | Requires the current context and known transitions |
| Saved target | `event_target:target_planet` | Target saved by a corresponding effect, not a file path |
| Computed value | `value:my_value` | Definition in `common/script_values/` |
| Numerical trigger value | `trigger:pop_amount` | Mechanism described in S3; the trigger must support it |
| Modifier value | `modifier:pop_citizen_happiness` | Read a context-dependent value, S3 |
| Composite reference | `owner.capital_scope.trigger:pop_amount` | Scope transition followed by specialized access, S3 |
| Composite name with `@` | `violation_of_equal_standing@prev.owner` | Observed in flag assignment; not a script constant `@name` |
| Text reference | `[This.GetName]` inside a string | Separate text interpretation; the outer string remains one token |
| Localization or graphical resource name | Values of `title`, `desc`, `icon` | The field establishes meaning; not all strings reference localization |
| File reference | `ai/hull_preference_weight` in `inline_script` | Resolved relative to the include directory according to S1 |

`this`, `root`, `prev`, `from` and their chains occur in code, but availability and precise meaning depend on the current scope. A single initial scope cannot be assigned to all of `common/` or every event.

Forms ending in `?` occur in transitions (`owner?`, `event_target:arkship.leader?`) and are recorded as a distinct spelling feature. Complete missing-target semantics and equivalence of spellings with and without whitespace are not proven here.

Composite names containing `@` occur in `common/scripted_effects/first_contact_dlc_effects.txt:3598` and `:3778`. Context suggests association of a flag name with a scope; the exact internal name-generation algorithm cannot be derived from these texts.

## Order and context

- Preserve entries in sequence, including repeated keys. A dictionary replacing earlier values with the last value is not a universal container model.
- Preserve original spelling, quotes, operators, formula and conditional boundaries, and source coordinates. Sorting commands may change meaning.
- Distinguish structural reading, parameter/include expansion and domain interpretation. A brace block alone does not identify a condition, effect or object data.
- Field names are not global contracts: `modifier`, `trigger`, `value` and `id` occur in different contexts.
- Observing a form does not prove validity in every scope; its absence from a selected directory does not establish a prohibition.

Further design will separately need decisions about reference resolution, include cycles, definition conflicts and unknown constructs. This document describes syntax and evidence, without selecting product behavior for those cases.

## Structural overview

This abbreviated outline describes observed forms, not a formal engine-language specification. Here `*` means repetition in the outline, rather than a game-text operator; `|` between alternatives is selection notation.

```text
document    := entry*
entry       := assignment | scalar | block | color_block | conditional
assignment  := key operator value
key         := atom | quoted_string
operator    := "=" | "<" | ">" | "<=" | ">=" | "!="
value       := scalar | block | color_block
scalar      := atom | quoted_string | formula
block       := "{" entry* "}"
color_block := color_tag block
color_tag   := "rgb" | "hsv"
formula     := "@[" expression "]" | "@\[" expression "]"
conditional := "[[" parameter_name "]" entry* "]"
             | "[[!" parameter_name "]" entry* "]"
```

Confirmed color forms are `field = rgb/hsv { ... }` and standalone `rgb { ... }` in color lists. The outline does not assert every combination valid everywhere. `atom`, `quoted_string` and `expression` are deliberately not finalized into regular expressions or evaluation rules. Parameters may occur inside atoms/strings or occupy a complete entry.

## Unestablished boundaries

- `trait_bg_active_glow { ... }` without `=` in `common/named_colors/01_trait_colors.txt:65` is an isolated questionable entry. It does not establish arbitrary named blocks without operators.
- `%` and some numerical operations are documented; their complete set and execution were not verified by running the game.
- Exponent notation, universal case/escaping rules and resolution of identical names remain unestablished. Missing examples should not become claimed engine prohibitions.
- This research does not describe `.gui`, `.gfx`, localization YAML, ODS, CSV or other formats as separate languages.
- These rules do not replace game-condition evaluation or imply that all expressions can be evaluated without save-game state.

## Sources

Paths below are relative to `E:/SteamLibrary/steamapps/common/Stellaris/`. A colon introduces the starting line of an explanation or example; instructions were read with surrounding context.

| ID | Source | Coverage |
|---|---|---|
| S1 | `common/inline_scripts/00_README.txt:33`, `:76`, `:85` | Include paths, string parameters, context restrictions |
| S2 | `common/scripted_effects/99_advanced_documentation.txt:13`, `:23`, `:37`, `:40`, `:89`, `:95` | Calls, defaults, conditional fragments, formulas |
| S3 | `events/000_how_to_use_variables_in_script.txt:13` | Scopes, state variables, trigger and modifier references |
| S4 | `common/script_values/00_script_values.txt:8`, `:52` | Numerical commands, script-value parameters |
| S5 | `common/zones/99_HOW_TO_ZONE.txt:102` | Domain meaning of `include` and building sets |
| S6 | `common/scripted_actions/99_README_SCRIPTED_ACTIONS.txt:1` | Scripted action references from components |
| S7 | `common/technology/000_documentation.txt:19` | Domain-specific technology documentation, not general grammar |
| S8 | `common/scripted_triggers/00_scripted_triggers.txt:16`, `:44` | Escaped strings in code and a negative scripted-trigger call |

Statistics and further coordinates: [pattern research](RESEARCH_SCRIPT_PATTERNS_EN.md), [machine-readable report](../../TMP/WEB_STTV/script_patterns/pattern_audit.json). Game sources were read only; product code and the rule profile were not changed.
