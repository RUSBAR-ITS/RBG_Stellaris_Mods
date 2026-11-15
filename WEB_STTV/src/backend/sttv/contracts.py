"""Declared conversions for each game-definition context."""

BASE = {
    "area": "area", "tier": "integer", "levels": "integer",
    "cost": "cost", "cost_per_level": "number", "weight": "number",
    "category": "list", "feature_flags": "list", "weight_groups": "list",
    "is_rare": "boolean", "is_dangerous": "boolean", "is_insight": "boolean",
    "is_reverse_engineerable": "boolean", "start_tech": "boolean",
    "icon": "identifier", "gateway": "identifier", "prerequisites": "requirements",
    "potential": "condition", "starting_potential": "condition",
    "ai_weight": "calculation", "modifier": "modifier",
    "mod_weight_if_group_picked": "group_weights",
    "weight_modifier": "calculation", "prereqfor_desc": "unlock",
    "technology_swap": "variant",
}
VARIANT = {
    "trigger": "condition", "modifier": "modifier", "weight": "calculation",
    "inherit_icon": "boolean", "inherit_effects": "boolean",
    "area": "area", "category": "list", "prereqfor_desc": "unlock",
}
CATEGORY = {"icon": "identifier", "weight_modifier": "calculation"}
TIER = {"previously_unlocked": "number", "weight_modifier": "calculation"}
CONTRACTS = {"technologies": BASE, "variant": VARIANT,
             "categories": CATEGORY, "tiers": TIER}
MULTIPLE = {"weight_modifier", "prereqfor_desc", "technology_swap"}
SCRIPT_CONTEXTS = {"condition", "calculation", "modifier", "group_weights", "unlock"}
