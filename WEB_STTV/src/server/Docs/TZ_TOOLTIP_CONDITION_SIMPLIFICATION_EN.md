# Specification. Shorter conditions in technology tooltips

## Contents

- [User-visible result](#user-visible-result)
- [Simplification rules](#simplification-rules)
- [Design check against the current database](#design-check-against-the-current-database)
- [Implementation acceptance](#implementation-acceptance)

## User-visible result

Implemented on the test site. The server simplifies the conditions displayed by `POST /api/trees/technology-tooltip`. Quantum Neuro-Links (`tech_neuro_quantum_links`) should read as follows.

**Technology can appear:**

- All of the following are true:
  - The empire does not have the origin “Wilderness”.
  - At least one of the following is true:
    - The empire’s form of government is not “Machine Intelligence”.
    - Has the civic “Driven Assimilator”.

The source expression is `AND(NOT(AND(origin)), OR(NOT(AND(authority)), civic))`. The civic provides an alternative only to the authority check. Names embedded in these phrases retain their game colors.

Particle Lances (`tech_energy_lance_1`) requires X-Ray Lasers and at least one of two ship technologies. The “Required technologies” section should read:

- All of the following are true:
  - Has researched the technology “X-Ray Lasers”
  - At least one of these technologies has been researched:
    - Battleships
    - Stingers

## Simplification rules

Process the server presentation tree from the leaves upwards, before choosing full or abbreviated technology labels. Apply the rules to `prerequisites`, `potential`, `allow` and conditions within weight modifiers. Game source documents, availability evaluation, parent selection and tree coordinates retain their existing roles. The client renders the resulting expression. Add the final colon to the “Technology can appear:” subsection title in both languages.

1. **One operand under AND or OR.** Replace the group with its sole predicate. Count all direct nodes before selecting content for display. A predicate can be a recognized check, a required technology, a logical group or a scoped check. Promote the entire scoped node, including its subject. Retain groups with zero or multiple children. Captions, technical fragments and unknown expressions keep their contents and position.
2. **Negation of a named check.** This iteration supports two positive predicates with the `=` operator and a scalar argument. If the first rule leaves exactly one such check under `NOT`, display a single negative phrase. The response keeps `kind: condition` and the original `key`, and sets `negated: true`. Resolve the object name through the same lookup as in the positive phrase.

   | Predicate | Dictionary key | RU phrase | EN phrase |
   |---|---|---|---|
   | `has_origin` | `sttv_tooltip_not_has_origin` | У государства нет происхождения «§Y{origin}§!» | The empire does not have the origin “§Y{origin}§!” |
   | `has_authority` | `sttv_tooltip_not_has_authority` | Форма правления государства — не «§Y{authority}§!» | The empire’s form of government is not “§Y{authority}§!” |

3. **Negation boundaries.** For other predicates, a missing phrase in the selected language or a compound operand, use the existing negation group with its children. Preserve the dedicated negative technology heading and existing numeric comparison inversion. Double negation retains both polarities. `NAND`, `NOR` and multi-operand `NOT` retain their operator and all operands. Preserve the scope of negation around subjects, `hidden_trigger`, `custom_tooltip` and computed formulas. Eligible predicates inside them can still be simplified.
4. **Research check labels.** Choose the label from the immediate heading after group simplification. Under a technology heading (“All of these technologies have been researched:”, “At least one of these technologies has been researched:” or their negative forms), give only the name of each direct item. Everywhere else use the full `sttv_tooltip_has_technology` phrase, including a sole prerequisite and a direct item alongside a subgroup. This applies equally to a scalar ID in `prerequisites` and to `has_technology`, even when the expression structure stays the same. The “Required technologies” section title alone cannot supply the verb. A group containing a nested alternative retains its general heading. Apply the game color once to the name alone. Keep the subject and negation at their original level. Keep the distinct eligibility phrase for `can_research_technology`.
5. Each heading introducing a list ends with one colon. Preserve check order, arguments, coefficients and calculation steps.

## Design check against the current database

An in-memory design check on 21 November 2026 covered 679 technologies in MongoDB and compared 1,364 nonempty technology/section pairs. For comparison, a unary AND/OR was reduced to its operand, and each new negative phrase was expanded back into `NOT` around its original predicate. The check compared structure, order, arguments, subjects and operations. Research checks were compared by technology ID across full and abbreviated labels. All comparisons matched.

| Section | Technologies with display changes | Unary AND | Unary OR | Negated origins | Negated authorities |
|---|---:|---:|---:|---:|---:|
| `potential` | 227 | 300 | 0 | 33 | 12 |
| `weight_modifier` | 179 | 891 | 0 | 1 | 1 |
| `prerequisites`, `allow` | 0 | 0 | 0 | 0 | 0 |

The table counts group and negation simplifications for **312 technologies**. All eight assignments to the three predicates were checked for Quantum Neuro-Links. Both expressions allow the technology for the same three assignments. All 12 two-operand negations retained both operands. Twelve synthetic cases covered boundaries including empty groups, unary OR in `allow`, scoped conditions, unknown checks, captions, hidden checks and a negated technology requirement. An in-memory preview inserted database names into both proposed translations.

The full label is also needed in `prerequisites` for **422 technologies**. For 412 it is the sole requirement, and for 10 it is a direct item under a general heading. The two counts overlap by 164 technologies, bringing the combined total to **570 of 679**. Structure and IDs matched across all 1,364 technology/section pairs after relabeling. The Russian and English previews for Particle Lances and all eight research combinations were checked. The requirement holds in three combinations, each of which includes X-Ray Lasers.

## Implementation acceptance

- Repeat the comparison on the complete current dataset. Check structure and wording separately. Recalculate the counts from source data when the game version changes.
- Open Quantum Neuro-Links in Russian and English. Check the sample text, colors of the three names, colons, indentation and all eight assignments. Simulate a missing negative translation and check that a readable negation group appears.
- For Particle Lances, verify the full mandatory research phrase and the two short names under the alternative heading in RU and EN. Also check a sole scalar prerequisite and a flat group of several mandatory technologies. The first uses “Has researched the technology”, and the second supplies the verb once in “All of these technologies have been researched:”.
- For Titans, check the technology alternatives, numeric threshold and the neighbouring empire as the subject. For Mega-Engineering, check both OR groups. For `tech_crystal_armor_1` and `tech_storm_manipulation`, check the addition, zero multiplier and order of calculated formula steps.
- In synthetic checks, compare the complete unknown expression and retain every child of a multi-operand `NOT`. A standalone research condition must have a complete phrase. Nested alternatives and compound negations retain their meaning.

Acceptance on 21 November 2026 confirmed equivalent research and weight conditions across 679 technologies and 1,364 nonempty technology/section pairs in each language. The presentation changed for 570 technologies. The test site API was checked for eight technologies in both languages. Chrome checks on the test site covered mixed prerequisites for Particle Lances, availability for Quantum Neuro-Links, the flat list for `tech_habitat_2` and the sole prerequisite for `tech_lasers_2` in RU and EN. [Content specification](../../../Docs/frontend/TZ_TECHNOLOGY_TOOLTIP_CONTENT_EN.md) · [Logical semantics](../../../Docs/semantics/LOGIC_AND_CONTEXT_EN.md) · [Русская версия](TZ_TOOLTIP_CONDITION_SIMPLIFICATION_RU.md)
