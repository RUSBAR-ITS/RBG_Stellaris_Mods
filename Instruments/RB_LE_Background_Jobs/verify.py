"""Verify the occupation catalogue, button bindings, pagination and stale-click guards."""
import argparse
import csv
import json
import operator
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
mod = root / "RB_LE/mod"
for package in ("Stellaris_Parser", "Document_Package"):
    sys.path.insert(0, str(root / "Instruments" / package))
from stellaris_parser.script.inline import Expansion, MemoryTemplates
from stellaris_parser.script.nodes import Assignment, Block, LogicalOperation
from stellaris_parser.script.parser import parse_text
from stellaris_parser.script.syntax import load_syntax
from stellaris_parser.script.traversal import walk

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--game", type=Path, default=Path("E:/SteamLibrary/steamapps/common/Stellaris"))
game = parser.parse_args().game
cfg = root / "Instruments/Stellaris_Parser/stellaris_parser/config"
syntax = load_syntax(*(cfg / (k + ".json") for k in ("lexical", "constructs", "logical_operators")))
options = json.loads((cfg / "inline_scripts.json").read_bytes())
tpl = mod / "common/inline_scripts"
templates = MemoryTemplates({p.relative_to(tpl).as_posix(): p.read_text("utf-8-sig")
                             for p in (tpl / "rb_le").glob("*.txt")}, options)
expander = Expansion(templates, options)


def read(relative, expand=False):
    path = mod / relative
    doc = parse_text(path.read_text("utf-8-sig"), syntax, str(path), role="template")
    return (expander.expand(doc, syntax) if expand else doc).items


def fields(items, key):
    return [n.value for n in items if isinstance(n, Assignment) and n.key.text == key]


def val(node, key):
    value, = fields(node.items, key)
    return value.text


def calls(node, key):
    return fields(walk(node.items), key)


def rule_map(path):
    return {n.key.text: n.value for n in read(path) if isinstance(n, Assignment)}


def script(node):
    if isinstance(node, Block):
        return "{ " + " ".join(script(n) for n in node.items) + " }"
    if isinstance(node, Assignment):
        return f"{node.key.text} {node.operator} {script(node.value)}"
    if hasattr(node, "body") and hasattr(node, "name"):
        return node.name.text + " = " + script(node.body)
    return node.raw


def occupations(lang):
    path = root / f"docs/RB_LE/BACKGROUND_JOB_VISIBILITY_4_6_0_{lang}.csv"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return sorted(r[0] for r in list(csv.reader(stream, delimiter=";"))[1:] if r[2] in ("Conditional", "По условию"))


ids = occupations("EN")
assert ids == occupations("RU") and len(ids) == len(set(ids)) == 101
assert {"none", "fe_overseer", "sand_caretaker"}.isdisjoint(ids)
events = {val(e, "id"): e for e in fields(read("events/rb_le_background_events.txt", True), "country_event")}
assert set(events) == {"rb_le.60", "rb_le.61", "rb_le.62"}
dossier = fields(read("events/rb_le_editor_events.txt", True), "country_event")
dossier, = [e for e in dossier if val(e, "id") == "rb_le.12"]


def menu(e):
    return {val(o, "name"): o for o in fields(e.items, "option")}


link = menu(dossier)["rb_le_background_menu"]
assert calls(link, "rb_le_can_edit_occupation") and val(calls(link, "country_event")[0], "id") == "rb_le.60"
assert list(menu(events["rb_le.60"])) == ["rb_le_change_occupation", "BACK", "rb_le_exit"]
assert calls(menu(events["rb_le.60"])["rb_le_change_occupation"], "rb_le_can_edit_occupation")
page = menu(events["rb_le.61"])

# Test the expanded controls, including the event ID passed through the register template.
registers = fields(read("events/rb_le_dossier_events.txt", True), "country_event")
screens = [(events["rb_le.61"], "rb_le_job_page", "rb_le_job_pages")]
for event in registers:
    if val(event, "id") == "rb_le.1":
        assert list(menu(event))[-1] == "rb_le_exit" and "BACK" not in menu(event)
    else:
        screens.append((event, "rb_le_page", "rb_le_pages"))
assert len(screens) == 5
comparators = {">": operator.gt, ">=": operator.ge, "<=": operator.le}


def condition(check, state):
    comparison, = [n for n in check.items if isinstance(n, Assignment) and n.key.text == "value"]
    return comparators[comparison.operator](state[val(check, "which")], state[comparison.value.text])


for event, current, total in screens:
    buttons = menu(event)
    names = ["rb_le_next_page", "rb_le_previous_page", "BACK", "rb_le_exit"]
    assert list(buttons)[-4:] == names
    for step, label in ((1, names[0]), (-1, names[1])):
        button = buttons[label]
        visible, = calls(fields(button.items, "trigger")[0], "check_variable")
        effect, = fields(button.items, "hidden_effect")
        branch, = fields(effect.items, "if")
        boundary, = calls(branch, "check_variable")
        wrap, = fields(branch.items, "set_variable")
        advance, = calls(fields(effect.items, "else")[0], "change_variable")
        assert val(advance, "which") == val(wrap, "which") == current
        assert val(calls(effect, "country_event")[0], "id") == val(event, "id")
        for pages in (0, 1, 2, 3, 11):
            for active in range(1, max(1, pages) + 1):
                state = {current: active, total: pages, "1": 1, "-1": -1}
                assert condition(visible, state) == (pages > 1)
                if pages > 1:
                    result = state[val(wrap, "value")] if condition(boundary, state) else active + state[val(advance, "value")]
                    assert result == (active - 1 + step) % pages + 1

locs = {val(x, "name"): x for x in fields(read("common/scripted_loc/rb_le_occupation_page.txt", True), "defined_text")}
expanded_collect, = fields(read("common/scripted_effects/rb_le_occupation_page.txt", True), "rb_le_collect_job_page")
scan, = fields(expanded_collect.items, "if")
assert calls(fields(scan.items, "limit")[0], "rb_le_can_edit_occupation")
assert not calls(expanded_collect, "log_error")
candidates = fields(scan.items, "if")
dispatch = events["rb_le.62"]
assert calls(dispatch, "rb_le_can_edit_occupation") and calls(dispatch, "is_variable_set")
assert val(calls(dispatch, "country_event")[0], "id") == "rb_le.12"
assert len(calls(dispatch, "change_background_job")) == 101
assert len(candidates) == 101
dispatch_conditions = calls(dispatch, "check_variable")
assert [val(c, "value") for c in dispatch_conditions] == [str(i) for i in range(1, 102)]
assert all(val(c, "which") == "rb_le_chosen_job" for c in dispatch_conditions)
assert [v.text for v in calls(dispatch, "change_background_job")] == ids
assert [script(x) for x in calls(dispatch, "event_target:rb_le_selected_leader")] == [
    "{ change_background_job = " + j + " }" for j in ids]
for i, (j, candidate) in enumerate(zip(ids, candidates), 1):
    assert calls(candidate, "has_background_job")[0].text == j
    assert calls(candidate, "rb_le_job_" + j) and calls(dispatch, "rb_le_job_" + j)
    assert val(calls(candidate, "rb_le_bind_job_slot")[0], "INDEX") == str(i)
for slot in range(1, 11):
    option = page[f"rb_le_job_slot_{slot}_label"]
    saved, = calls(option, "set_variable")
    assert (val(saved, "which"), val(saved, "value")) == ("rb_le_chosen_job", f"rb_le_job_slot_{slot}")
    assert val(calls(option, "country_event")[0], "id") == "rb_le.62"
    lines = fields(locs[f"rb_le_job_slot_{slot}_name"].items, "text")
    assert [val(x, "localization_key") for x in lines] == ["job_" + j for j in ids]
    for index, line in enumerate(lines, 1):
        number, = calls(line, "check_variable")
        assert (val(number, "which"), val(number, "value")) == (f"rb_le_job_slot_{slot}", str(index))

rules = rule_map("common/scripted_triggers/rb_le_occupations.txt")
sites = rule_map("common/scripted_triggers/rb_le_occupation_sources.txt")
assert set(rules) == {"rb_le_job_" + j for j in ids}
all_rules = rules | sites
for node in all_rules.values():
    for item in walk(node.items):
        if isinstance(item, Assignment) and item.key.text.startswith("rb_le_"):
            assert item.key.text in all_rules, item.key.text
    assert not re.search(r"\$\w+\$", script(node))
assert not calls(rules["rb_le_job_captain"], "any_owned_pop_group")
assert calls(rules["rb_le_job_civilian"], "can_work_specific_job")[0].text == "civilian"
assert "has_edict = neurocasted_spectacles" in script(rules["rb_le_job_cyberdome_duelist"])
assert "neurocasted_spectacles" not in script(rules["rb_le_job_cyberdome_spectator"])
assert "d_desertling_infestation" in script(rules["rb_le_job_alien_hunter"])
assert "stratovent_world_modifier_refining" in script(rules["rb_le_job_stratovent_refiner"])
assert "golden_academy_reformed" in script(sites["rb_le_can_build_building_elite_academy"])
assert "owner.overlord" in script(sites["rb_le_can_build_holding_aid_agency"])
assert "value:rb_le_free_subject_holdings" in script(sites["rb_le_can_build_holding_aid_agency"])
limits = rule_map("common/script_values/rb_le_occupation_limits.txt")
holding_limit = limits["rb_le_subject_holding_limit"]
free_holdings = limits["rb_le_free_subject_holdings"]
assert val(holding_limit, "base") == val(free_holdings, "base") == "0", "Holding calculations require a numeric base"
assert [add.text for add in fields(holding_limit.items, "add")] == [
    "modifier:subject_holding_target_max_buildings_add", "overlord.modifier:subject_holding_owner_max_buildings_add"]
assert val(holding_limit, "max") == "4"
assert val(free_holdings, "add") == "value:rb_le_subject_holding_limit"
assert len(calls(free_holdings, "num_buildings")) == 4
assert "value:rb_le_available_spinal_mounts" in script(sites["rb_le_space_for_arkship_capital_shipyard"])
assert calls(limits["rb_le_available_spinal_mounts"], "parameters")
assert "branch_office_owner" in script(sites["rb_le_can_build_building_psionic_offices"])
for job in ("criminal", "dystopian_enforcer", "enforcer", "healthcare"):
    rule = rules["rb_le_job_" + job]
    owner_checks = calls(rule, "branch_office_owner")
    guarded_checks = []
    for node in walk(rule.items):
        if not isinstance(node, LogicalOperation) or node.name.text != "AND":
            continue
        block = node.body
        if fields(block.items, "has_branch_office"):
            assert script(block.items[0]) == "has_branch_office = yes", job
            guarded_checks.extend(calls(block, "branch_office_owner"))
            assert not calls(block, "num_assigned_jobs") and not calls(block, "free_jobs_of_type"), job
    assert owner_checks and guarded_checks == owner_checks, f"Unguarded branch office owner in {job}"
    assert val(calls(rule, "num_assigned_jobs")[0], "job") == job
    assert val(calls(rule, "free_jobs_of_type")[0], "job") == job
assert "pc_ark" in script(rules["rb_le_job_ark_harvester"])
assert "orbital_defence.starbase" in script(rules["rb_le_job_telepath"])

effects = rule_map("common/scripted_effects/rb_le_occupation_page.txt")
collect = effects["rb_le_collect_job_page"]
open_effect, = fields(menu(events["rb_le.60"])["rb_le_change_occupation"].items, "hidden_effect")
assert script(open_effect.items[0]) == "set_variable = { which = rb_le_job_page value = 1 }"
assert val(calls(open_effect, "country_event")[0], "id") == "rb_le.61"
for direction in ("rb_le_next_page", "rb_le_previous_page"):
    assert not calls(page[direction], "clear_variable")
bind = effects["rb_le_bind_job_slot"]
reset = effects["rb_le_clear_job_slots"]
assert [v.text for v in fields(reset.items, "clear_variable")] == [f"rb_le_job_slot_{i}" for i in range(1, 11)]
math = calls(collect, "multiply_variable")[0]
assert val(math, "which") == "rb_le_job_cursor" and val(math, "value") == "-10"
assert val(calls(collect, "divide_variable")[0], "value") == "10"
assert calls(collect, "ceiling_variable")[0].text == "rb_le_job_pages"
assert [(val(v, "which"), val(v, "value")) for v in calls(bind, "set_variable")] == [
    (f"rb_le_job_slot_{i}", "$INDEX$") for i in range(1, 11)]
for active in ([], ids[:1], ids[:10], ids[:11], ids[2::3], ids):
    expected = set(active) - {"captain"}
    result = []
    for p in range(1, (len(expected) + 9) // 10 + 1):
        cursor = (p - 1) * -10
        for candidate in candidates:
            job = calls(candidate, "has_background_job")[0].text
            if job not in expected:
                continue
            cursor += int(val(calls(candidate, "change_variable")[1], "value"))
            if 1 <= cursor <= 10:
                result.append(ids[int(val(calls(candidate, "rb_le_bind_job_slot")[0], "INDEX")) - 1])
    assert result == sorted(expected)

for folder, lang in (("english", "EN"), ("russian", "RU")):
    local = mod / f"localisation/{folder}/rb_le_l_{folder}.yml"
    assert local.read_bytes().startswith(b"\xef\xbb\xbf")
    text = local.read_text("utf-8-sig")
    assert all(f'rb_le_job_slot_{i}_label:0 "[Root.rb_le_job_slot_{i}_name]"' in text for i in range(1, 11))
    keys = set()
    for path in (game / "localisation" / folder).glob("*.yml"):
        keys.update(re.findall(r"^\s*(job_\w+)\s*:", path.read_text("utf-8-sig"), re.M))
    assert {"job_" + j for j in ids} <= keys
print("Passed: 101 candidates, 1,010 localized slot bindings, 101 selected-leader writes, navigation and source regressions.")
