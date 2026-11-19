# Stellaris construct dictionary for technology analysis

## Contents

- [Purpose](#purpose)
- [Sections](#sections)
- [Reading the entries](#reading-the-entries)
- [Use in the project](#use-in-the-project)
- [Next additions](#next-additions)

## Purpose

The first agreed set of constructs for selecting technology predecessors, identifying the function of unlocked objects and arranging the tree. The dictionary groups constructs by purpose. Entries describe meaning, context, value form, analytical use and supporting sources.

Compiled on 2026-11-18. Primary source: the installed **Stellaris Cygnus v4.5.4 (1b4f)**, verified against `launcher-settings.json`. Game example paths refer to this installation. Information from an earlier engine documentation dump is identified separately.

## Sections

| Section | Contents |
| --- | --- |
| [Technologies and variants](TECHNOLOGIES_EN.md) | Area, category, tier, dependencies, starting and repeatable technologies, conditional variants |
| [Logic and context](LOGIC_AND_CONTEXT_EN.md) | Logical operations, values, existence checks and object scope transitions |
| [Empire conditions](EMPIRE_CONDITIONS_EN.md) | Nomads, ship categories, ethics, authority, archetype, origin and civics |
| [Object relations](OBJECT_RELATIONS_EN.md) | Technology requirements, upgrades, object groups, construction conditions and displayed unlocks |
| [Effects and function](FUNCTIONAL_EFFECTS_EN.md) | Modifiers, capabilities, production, upkeep and cost |
| [Tooltips and conditions](TOOLTIPS_EN.md) | `hidden_trigger`, forms of `custom_tooltip` and text parameters |

[Русская версия](README_RU.md).

## Reading the entries

- An entry describes a **name together with its context**. `technology.category` and `resources.category` have different meanings. Dots indicate a path for the reader, not source script syntax or a new database identifier.
- Tables list forms needed for the examined contexts. They are not an exhaustive grammar or a whitelist of engine values. Source numbers may use static variables; the working database already contains their substituted values.
- Game meaning is separate from intended use in WEB_STTV. Matching a modifier or object group is evidence of related function; it does not by itself establish a selected predecessor.
- Source links support a specific use. Documentation comments do not replace checking definitions. This reference does not verify conditions in a running game.
- Built-in fields, operators, object references and named scripted triggers are distinguished explicitly. An `is_` or `has_` prefix does not determine the construct type.
- Game localization keys are recorded as string references without inventing translations. Explanations are bilingual documentation, not new game localization.

## Use in the project

The dictionary currently consists of reference documentation. Machine-readable rules, their configuration format and a condition evaluator require a separate specification. An entry does not mean its semantics are already implemented. The parser preserves unknown constructs; no mandatory command whitelist is introduced.

Requirement analysis must retain logical grouping, object context, negation and the distinction between availability, selection weight, effects and tooltip presentation. An unknown condition is not false. A condition in `weight_modifier` does not become a prerequisite merely because it contains `has_technology`.

Computed `parent_tech` and `location` belong to the WEB_STTV view model, not the game language. They may depend on the selected technology variant and layout context; their model will be documented separately. All original technology requirements remain independent of the chosen layout anchor.

Historical frequency inventories in `language/keywords/` are not the foundation of this dictionary and remain unchanged. This set does not approve an ordering of the sorting criteria under discussion or change the running interface.

## Next additions

The next candidates for tracing function through actions and events are `scripted_action`, `on_completed`, `events`, `id` and `damage_ship`. Full descriptions of their contexts and links belong to the next addition; they are not yet presented as completed analytical rules.
