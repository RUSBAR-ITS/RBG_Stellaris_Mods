# Dictionary — logic and context

## Contents

- [Logical constructs](#logical-constructs)
- [Object context](#object-context)
- [Analysis rules](#analysis-rules)
- [Sources](#sources)

## Logical constructs

| Keyword or value | Form | Meaning in the examined context | Sources |
| --- | --- | --- | --- |
| `AND` | Named logical block | Requires all child conditions to hold. | L1 |
| `OR` | Named logical block | Requires at least one child condition to hold. Alternatives must not become mandatory dependencies. | L1, L2 |
| `NOT` | Named logical block | Logical negation. Preserve the whole block, including multiple child entries; do not truncate it to one node. | L1 |
| `NAND` | Named logical block | Negated AND: not all conditions hold. | L1 |
| `NOR` | Named logical block | Negated OR: none of the conditions hold. | L1, L3 |
| `yes`, `no` | Boolean values | Expected state in a boolean check. `no` does not turn an arbitrary command into logical negation: the command determines its role. | L1, L3 |
| `always` | Check taking `yes` / `no` | A constant condition result, independent of empire parameters. | L4 |
| `exists` | Check taking an object reference such as `owner` or `this` | Tests whether that object exists. Neither creates the object nor changes the scope of nested checks. | L3, L4 |

## Object context

These are references and scope transitions, not independent empire attributes. A block value is processed in the specified scope; a scalar reference is passed to another construct.

| Name | Meaning | Analytical use | Sources |
| --- | --- | --- | --- |
| `owner` | The current object's owner, where that transition is supported | `owner = { has_technology = ... }` checks the owner's technology; `exists = owner` checks whether an owner exists. | L3 |
| `founder_species` | The country's founding species | Allows `is_archetype` to apply to a species without attributing that check directly to the country object. | L5 |
| `this` | Current object at this point of execution | Preserve scope through nesting; do not assume this reference is constant across the tree. | L3, L6 |
| `root` | Root object of the current execution chain | Do not automatically replace it with the owner or current technology: a technology definition is not a runtime scope object. | L7 |
| `from` | An object supplied by the calling context | Meaning depends on the caller. Component `potential` documentation specifies `this` as the ship design and `from` as the country. It is not a universal alias for the previous block. | L6 |

## Analysis rules

- Preserve the condition tree, order and repetitions. Named logical operations differ from comparison or assignment symbols.
- `prerequisites` can contain technology ID lists inside `OR`; ordinary triggers contain checks. A shared block form does not make these contexts identical.
- This dictionary does not introduce a logical evaluator. In particular, do not assign semantics to arbitrary scalar operator forms or simplify multi-entry `NOT` without verifying the engine context.
- An unknown reference or condition is not `false`. Moving a check through `owner`, `from` or `founder_species` changes its target and may change its meaning.
- `custom_tooltip` and `hidden_trigger` are documented in [tooltips](TOOLTIPS_EN.md): they control condition presentation, not scope transitions.

## Sources

- [L1 — agreed analysis of logical values and operators](../KEYWORDS_AND_VALUES_EN.md). The historical section about temporarily ignoring inline calls belongs to an earlier stage; only its logic description is used here. [Current recognition configuration](../../config/parser/logical_operators.json).
- [L2 — alternative technology requirements](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_megastructures.txt:6).
- [L3 — job eligibility conditions](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/01_scripted_triggers_jobs.txt:2).
- [L4 — v4.3.1 trigger documentation dump](https://raw.githubusercontent.com/OldEnt/stellaris-triggers-modifiers-effects-list/master/4.3.1_game_triggers.log): `always`, `exists`. Older than the installation; local examples are checked separately.
- [L5 — founding-species check](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/02_scripted_triggers_machine_age.txt:63).
- [L6 — component scope documentation](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/000_documentation.txt:58).
- [L7 — root reference in a point-of-interest check](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:628); [root and from event contexts](E:/SteamLibrary/steamapps/common/Stellaris/events/nomads_events_1.txt:2253).

[Dictionary index](README_EN.md) · [Русская версия](LOGIC_AND_CONTEXT_RU.md).
