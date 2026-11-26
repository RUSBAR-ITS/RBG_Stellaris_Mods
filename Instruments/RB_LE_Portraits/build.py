"""Compile vanilla leader appearances into RB_LE graphics and event lookups."""
import argparse
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
import re
import sys
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "Instruments" / p) for p in ("Stellaris_Parser", "Document_Package")]
from stellaris_parser.script.nodes import Assignment, Block, Scalar
from stellaris_parser.script.parser import parse_text
from stellaris_parser.script.syntax import load_syntax

CONFIG = ROOT / "Instruments/Stellaris_Parser/stellaris_parser/config"
SYNTAX = load_syntax(*(CONFIG / (n + ".json") for n in ("lexical", "constructs", "logical_operators")))
MOD = ROOT / "RB_LE/mod"
GENDERS = ("male", "female", "indeterminable")


def fields(block):
    return [(a.key.text, a.value) for a in block.items if isinstance(a, Assignment)]


def values(block, key):
    return [v for k, v in fields(block) if k == key]


def words(block):
    return [n.text for n in block.items if isinstance(n, Scalar)]


def distinct(seq):
    return tuple(dict.fromkeys(seq))


def read(path):
    text = path.read_text("utf-8-sig")
    if path.name == "11_portraits_humanoid_hp.txt":
        # These vanilla group declarations omit the equals sign.
        text = re.sub(r"(?m)^(\s*humanoid_hp_\w+)\s+\{", r"\1 = {", text)
    return text, parse_text(text, SYNTAX, str(path), role="template")


def literal(node, text):
    return " ".join(re.sub(r"#[^\n]*", "", text[node.span.start:node.span.end]).split())


def kv(block, key):
    return [s.text for s in values(block, key) if isinstance(s, Scalar)]


def list_files(block):
    if isinstance(block, Scalar):
        return [block.text] if block.text.lower().endswith(".dds") else []
    files = []
    for n in block.items:
        if isinstance(n, Assignment):
            files.extend(list_files(n.key))
            files.extend(list_files(n.value))
        elif isinstance(n, (Block, Scalar)):
            files.extend(list_files(n))
    return distinct(files)


def scan(game):
    categories = {"robots"}
    for path in sorted((game / "common/portrait_categories").glob("*.txt")):
        _, doc = read(path)
        for _, category in fields(doc):
            categories.update(k for v in values(category, "sets") for k in words(v))
    normal = set()
    for path in sorted((game / "common/portrait_sets").glob("*.txt")):
        _, doc = read(path)
        for key, group in fields(doc):
            normal.update(k for b in values(group, "uplifted_portraits") for k in words(b))
            if key in categories:
                for b in [group, *values(group, "conditional_portraits")]:
                    normal.update(k for v in values(b, "portraits") for k in words(v))

    variants, groups, selectors = {}, {}, {}
    for path in sorted((game / "gfx/portraits/portraits").glob("*.txt")):
        text, doc = read(path)
        for b in values(doc, "portraits"):
            variants.update({k: (v, text) for k, v in fields(b)})
        for b in values(doc, "portrait_groups"):
            for k, v in fields(b):
                if k in normal and isinstance(v, Block) and values(v, "default"):
                    # Vanilla repeats several group definitions. The last ones
                    # include the leader branches and agree on their members.
                    groups[k] = v, text
    for path in sorted((game / "gfx/portraits/asset_selectors").glob("*.txt")):
        _, doc = read(path)
        selectors.update({key: list_files(b) for key, b in fields(doc) if isinstance(b, Block)})

    routes = {}
    for key in sorted(normal):
        pools = {}
        if key in groups:
            b, text = groups[key]
            for role in ("leader", "ruler"):
                for gender in GENDERS:
                    result = []
                    for scope in values(b, role):
                        for operation, entry in fields(scope):
                            triggers = values(entry, "trigger")
                            if triggers:
                                rule = literal(triggers[0], text)
                                matches = re.findall(r"\bgender = (\w+)", rule)
                                assert matches and not re.search(r"\b(NOT|NOR|AND)\b", rule), rule
                                if gender not in matches:
                                    continue
                            if operation == "set":
                                result.clear()
                            else:
                                assert operation == "add", operation
                            for p in values(entry, "portraits"):
                                for face in words(p):
                                    if face == "cyb12_m" and face not in variants:
                                        # The ruler branch uses a nonexistent generic male
                                        # face. Use this group's concrete male leader list.
                                        result.extend(pools["leader", "male"])
                                    else:
                                        result.append(face)
                    pools[role, gender] = distinct(result or kv(b, "default"))
        else:
            assert key in variants, key
            pools = {(role, g): (key,) for role in ("leader", "ruler") for g in GENDERS}
        routes[key] = pools
    return routes, variants, selectors


def asset_checker(game):
    @lru_cache(maxsize=1)
    def packed_assets():
        names = set()
        for archive in (game / "dlc").glob("*/*.zip"):
            with ZipFile(archive) as pack:
                names.update(name.lower() for name in pack.namelist() if name.lower().endswith(".dds"))
        return names

    @lru_cache(maxsize=None)
    def exists(path):
        return (game / path).is_file() or path.lower() in packed_assets()
    return exists


class Appearance:
    def __init__(self, key, definition, selectors, asset_exists):
        b, text = definition
        self.key = key
        self.hair, = kv(b, "attachment_selector")
        self.outfit, = kv(b, "clothes_selector")
        self.label = next(iter(kv(b, "custom_attachment_label")), "ATTACHMENTS")
        self.hairs = selectors.get(self.hair, ()) if self.hair != "no_texture" else ()
        self.outfits = selectors.get(self.outfit, ()) if self.outfit != "no_texture" else ()
        self.body_fields = [(k, literal(v, text)) for k, v in fields(b) if k not in
                            ("character_textures", "clothes_selector", "attachment_selector", "portrait_evolution")]
        self.textures = []
        bindings = {}
        for tex in values(b, "character_textures"):
            for n in tex.items:
                if isinstance(n, Scalar):
                    self.textures.append(n.text)
                else:
                    assert n.key.text == "tied_texture"
                    path, = kv(n.value, "texture")
                    self.textures.append(path)
                    bindings[path] = [int(x) for v in values(n.value, "evolution_variants") for x in words(v)]
        self.textures = distinct(self.textures) or (None,)
        self.stages = [dict.fromkeys(self.textures)]
        for evolution in values(b, "portrait_evolution"):
            for v in values(evolution, "variants"):
                for stage in v.items:
                    trigger, = values(stage, "trigger")
                    if literal(trigger, text) == "{ always = no }":
                        continue
                    cases = [literal(n, text) for value in values(stage, "value")
                             for n in value.items if isinstance(n, Block)]
                    layer = {}
                    for path in self.textures:
                        indices = [0] if len(cases) == 1 else bindings[path]
                        assert len(indices) == 1, (key, path, indices)
                        layer[path] = cases[indices[0]]
                    assets = (path for case in layer.values() for path in re.findall(r'"(gfx/[^"]+\.dds)"', case))
                    if all(asset_exists(path) for path in assets):
                        self.stages.append(layer)

    def visual_key(self, ti, si, hi, oi):
        base = f"rb_le_vis_{self.key}_t{ti}_s{si}"
        if hi == oi == 1:
            return base
        return f"{base}_h{hi}_o{oi}"


def eq(var, number):
    return f"check_variable = {{ which = rb_le_{var} value = {number} }}"


def setvar(var, value):
    return f"set_variable = {{ which = rb_le_{var} value = {value} }}"


def choose(branches):
    lines = []
    for i, (test, action) in enumerate(branches):
        lines.append(f"{'else_if' if i else 'if'} = {{ limit = {{ {test} }} {action} }}")
    return "\n".join(lines)


def definition(name, body):
    lines = ["\t" + line if line else "" for line in body.splitlines()]
    return name + " = {\n" + "\n".join(lines) + "\n}\n"


def names_for(routes, key, concrete):
    pools = routes[key]
    result = {}
    for context, pool in pools.items():
        if concrete is not None and concrete not in pool:
            # A scripted leader can have a concrete phenotype outside the
            # gender normally generated for that character. Honour the face.
            pool = next((p for (r, g), p in pools.items() if r == context[0]
                         and g != "indeterminable" and concrete in p), (concrete,))
        result[context] = pool
    return result


def texture_identity(path, body):
    if path and re.fullmatch(r"human_(male|female)_\d+", body):
        eye = re.search(r"_(light_brown|brown|green|blue|hazel)_eyes\.dds$", path)
        if eye:
            return "human_eye_" + eye[1]
    return path


def remap(axis, old, new):
    if old == new:
        return ""
    matches = [(i, new.index(item) + 1) for i, item in enumerate(old, 1) if item in new]
    if all(i == j for i, j in matches) and len(matches) == len(old):
        return ""
    # Assign once per branch so an old index cannot match a second branch.
    branches = [(eq(axis, i), setvar(axis, j)) for i, j in matches if j != 1]
    if not branches:
        return setvar(axis, 1)
    return choose(branches) + "\nelse = { " + setvar(axis, 1) + " }"


def pose_choices(axis, actions):
    if len(actions) == 1:
        return actions[0]
    return choose([(eq(axis, i), action) for i, action in enumerate(actions, 1)])


def make_portrait(body, hair, outfit, texture, stage, key):
    lines = [f"{field} = {value}" for field, value in body.body_fields]
    lines.append(f'attachment_selector = "{hair}"')
    lines.append(f'clothes_selector = "{outfit}"')
    if texture:
        lines.append(f'character_textures = {{ "{texture}" }}')
    if stage:
        lines.append(f'portrait_evolution = {{ variants = {{ {{ value = {{ {stage} }} trigger = {{ always = yes }} }} }} }}')
    return definition(key, "\n".join(lines))


def compile_catalogue(game):
    version = json.loads((game / "launcher-settings.json").read_text("utf-8-sig"))["rawVersion"]
    if version != "v4.6.0":
        raise ValueError(f"Review portrait definitions before rebuilding for {version}")
    routes, variants, selectors = scan(game)
    sources = {}
    for group, pools in routes.items():
        for k in distinct(x for p in pools.values() for x in p):
            assert k in variants and (k not in sources or routes[sources[k]] == pools), (k, group)
            sources.setdefault(k, group)
    exists = asset_checker(game)
    bodies = {k: Appearance(k, variants[k], selectors, exists) for k in sorted(sources)}
    family_numbers = {}
    def family_number(pool):
        if len(pool) == 1:
            a = bodies[pool[0]]
            if max(len(x) for x in (a.hairs, a.outfits, a.stages, a.textures)) < 2:
                return 0
        return family_numbers.setdefault(pool, len(family_numbers) + 1)

    recognition, family_markers, context_rules = {}, {}, {}
    for key in sorted(routes.keys() | bodies.keys()):
        group = sources.get(key, key)
        options = names_for(routes, group, key if key in bodies and key not in routes else None)
        ids = {c: family_number(p) for c, p in options.items()}
        if not any(ids.values()):
            continue
        def gender_cases(role):
            counts = {g: ids[role, g] for g in GENDERS}
            if len(set(counts.values())) == 1:
                return setvar("detected", counts["male"])
            return choose([(f"event_target:rb_le_selected_leader = {{ gender = {g} }}", setvar("detected", counts[g])) for g in GENDERS])
        action = gender_cases("leader")
        if action != gender_cases("ruler"):
            action = choose([("event_target:rb_le_selected_leader = { is_ruler = yes }", gender_cases("ruler"))]) + "\nelse = { " + action + " }"
        # Most portraits determine the family directly. Resolve the remaining
        # distinct gender/role tables once after looking up the portrait key.
        if len(set(ids.values())) == 1:
            detected = next(iter(ids.values()))
        else:
            detected = context_rules.setdefault(action, -1 - len(context_rules))
        family_markers[key] = detected
        recognition[key] = f'root = {{ {setvar("detected", detected)} }}'

    graphics, rules, profiles, setters, poses = [], [], [], [], []
    # A persistent scratch species can never match an ordinary portrait after a failed read.
    graphics.append('rb_le_empty_portrait = { entity = "portrait_human_female_entity" clothes_selector = "no_texture" attachment_selector = "no_texture" }')
    neighbors = defaultdict(set)
    ids = {key: index for index, key in enumerate(sorted(bodies), 1)}
    for pool, n in family_numbers.items():
        if len(pool) > 1:
            for a, b in zip(pool, (*pool[1:], pool[0])):
                neighbors[a].add(b)
                neighbors[b].add(a)
        if len(pool) == 1:
            actions = setvar("next_body", ids[pool[0]])
        else:
            actions = choose([(eq("pheno", j), setvar("next_body", ids[k])) for j, k in enumerate(pool, 1)])
        profiles.append(definition("if", f'limit = {{ {eq("family", n)} }}\n' + setvar("pheno_n", len(pool)) + "\n" + actions))

    fixed_layers = {}
    look_number = 0
    edited_families = []
    for k, a in bodies.items():
        if k not in recognition:
            continue
        layers = {}
        for axis, assets in (("hair", a.hairs), ("outfit", a.outfits)):
            layer_tags = []
            for asset in assets:
                if asset not in fixed_layers:
                    tag = f"rb_le_layer_{len(fixed_layers) + 1}"
                    fixed_layers[asset] = tag
                    rules.append(definition(tag, f'default = "{asset}"'))
                layer_tags.append(fixed_layers[asset])
            layers[axis] = layer_tags or ["no_texture"]
        texture_actions = []
        first_look = look_number + 1
        for ti, tex in enumerate(a.textures, 1):
            stage_actions = []
            for si, stage in enumerate(a.stages, 1):
                hair_actions = []
                for hi, hair in enumerate(layers["hair"], 1):
                    outfit_actions = []
                    for oi, outfit in enumerate(layers["outfit"], 1):
                        key = a.visual_key(ti, si, hi, oi)
                        graphics.append(make_portrait(a, hair, outfit, tex, stage[tex], key))
                        look_number += 1
                        recognition[key] = f'root = {{ {setvar("read_look", look_number)} }}'
                        outfit_actions.append(f"rb_le_paint_portrait = {{ PORTRAIT = {key} INDEX = {look_number} }}")
                    hair_actions.append(pose_choices("outfit", outfit_actions))
                stage_actions.append(pose_choices("hair", hair_actions))
            texture_actions.append(pose_choices("stage", stage_actions))
        look_range = (f"check_variable = {{ which = rb_le_read_look value >= {first_look} }} "
                      f"check_variable = {{ which = rb_le_read_look value <= {look_number} }}")
        edited_families.append(definition("if", f"limit = {{ {look_range} }}\n" + setvar("detected", family_markers[k])))
        changes = []
        for prev in sorted(neighbors[k]):
            previous = bodies[prev]
            rules_for_change = [
                remap("hair", previous.hairs, a.hairs),
                remap("outfit", previous.outfits, a.outfits),
                remap("tex", [texture_identity(p, prev) for p in previous.textures],
                     [texture_identity(p, k) for p in a.textures]),
            ]
            actions = "\n".join(rule for rule in rules_for_change if rule)
            if actions:
                changes.append((eq("body", ids[prev]), actions))
        label = {"ATTACHMENTS": 0, "HAIR_STYLE": 1, "MASK": 2, "HAT": 3}[a.label]
        limits = "\n".join(setvar(var, value) for var, value in [
            ("body", ids[k]), ("hair_kind", label), ("hair_n", max(1, len(a.hairs))),
            ("outfit_n", max(1, len(a.outfits))), ("tex_n", len(a.textures)), ("stage_n", len(a.stages)),
        ])
        paint_body = pose_choices("tex", texture_actions)
        setters.append(definition("rb_le_body_" + k, "\n".join(filter(None, [choose(changes), limits]))))
        poses.append(definition("if", f'limit = {{ {eq("next_body", ids[k])} }}\n' + paint_body))
    # The chosen body is stable throughout dispatch. Each body occurs once,
    # even when several player/leader/gender combinations share a phenotype.
    dispatch = [definition("if", f'limit = {{ {eq("next_body", ids[k])} }}\nrb_le_body_{k} = yes')
                for k in bodies if k in recognition]
    render = definition("rb_le_render_choices", "\n".join([setvar("next_body", 0), *profiles, *dispatch]))
    cases = "\n".join(f"{key} = {{ {action} }}" for key, action in recognition.items())
    switch = definition("switch", "trigger = species_portrait\n" + cases)
    resolve = [definition("if", f'limit = {{ {eq("detected", number)} }}\n{action}')
               for action, number in context_rules.items()]
    edited = definition("if", "limit = { check_variable = { which = rb_le_read_look value > 0 } }\n" + "\n".join(edited_families))
    registry = definition("rb_le_identify_portrait", "\n".join([definition("event_target:rb_le_portrait_probe", switch), edited, *resolve]))
    head = "# Generated by Instruments/RB_LE_Portraits/build.py for Stellaris 4.6.0.\n"
    return {
        "gfx/portraits/portraits/rb_le_appearances.txt": head + definition("portraits", "\n".join(graphics)),
        "gfx/portraits/asset_selectors/rb_le_layers.txt": head + "\n".join(rules),
        "common/scripted_effects/rb_le_portrait_lookup.txt": head + registry,
        "common/scripted_effects/rb_le_portrait_choices.txt": head + "\n".join([render, *setters, definition("rb_le_render_pose", "\n".join(poses))]),
    }


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--game", type=Path, required=True)
    cli.add_argument("--check", action="store_true")
    args = cli.parse_args()
    for rel, content in compile_catalogue(args.game).items():
        file = MOD / rel
        if args.check:
            if not file.exists() or file.read_text("utf-8") != content:
                raise SystemExit(f"Out of date: {rel}")
        else:
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(content, encoding="utf-8", newline="\n")
        print(rel)
