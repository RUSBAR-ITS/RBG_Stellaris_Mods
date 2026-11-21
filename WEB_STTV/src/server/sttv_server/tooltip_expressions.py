"""Vocabulary for the expression and argument nodes of technology tooltips."""

from .tree.ast import fields, number


# The comparison sign belongs to the assignment that supplies the numeric value.
ARGUMENTS = {
    "calc_true_if": {"amount": "value"},
    "count_archaeological_site": {"count": "value"},
    "count_owned_pop_amount": {"count": "value"},
    "count_starbase_sizes": {"count": "value", "starbase_size": "starbase_size"},
    "has_citizenship_type": {"type": "citizenship", "country": "country"},
    "has_dna": {"ship_category": "ship_category"},
    "has_resource": {"type": "resource", "amount": "value"},
    "has_slavery_type": {"type": "slavery", "country": "country"},
    "num_buildings": {"type": "building", "value": "value", "disabled": "disabled",
                      "in_construction": "in_construction"},
    "num_districts": {"type": "district", "value": "value"},
    "num_zones": {"type": "zone", "value": "value"},
    "resource_expenses_compare": {"resource": "resource", "value": "value"},
}

LOGIC = {"AND", "OR", "NOT", "NAND", "NOR"}
WEIGHT_TERMS = {
    ("weight_modifier", "modifier"): "modifier",
    ("weight_modifier", "factor"): "weight_factor",
    ("modifier", "factor"): "factor",
    ("modifier", "add"): "add",
}
FORMULA_TERMS = {
    ("script_value", "base"): "base",
    ("script_value", "add"): "formula_add",
    ("script_value", "modifier"): "formula_modifier",
    ("modifier", "mult"): "mult",
}


def operation_term(path, key):
    """Select a template suffix. The path contains the enclosing game constructs."""
    parent = path[-1] if path else None
    if key == "limit":
        if parent == "if":
            return "limit"
        if parent in ("count_owned_pop_amount", "count_archaeological_site"):
            return "limit_filter"
    if key in ("if", "else", "hidden_trigger"):
        return key
    terms = FORMULA_TERMS if "script_value" in path else WEIGHT_TERMS
    return terms.get((parent, key))


def councilor_position(block):
    """Only the exact additive owner-scoped operation has this known meaning."""
    def exact_keys(value, names):
        entries = value.get("items", [])
        return (value.get("kind") == "block" and len(entries) == len(names)
                and all(n.get("kind") == "assignment" and n["operator"] == "=" for n in entries)
                and {n["key"]["text"] for n in entries} == names)

    if not exact_keys(block, {"trigger", "trigger_scope", "mode", "parameters"}):
        return None
    def text(value, key):
        entry, = fields(value, key)
        return entry["text"] if entry["kind"] == "scalar" else None

    if (text(block, "trigger"), text(block, "trigger_scope"), text(block, "mode")) != (
        "get_councilor_level", "owner", "add"
    ):
        return None
    parameters = fields(block, "parameters")[0]
    if exact_keys(parameters, {"type"}):
        return text(parameters, "type")
    return None


def numeric_text(value, language, *, signed=False):
    """Keep the source precision and give positive additive changes an explicit sign."""
    parsed = number(value)
    if parsed is None:
        raise ValueError(f"Expected a numeric operand, got {value!r}")
    if signed and parsed > 0 and not value.startswith("+"):
        value = "+" + value
    return value.replace(".", ",") if language == "ru" else value
