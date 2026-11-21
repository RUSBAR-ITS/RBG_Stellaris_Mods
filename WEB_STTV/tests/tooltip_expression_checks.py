"""Check the expression vocabulary against compact technology trees and live translations."""

from collections import Counter

from sttv_server.tooltip_expressions import ARGUMENTS, LOGIC, councilor_position, numeric_text, operation_term
from sttv_server.tree.ast import fields, scalar


COMPARISONS = {"=", "!=", ">", "<", ">=", "<="}


def inspect(node, path, subjects, vocabulary, counts, unknown):
    """Keep unsupported expressions intact, including their nested checks."""
    kind = node["kind"]
    term = None
    if kind == "scalar":
        return
    if kind == "block":
        for entry in node["items"]:
            inspect(entry, path, subjects, vocabulary, counts, unknown)
        return
    if kind == "assignment":
        key, value = node["key"]["text"], node["value"]
        parent = path[-1]
        slot = ARGUMENTS.get(parent, {}).get(key)
        operators = COMPARISONS if slot == "value" else {"="}
        if slot and value["kind"] == "scalar" and node["operator"] in operators:
            counts["argument", parent, key] += 1
            return
        if key == "complex_trigger_modifier" and parent == "script_value" and councilor_position(value):
            counts["term", "add_councilor_level"] += 1
            for name in ("trigger", "trigger_scope", "parameters", "mode"):
                counts["argument", key, name] += 1
            counts["argument", "parameters", "type"] += 1
            term = "add_councilor_level"
        elif key in subjects:
            if key == "num_buildings" and any(fields(value, flag) for flag in ("disabled", "in_construction")):
                flags = [fields(value, name) for name in ("disabled", "in_construction")]
                if any(len(items) != 1 or items[0].get("text") != "no" for items in flags):
                    unknown.setdefault(key, {"path": list(path), "expression": node})
            inspect(value, (*path, key), subjects, vocabulary, counts, unknown)
            return
        else:
            term = operation_term(path, key)
        if term and node["operator"] == "=":
            counts["assignment", key] += 1
            if key != "complex_trigger_modifier":
                counts["term", term] += 1
                inspect(value, (*path, key), subjects, vocabulary, counts, unknown)
    elif kind == "logical_operation" and node["operator"] in LOGIC:
        term = node["operator"].lower()
        counts["term", term] += 1
        inspect(node["body"], (*path, node["operator"]), subjects, vocabulary, counts, unknown)
    elif kind == "script_value" or (kind == "scripted_trigger_test" and node["value"]["kind"] == "scalar"
                                    and node["operator"] in COMPARISONS):
        term = kind
        counts["term", term] += 1
        if kind == "scripted_trigger_test":
            counts["result comparison", node["operator"], node["value"]["text"]] += 1
        inspect(node["body"], (*path, kind), subjects, vocabulary, counts, unknown)
    if not term or (kind == "assignment" and node["operator"] != "=") or "sttv_tooltip_" + term not in vocabulary:
        name = node["key"]["text"] if kind == "assignment" else node.get("operator", kind)
        unknown.setdefault(str(name), {"path": list(path), "expression": node})


def example_phrases(samples, translated, apocalypse):
    def section(tech, key):
        block, = fields(samples[tech], key)
        return block

    def mods(tech):
        return fields(section(tech, "weight_modifier"), "modifier")

    def operands(group):
        assert group["kind"] == "logical_operation" and group["operator"] == "OR"
        return [n["text"] for n in group["body"]["items"]]

    titans = "tech_titans"
    options, = section(titans, "prerequisites")["items"]
    assert operands(options) == ["tech_battleships", "tech_stinger_growth_2"]
    assert scalar(section(titans, "potential"), "host_has_dlc") == "Apocalypse"
    threshold, = [n for mod in mods(titans) if scalar(mod, "factor") == "0.1"
                  for n in mod["items"] if n.get("operator") == "NOT"]
    years, = threshold["body"]["items"]
    assert (years["key"]["text"], years["operator"], years["value"]["text"]) == ("years_passed", ">", "100")
    neighbor, = [mod for mod in mods(titans)
                 if any(scalar(n, "has_technology") == titans for n in fields(mod, "any_neighbor_country"))]

    mega = "tech_mega_engineering"
    left, required, right = section(mega, "prerequisites")["items"]
    assert operands(left) == ["tech_starbase_5", "tech_arkship_tier_3"]
    assert required["text"] == "tech_zero_point_power"
    assert operands(right) == ["tech_battleships", "tech_stingers"]
    overall = scalar(section(mega, "weight_modifier"), "factor")

    necro, = [m for m in mods("tech_synthetic_leaders") if scalar(m, "has_origin") == "origin_necrophage"]
    assert scalar(necro, "has_trait") == "trait_necrophage"
    armor, = [m for m in mods("tech_crystal_armor_1") if scalar(m, "has_country_flag") == "crystal_armor_1_weight"]

    storm = mods("tech_storm_manipulation")
    outer, = [v["body"] for m in storm for v in fields(m, "factor") if v["kind"] == "script_value"]
    assert [n["key"]["text"] for n in outer["items"]] == ["base", "modifier", "add"]
    conditional, = fields(outer, "modifier")
    assert fields(conditional, "any_owned_leader")
    inner, = fields(conditional, "mult")
    positions = [councilor_position(b) for b in fields(inner["body"], "complex_trigger_modifier")]
    assert positions == ["councilor_storm_callers", "councilor_storm_callers_megacorp"]
    zero, = [scalar(m, "factor") for m in storm
             if scalar(m, "has_origin") == "origin_storm_chasers" and scalar(m, "factor") == "0"]
    values = [scalar(neighbor, "factor"), overall, scalar(necro, "factor"), scalar(armor, "add"), zero]
    assert values == ["10", "0.25", "0.33", "5", "0"]
    phrases = {}
    for lang, text in translated.items():
        def phrase(key, **values):
            return text["sttv_tooltip_" + key].format(**values)

        phrases[lang] = {
            titans: {"prerequisites": [phrase("or"), [text[k] for k in operands(options)]],
                     "potential": phrase("host_has_dlc", dlc=apocalypse[lang]),
                     "weight_rules": [
                         [phrase("factor", value=numeric_text("0.1", lang)),
                          phrase("years_passed", comparison="≤", value=years["value"]["text"])],
                         [phrase("factor", value=values[0]), phrase("any_neighbor_country"),
                          phrase("has_technology", technology=text[titans])]]},
            mega: {"prerequisites": [phrase("and"), [
                       [phrase("or"), [text[k] for k in operands(left)]], text[required["text"]],
                       [phrase("or"), [text[k] for k in operands(right)]]]],
                   "overall_factor": phrase("weight_factor", value=numeric_text(overall, lang))},
            "tech_synthetic_leaders": [phrase("factor", value=numeric_text(values[2], lang)), phrase("and"),
                                       phrase("has_origin", origin=text["origin_necrophage"]),
                                       phrase("has_trait_species", trait=text["trait_necrophage"])],
            "tech_crystal_armor_1": [],
            "tech_storm_manipulation": {
                "operations_in_nested_value": [phrase("add_councilor_level", position=text[p]) for p in positions],
                "separate_modifier": [phrase("factor", value=zero),
                                      phrase("has_origin", origin=text["origin_storm_chasers"])]},
        }
        assert numeric_text("-1.50", lang, signed=True) == ("-1,50" if lang == "ru" else "-1.50")
        assert numeric_text("0", lang, signed=True) == "0"
    return phrases


def synthetic_checks(subjects, vocabulary):
    def assignment(key, value):
        return {"kind": "assignment", "key": {"kind": "scalar", "text": key}, "operator": "=", "value": value}

    def block(*items):
        return {"kind": "block", "items": list(items)}

    always = assignment("always", {"kind": "scalar", "text": "yes"})
    extra = assignment("unknown_check", block(always))
    nand = {"kind": "logical_operation", "operator": "NAND", "body": block(always, extra)}
    counts, unknown = Counter(), {}
    inspect(nand, ("allow",), subjects, vocabulary, counts, unknown)
    assert counts["term", "nand"] == 1
    assert unknown == {"unknown_check": {"path": ["allow", "NAND"], "expression": extra}}
    changed = assignment("complex_trigger_modifier", block(
        assignment("mode", {"kind": "scalar", "text": "multiply"}), extra))
    unknown = {}
    inspect(changed, ("weight_modifier", "script_value"), subjects, vocabulary, Counter(), unknown)
    assert unknown["complex_trigger_modifier"]["expression"] == changed
    assert ARGUMENTS["num_buildings"]["type"] == "building"
    assert ARGUMENTS["has_resource"]["type"] == "resource"
