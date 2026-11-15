"""Single field and cardinality contract shared by conversion and schema generation."""

from dataclasses import dataclass

# Operators representable in database format version 1.
SCRIPT_OPERATORS = {"=", "<", ">", "<=", ">=", "!=", "?="}


@dataclass(frozen=True)
class Field:
    kind: str
    multiple: bool = False


CONTRACTS = {
    "technologies": {
        "area": Field("area"), "tier": Field("integer"), "levels": Field("integer"),
        "cost": Field("cost"), "cost_per_level": Field("number"), "weight": Field("number"),
        "category": Field("list"), "feature_flags": Field("list"), "weight_groups": Field("list"),
        "is_rare": Field("boolean"), "is_dangerous": Field("boolean"),
        "is_insight": Field("boolean"), "is_reverse_engineerable": Field("boolean"),
        "start_tech": Field("boolean"), "icon": Field("identifier"), "gateway": Field("identifier"),
        "prerequisites": Field("requirements"), "potential": Field("condition"),
        "starting_potential": Field("condition"), "ai_weight": Field("calculation"),
        "modifier": Field("modifier"), "mod_weight_if_group_picked": Field("group_weights"),
        "weight_modifier": Field("calculation", True), "prereqfor_desc": Field("unlock", True),
        "technology_swap": Field("variant", True),
    },
    "variant": {
        "trigger": Field("condition"), "modifier": Field("modifier"), "weight": Field("calculation"),
        "inherit_icon": Field("boolean"), "inherit_effects": Field("boolean"),
        "area": Field("area"), "category": Field("list"), "prereqfor_desc": Field("unlock", True),
    },
    "categories": {"icon": Field("identifier"), "weight_modifier": Field("calculation", True)},
    "tiers": {"previously_unlocked": Field("number"), "weight_modifier": Field("calculation", True)},
}
SCRIPT_CONTEXTS = {"condition", "calculation", "modifier", "group_weights", "unlock"}
AREAS = ("physics", "society", "engineering")
