"""Check the shipped catalogue, including nonhuman graphics and phenotype transitions."""
import argparse
from collections import Counter
from functools import lru_cache
import json
from pathlib import Path
import re

from build import Appearance, CONFIG, MOD, SYNTAX, asset_checker, fields, kv, read, scan, values, words
from stellaris_parser.script.inline import Expansion, MemoryTemplates
from stellaris_parser.script.nodes import Assignment
from stellaris_parser.script.traversal import walk


def verify_event_expansion(catalogues):
    definitions = {}
    for path in (MOD / "common/scripted_effects").glob("*.txt"):
        doc = catalogues[path] if path in catalogues else read(path)[1]
        definitions.update(fields(doc))
    graph = {}

    def calls(block):
        return Counter(node.key.text for node in walk(block.items)
                       if isinstance(node, Assignment) and node.key.text in definitions)

    for key, body in definitions.items():
        graph[key] = calls(body)

    @lru_cache(maxsize=None)
    def depth(key):
        return 1 + max((depth(child) for child in graph[key]), default=0)

    @lru_cache(maxsize=None)
    def copies(key, target):
        return int(key == target) + sum(n * copies(child, target) for child, n in graph[key].items())

    folder = MOD / "common/inline_scripts"
    config = json.loads((CONFIG / "inline_scripts.json").read_text())
    templates = MemoryTemplates({p.relative_to(folder).as_posix(): p.read_text("utf-8-sig")
                                 for p in folder.rglob("*.txt")}, config)
    expander = Expansion(templates, config)
    events = {}
    for path in (MOD / "events").glob("*.txt"):
        doc = expander.expand(read(path)[1], SYNTAX)
        for event in values(doc, "country_event"):
            key, = kv(event, "id")
            events[key] = calls(event)
            if key == "rb_le.26":
                verify_arrows(event)
            if key in ("rb_le.25", "rb_le.26"):
                options = {kv(o, "name")[0]: o for o in values(event, "option")}
                discard_label = "BACK" if key == "rb_le.25" else "CANCEL"
                discard, = values(options[discard_label], "hidden_effect")
                assert kv(discard, "rb_le_close_portrait") == ["yes"]
                assert kv(values(discard, "country_event")[0], "id") == ["rb_le.20"]
                assert list(options)[-2:] == ["BACK", "rb_le_exit"]
                if key == "rb_le.26":
                    back, = values(options["BACK"], "hidden_effect")
                    assert not kv(back, "rb_le_close_portrait")
                    assert kv(values(back, "country_event")[0], "id") == ["rb_le.25"]
            if key == "rb_le.20":
                inspect, = values(event, "immediate")
                assert fields(inspect)[0][0] == "rb_le_inspect_portrait"
                pending, = values(inspect, "if")
                assert kv(values(pending, "limit")[0], "has_country_flag") == ["rb_le_check_written"]
                result, = values(pending, "if")
                checks = values(values(result, "limit")[0], "check_variable")
                assert any(kv(c, "which") == ["rb_le_read_look"] and kv(c, "value") == ["rb_le_expected_look"] for c in checks)
                assert kv(values(result, "country_event")[0], "id") == ["rb_le.29"]
                assert kv(values(values(pending, "else")[0], "country_event")[0], "id") == ["rb_le.28"]
    assert not expander.warnings, expander.warnings
    portrait_screens = ("rb_le.20", "rb_le.25", "rb_le.26", "rb_le.27", "rb_le.28", "rb_le.29")
    longest = max(depth(key) for screen in portrait_screens for key in events[screen])
    assert longest < 5, (longest, portrait_screens)
    for target, entry in (("rb_le_render_choices", "rb_le.27"), ("rb_le_render_pose", "rb_le.27"),
                          ("rb_le_identify_portrait", "rb_le.20")):
        expanded = {screen: sum(n * copies(key, target) for key, n in roots.items())
                    for screen, roots in events.items()}
        assert {screen: n for screen, n in expanded.items() if n} == {entry: 1}, expanded

    paint = definitions["rb_le_paint_portrait"]
    commit, = values(paint, "if")
    assert kv(values(commit, "limit")[0], "has_country_flag") == ["rb_le_commit_preview"]
    write, = values(commit, "event_target:rb_le_selected_leader")
    assert kv(write, "change_leader_portrait") == ["$PORTRAIT$"]
    expected, = values(commit, "set_variable")
    assert kv(expected, "which") == ["rb_le_expected_look"] and kv(expected, "value") == ["$INDEX$"]
    probe_reads = values(definitions["rb_le_read_subject_portrait"], "change_species_characteristics")
    assert [kv(s, "portrait")[0] for s in probe_reads] == ["rb_le_empty_portrait", "event_target:rb_le_selected_leader"]
    assert all(kv(s, "can_change_leader") == ["no"] for s in probe_reads)
    preview, = values(values(paint, "else")[0], "event_target:rb_le_portrait_probe")
    assert kv(values(preview, "change_species_characteristics")[0], "portrait") == ["$PORTRAIT$"]
    verified, = values(preview, "if")
    assert kv(values(verified, "limit")[0], "species_portrait") == ["$PORTRAIT$"]
    assert kv(values(verified, "root")[0], "set_country_flag") == ["rb_le_preview_ready"]
    print(f"Portrait event expansion: maximum scripted-effect depth {longest}; one catalogue render entry.")


def verify_arrows(event):
    options = values(event, "option")
    assert [kv(o, "name")[0] for o in options] == ["rb_le_portrait_next", "rb_le_portrait_prev"] * 5 + ["ACCEPT", "CANCEL", "BACK", "rb_le_exit"]
    trigger, = values(read(MOD / "common/scripted_triggers/rb_le_portrait.txt")[1], "rb_le_can_cycle_axis")
    assert kv(trigger, "rb_le_has_preview") == ["yes"]
    assert [(kv(v, "which")[0], kv(v, "value")[0]) for v in values(trigger, "check_variable")] == [
        ("rb_le_axis", "$ID$"), ("rb_le_$AXIS$_n", "1")]
    count_check = values(trigger, "check_variable")[-1]
    assert next(a.operator for a in count_check.items if a.key.text == "value") == ">"
    for i, axis in enumerate(("pheno", "tex", "hair", "outfit", "stage")):
        var = "rb_le_" + axis
        for opt, step in zip(options[2*i:2*i+2], (1, -1)):
            hidden, = values(opt, "hidden_effect")
            guarded, = values(hidden, "if")
            assert kv(values(hidden, "country_event")[0], "id") == ["rb_le.27"]
            for rule in (values(opt, "trigger")[0], values(guarded, "limit")[0]):
                args, = values(rule, "rb_le_can_cycle_axis")
                assert kv(args, "AXIS") == [axis] and kv(args, "ID") == [str(i+1)]
            wrap, = values(guarded, "if")
            check, = values(values(wrap, "limit")[0], "check_variable")
            reset, = values(wrap, "set_variable")
            normal, = values(values(guarded, "else")[0], "change_variable")
            assert all(kv(c, "which") == [var] for c in (check, reset, normal))
            assert next(a.operator for a in check.items if a.key.text == "value") == "="
            for n in (2, 5, 26, 96):
                read_value = {var+"_n": n, "1": 1, "-1": -1}
                for current in range(1, n + 1):
                    actual = (read_value[kv(reset, "value")[0]] if current == read_value[kv(check, "value")[0]]
                              else current + read_value[kv(normal, "value")[0]])
                    assert actual == (current - 1 + step) % n + 1, (axis, current, n, step)


def check_transition(source, destination, originals, effects):
    old, new = originals[source].hairs, originals[destination].hairs
    old_id, = [kv(value, "value")[0] for value in values(effects["rb_le_body_" + source], "set_variable")
               if kv(value, "which") == ["rb_le_body"]]
    for index, path in enumerate(old, 1):
        state = dict(rb_le_hair=index, rb_le_body=int(old_id), rb_le_outfit=1, rb_le_tex=1)

        def execute(block):
            matched = False
            for op, value in fields(block):
                if op == "rb_le_bound_portrait_choices":
                    return
                if op == "set_variable":
                    state[kv(value, "which")[0]] = int(kv(value, "value")[0])
                if op == "if":
                    matched = False
                if op in ("if", "else_if") and not matched:
                    limit, = values(value, "limit")
                    condition, = values(limit, "check_variable")
                    matched = state[kv(condition, "which")[0]] == int(kv(condition, "value")[0])
                    if matched:
                        execute(value)
                elif op == "else" and not matched:
                    execute(value)

        execute(effects["rb_le_body_" + destination])
        result = state["rb_le_hair"] if state["rb_le_hair"] <= len(new) else 1
        assert result == (new.index(path) + 1 if path in new else 1), (source, destination, index)


def pose_leaves(block, selection):
    for op, value in fields(block):
        if op == "limit":
            continue
        if op == "rb_le_paint_portrait":
            yield selection, kv(value, "PORTRAIT")[0], int(kv(value, "INDEX")[0])
            continue
        assert op in ("if", "else_if")
        condition, = values(values(value, "limit")[0], "check_variable")
        axis, = kv(condition, "which")
        assert axis not in selection and next(a.operator for a in condition.items if a.key.text == "value") == "="
        yield from pose_leaves(value, {**selection, axis: int(kv(condition, "value")[0])})


def verify(game):
    choices_path = MOD / "common/scripted_effects/rb_le_portrait_choices.txt"
    lookup_path = MOD / "common/scripted_effects/rb_le_portrait_lookup.txt"
    choices_text, choices = read(choices_path)
    _, lookup = read(lookup_path)
    effects = dict(fields(choices))
    bodies = {k for k in effects if k.startswith("rb_le_body_")}
    families = re.findall(r"which = rb_le_family value = (\d+)", choices_text)
    assert len(set(families)) == len(families) == 410
    assert Counter(re.findall(r"(rb_le_body_\w+) = yes", choices_text)) == Counter(bodies)
    verify_event_expansion({choices_path: choices, lookup_path: lookup})

    registry, = values(lookup, "rb_le_identify_portrait")
    probe, = values(registry, "event_target:rb_le_portrait_probe")
    switch, = values(probe, "switch")
    routes = dict(fields(switch))
    assert kv(switch, "trigger") == ["species_portrait"]
    for key in ("human", "humanoid_hp_12", "human_legacy", "tox2", "cyb1", "sd_hum_robot", "psionic_06"):
        assert key in routes, key
    assert not {"rb_le_empty_portrait", "paragon_azaryn_3_buds", "paragon_azaryn_no_buds", "default"} & routes.keys()

    def lookup_value(portrait, variable):
        action, = values(values(routes[portrait], "root")[0], "set_variable")
        assert kv(action, "which") == [variable]
        return int(kv(action, "value")[0])

    edited = values(registry, "if")[0]
    family_by_index = {}
    for branch in values(edited, "if"):
        bounds = values(values(branch, "limit")[0], "check_variable")
        assert [next(a.operator for a in b.items if a.key.text == "value") for b in bounds] == [">=", "<="]
        assert all(kv(b, "which") == ["rb_le_read_look"] for b in bounds)
        first, last = (int(kv(b, "value")[0]) for b in bounds)
        assert first == len(family_by_index) + 1 and last >= first
        family, = values(branch, "set_variable")
        assert kv(family, "which") == ["rb_le_detected"]
        family_by_index.update(dict.fromkeys(range(first, last+1), int(kv(family, "value")[0])))

    gfx, portraits = read(MOD / "gfx/portraits/portraits/rb_le_appearances.txt")
    shapes = fields(values(portraits, "portraits")[0])
    assert len(shapes) == len(dict(shapes))
    assets_text, layers = read(MOD / "gfx/portraits/asset_selectors/rb_le_layers.txt")
    selectors = dict(fields(layers))
    exists = asset_checker(game)
    _, variants, vanilla_selectors = scan(game)
    originals, body_names = {}, {}
    for effect_name in bodies:
        native = effect_name.removeprefix("rb_le_body_")
        originals[native] = Appearance(native, variants[native], vanilla_selectors, exists)
        body_id, = [int(kv(v, "value")[0]) for v in values(effects[effect_name], "set_variable")
                    if kv(v, "which") == ["rb_le_body"]]
        assert body_id not in body_names
        body_names[body_id] = native
    combinations = {}
    for selector in selectors.values():
        assert len(fields(selector)) == 1 and len(kv(selector, "default")) == 1
    for key, shape in shapes:
        if key == "rb_le_empty_portrait":
            continue
        native, ti, si, hi, oi = re.fullmatch(r"rb_le_vis_(\w+)_t(\d+)_s(\d+)(?:_h(\d+)_o(\d+))?", key).groups()
        texture, stage, hair, outfit = (int(i or 1) for i in (ti, si, hi, oi))
        original = originals[native]
        index = lookup_value(key, "rb_le_read_look")
        assert family_by_index[index] == lookup_value(native, "rb_le_detected"), key
        textures = [p for v in values(shape, "character_textures") for p in words(v)]
        assert textures == [p for p in (original.textures[texture-1],) if p], key
        assert 1 <= stage <= len(original.stages)
        for axis, number, assets in (("attachment_selector", hair, original.hairs), ("clothes_selector", outfit, original.outfits)):
            selector, = kv(shape, axis)
            if assets:
                assert kv(selectors[selector], "default") == [assets[number-1]], (key, selector)
            else:
                assert number == 1 and selector == "no_texture", key
        combinations[key] = index
    assert len(set(combinations.values())) == len(combinations) == len(family_by_index)
    assert len(combinations) == sum(len(a.textures)*len(a.stages)*max(1,len(a.hairs))*max(1,len(a.outfits)) for a in originals.values())
    painted = set()
    for selection, key, index in pose_leaves(effects["rb_le_render_pose"], {}):
        original = originals[body_names[selection["rb_le_next_body"]]]
        indices = [selection.get("rb_le_" + axis, 1) for axis in ("tex", "stage", "hair", "outfit")]
        assert key == original.visual_key(*indices) and combinations[key] == index, (key, selection)
        assert key not in painted
        painted.add(key)
    assert painted == combinations.keys()
    paths = set(re.findall(r'"(gfx/[^"]+\.dds)"', gfx + assets_text))
    assert not (missing := [path for path in paths if not exists(path)]), missing

    def counts(key):
        limits = {kv(item, "which")[0]: int(kv(item, "value")[0])
                  for item in values(effects["rb_le_body_" + key], "set_variable")}
        return tuple(limits["rb_le_" + axis + "_n"] for axis in ("tex", "hair", "outfit", "stage"))

    assert all(counts(f"human_female_0{i}") == (5, 26, 7, 1) for i in range(1, 6))
    assert [counts(f"human_legacy_female_0{i}")[1] for i in range(1, 6)] == [34, 7, 21, 43, 8]
    assert counts("human_male_01") == (5, 86, 7, 1)
    assert [counts(f"human_legacy_male_0{i}")[1] for i in range(1, 6)] == [81, 20, 20, 96, 20]
    assert counts("tox2")[:2] == (3, 3) and counts("cyb1")[3] == 3
    assert counts("sd_hum_robot") == counts("bio7") == (4, 1, 1, 1)
    shape_by_key = dict(shapes)
    for a, b in ((1, 2), (2, 3), (3, 4), (4, 5), (5, 1)):
        left, right = f"human_legacy_male_0{a}", f"human_legacy_male_0{b}"
        check_transition(left, right, originals, effects)
        check_transition(right, left, originals, effects)
    for i in range(1, 5):
        shape = shape_by_key[f"rb_le_vis_pro1_f_t{i}_s2"]
        stage, = values(shape, "portrait_evolution")
        block = gfx[stage.span.start:stage.span.end].lower()
        assert f"color_{i}_" in block and "mask =" in block
    print(f"{len(bodies)} phenotypes, {len(families)} choice lists, {len(combinations)} preview graphics, "
          f"{len(selectors)} selectors, {len(paths)} available DDS assets.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", type=Path, required=True)
    verify(parser.parse_args().game)
