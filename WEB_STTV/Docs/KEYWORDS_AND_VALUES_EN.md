# Stellaris — keywords and values

## Contents

- [Purpose and status](#purpose-and-status)
- [Boolean values](#boolean-values)
- [Keyword id — identifier](#keyword-id--identifier)
- [Logical operators](#logical-operators)
- [Inline_script — opaque value](#inline_script--opaque-value)
- [Evidence and verification scope](#evidence-and-verification-scope)

## Purpose and status

This document records the incremental review of Stellaris language text elements: the user proposes an interpretation, it is checked against source files, and the agreed result is added here. Each accepted group retains its purpose, recognition rule, examples, and verification evidence.

Currently, **boolean values** `yes`/`no`, the **keyword `id`** for specifying an identifier, **logical operators** `AND`, `OR`, `NOT`, `NAND`, `NOR`, and the temporary representation of **`inline_script` contents as an opaque scalar value** have been approved. Other elements in the frequency list have not yet been classified as part of this review. Further findings are added to both language versions after verification and agreement.

This reference document records agreed decisions. Recording a rule here does not mean that the parser or its configuration already implements it.

## Boolean values

**Status:** approved by the user on 2026-11-15. **Class:** boolean value (`boolean`).

| Stellaris spelling | Meaning | JSON equivalent | Occurrences in the checked corpus |
| --- | --- | --- | ---: |
| `yes` | True, yes | `true` | 76,437 |
| `no` | False, no | `false` | 30,092 |

The rule applies to a separate unquoted value matching `yes` or `no` in full and in the stated case. Boolean values are neither operators nor command names.

Rule boundaries:

- It does not apply to parts of identifiers, strings, or substitutions. For example, `no` inside `no_name` does not make that identifier a boolean value.
- It does not prescribe converting the strings `"yes"` and `"no"` into booleans. No such quoted strings were found among the checked occurrences.
- It does not establish the behavior of other case variants such as `YES` or `No`.
- It identifies the value class, not the meaning of the entire command. The specific operation and the validity of its value depend on context.

Form examples:

```text
is_ai = yes
is_ai = no
clear_deposits = yes
```

The first two entries test a condition against an expected boolean result. The third invokes an effect. Classifying `yes` as a boolean value does not turn an effect invocation into a condition or define that effect's behavior with `no`.

The `true`/`false` equivalents in the table explain the meaning. They do not imply a change to the current parser-tree or database format.

## Keyword id — identifier

**Status:** approved by the user on 2026-11-15. **Class:** keyword — identifier field.

**`id` (identifier) defines or specifies the identifier of an object or group.** An identifier designates a record, refers to it, or allows records to be matched. This is the shared purpose of the word; our list does not split `id` into separate entries by object type.

General form:

```text
id = identifier
```

Here, `identifier` is a placeholder for the value. The keyword `id` occurs to the left of `=`, with one scalar value on the right: a number or text, including quoted text and substitutions. No blocks, lists, or formulas occur on the right in the checked corpus. Our list combines the spellings `id` and `ID` into one `id` entry.

Examples from source files:

```text
id = 1
id = achievement.1
id = "crisis_8156.trigger.1"
id = $EVENT_ID$
id = fotd.patrol.1.$TIER$@root
```

In an event definition, `id` establishes the event's identifier; in an event call, it specifies the identifier of the event to fire. Aura documentation also uses `id` for a shared group: among auras with the same identifier, the aura with the highest priority is applied. Thus, identifiers also support grouping; global uniqueness of every value is not implied.

## Logical operators

**Status:** the basic rule was approved by the user on 2026-11-15. **Class:** named logical operator.

| Operator | Purpose | Logical blocks in the checked corpus |
| --- | --- | ---: |
| `AND` | Logical AND: all conditions are satisfied | 2,869 |
| `OR` | Logical OR: at least one condition is satisfied | 11,647 |
| `NOT` | Logical negation | 16,232 |
| `NAND` | Negated AND: not all conditions are satisfied | 339 |
| `NOR` | Negated OR: none of the conditions are satisfied | 4,939 |

The basic form has the operator name to the left of `=` and a `{ … }` block on the right. Recognition of these five names ignores case; original spelling is preserved. These are named constructs over parsed structure, not new lexical symbols alongside `=`, `>`, and others.

Recognition and preservation rule:

1. First respect the boundaries of strings, comments, and opaque `inline_script` values. Do not identify logical operators inside them.
2. In the structure available for analysis, recognize a separate unquoted name `AND`, `OR`, `NOT`, `NAND`, or `NOR`, followed by `=` and a block.
3. Preserve the order and repetitions of child entries. Contents may include expressions, standalone identifiers, and nested logical blocks; do not require every item to use `key = value`.
4. Do not restrict `NOT` to one child entry. Source blocks with multiple entries must be preserved in full by structural parsing.
5. Do not evaluate conditions or simplify expressions. The number and form of items do not change the class of a recognized logical block.

An identifier list inside a logical block — `common/technology/00_biogenesis_tech.txt:794`:

```text
prerequisites = {
    tech_stingers
    OR = {
        tech_mauler_growth_1
        tech_stinger_growth_1
        tech_weaver_growth_1
        tech_harbinger_growth_1
    }
}
```

Multiple entries inside `NOT` — `common/anomalies/01_anomaly_categories.txt:676`:

```text
NOT = {
    has_technology = tech_lasers_3
    has_technology = tech_lasers_4
    has_technology = tech_lasers_5
}
```

`localization = AND`, the string `"AND"`, and the substitution `$AND$` do not match the logical-block form. The spelling `NOT` inside an opaque `inline_script` is not classified at this stage. The shorthand logical-operation form `NOT = tech_mauler_growth_1` is not established by the checked sources and is not included in the basic rule; the lack of an example does not establish an engine prohibition.

Table figures refer to the original `common/` and `events/` research, without include expansion or recalculation of the frequency list. The review covered 36,028 separate occurrences of the five names: 36,026 logical blocks, one `localization = AND` value, and one `NOT = xenophile` parameter inside `inline_script`. String contents were not counted as separate outer nodes. Details: [logical_operators_audit.json](../../TMP/WEB_STTV/text_frequency/logical_operators_audit.json).

## Inline_script — opaque value

**Status:** the temporary rule was approved by the user on 2026-11-15. **Contents class at the current stage:** opaque scalar value.

Both forms receive the same treatment:

```text
inline_script = paragon/council_weight_mult
```

```text
inline_script = {
    script = paragon/ethic_weight_mult
    IS = xenophobe
    NOT = xenophile
}
```

The entire value to the right of `=` is treated as one indivisible value: both a plain script reference and a brace-delimited block. The block form is not an exception: its internal entries are neither parsed nor classified at this stage.

Following the user's subsequent clarification, this value is passed to a **separate `inline_script` expansion function**. For now, the function is a stub returning an empty result: the entire invocation is skipped, leaving no reference, block, or opaque scalar in the resulting tree. The opaque value is only handler input; source text and skipped coordinates are preserved separately from the tree.

- Preserve the complete original value, including quotes, brackets, strings, and source coordinates. Ignoring contents does not mean deleting them.
- Identify only the outer value boundaries needed to continue parsing neighboring entries. Brackets inside strings and comments must not terminate the value.
- Do not extract fields, parameters, logical operators, or code inside strings from the value. Do not perform substitutions.
- Do not expand a plain reference or load its template; do not expand a reference written inside a block either.
- Rules for processing `inline_script` contents will be defined separately at the next stage.

Settings for the five logical operators reside in a separate `config/parser/logical_operators.json`. The node model, configuration integration, stub function, and checks are described in the [implemented fourth-stage specification](TZ_BACKEND_STAGE_4_EN.md).

Implementation is complete: logical blocks use `LogicalOperation` nodes, and both `inline_script` forms are skipped through `expand_inline_script`. `InlineScriptValue` exists only as function input. Source tokens and `Document.skipped_inline_scripts` retain text and skip coordinates. Verification found 36,026 logical nodes and 6,885 invocations; the third frequency pass excludes these constructs from the statistics. [Interface and limitations](BACKEND_STAGE_4_EN.md).

## Evidence and verification scope

The source corpus consists of vanilla `.txt` files under `common/` and `events/` in the installed Stellaris v4.5.4, researched on 2026-11-15. Coverage and excluded files are described in the [frequency research](RESEARCH_TEXT_FREQUENCY_EN.md). Figures for `yes`/`no` refer to the first, case-sensitive pass; `id` statistics merge case variants. The current [frequencies.txt](../data/text_frequency/frequencies.txt) excludes `yes`/`no`, elements with a frequency of 1, recognized logical operators, and entire `inline_script` calls. The fourth frequency pass also excludes script variables written as `@name` and `$NAME$` substitutions; the frequency research specifies the filter boundaries. Report filtering does not extend the scope of the classification rules verified here.

A separate contextual check of all **106,529** occurrences of `yes` and `no` established that:

- All occur to the right of an operator as separate unquoted values.
- No occurrences were found as names to the left of an operator or standalone list elements.
- All files containing the counted occurrences parsed successfully; totals matched the frequency statistics. Source-file hashes matched the run manifest.
- No counterexamples to the accepted interpretation were found in the researched corpus.

Checking all **20,358** separate case-insensitive occurrences of `id` in **428** files established that:

- Every occurrence is unquoted and to the left of `=`, with one `Scalar` node on the right. No `id` occurrences appear on the right or as standalone list elements.
- There are 20,357 `id` spellings and one `ID`. The right-hand value is quoted in 143 cases and contains a substitution parameter in 53 cases.
- All files containing counted occurrences parsed successfully; the total matches the frequency report. Hashes of all 2,238 files in the source manifest match the previous run.
- Details are retained in the research report [id_context_audit.json](../../TMP/WEB_STTV/text_frequency/id_context_audit.json).

Sources supporting the purpose of `id` and the examples; paths are relative to `STELLARIS_ROOT`:

| Source | Evidence |
| --- | --- |
| `common/component_templates/000_documentation.txt:89` and `:90` | Documentation: shared aura identifier for priority selection, using `id = aura_id` |
| `common/component_templates/00_biogenesis_special_utilities.txt:875` | `id = growth_aura` used in `stack_info` |
| `events/achievement_events.txt:5` | Event definition identifier `achievement.1` |
| `common/scripted_effects/astral_planes_effects.txt:18` | Identifier of the called event `tutorial.1340` |
| `common/achievements.txt:2` | Numeric achievement identifier |
| `common/scripted_effects/02_machine_age_effects.txt:1931` | Quoted identifier value |
| `common/inline_scripts/grand_archive/collection/curator_postponed_reward_stage_1_event.txt:2` | Identifier supplied through `$EVENT_ID$` |
| `common/inline_scripts/fotd/create_seperatists_fleet.txt:25` | Compound value `fotd.patrol.1.$TIER$@root` |

The conclusion concerns the checked corpus and the agreed classification rule; this research does not establish every possible form supported by the engine's language. General constructs and lexical operators are covered separately in the [syntax description](SCRIPT_SYNTAX_EN.md).
