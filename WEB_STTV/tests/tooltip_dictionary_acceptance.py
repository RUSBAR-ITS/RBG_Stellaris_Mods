"""Verify the bilingual condition templates against the published game and localization API."""

import argparse
import json
import re
from collections import Counter
from functools import partial
from pathlib import Path
from string import Formatter
from urllib.request import Request, urlopen

from stellaris_parser.localization.reader import read_entries
from stellaris_parser.localization.snapshot import Snapshot
from sttv_loader.connection import database
from sttv_loader.settings import settings
from sttv_server.config import load_config
from sttv_server.database import selected_strings
from sttv_server.localization import determine_key
from sttv_server.tree.ast import fields, scalar
from sttv_server.tree.dlcs import catalog
from sttv_server.tree.inputs import records
from tooltip_expression_checks import example_phrases, inspect, synthetic_checks


PROJECT = Path(__file__).resolve().parents[1]
SECTIONS = ("prerequisites", "potential", "allow", "weight_modifier")
REFERENCE = re.compile(r"\$([\w.:-]+)\$")


def templates(language):
    directory, header = {"ru": ("russian", "l_russian"), "en": ("english", "l_english")}[language]
    result = {}
    for section in ("conditions", "scopes", "expressions"):
        path = PROJECT / "localization" / directory / f"sttv_tooltip_{section}_l_{directory}.yml"
        for key, value, _ in read_entries(path, header, "utf-8-sig", Snapshot({"inputs": []})):
            if key in result or not value or not key.startswith("sttv_tooltip_"):
                raise ValueError(f"Invalid template in {path}: {key}")
            result[key] = value
    return result


def slots(text):
    return sorted(field for _, field, _, _ in Formatter().parse(text) if field is not None)


def published(url, language, keys):
    payload = json.dumps({"language": language, "keys": sorted(keys)}).encode()
    request = Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=15) as response:
        data = json.load(response)
    result = {row["key"]: row["text"] for row in data["items"]}
    if data["language"] != language or set(result) != set(keys) or not all(result.values()):
        raise ValueError(f"Incomplete {language} lookup")
    return result


def verify_templates(url):
    sources = {language: templates(language) for language in ("ru", "en")}
    _, scopes, _ = inventory()
    if sources["ru"].keys() != sources["en"].keys():
        raise ValueError("The two languages have different template keys")
    for key, text in sources["en"].items():
        if slots(text) != slots(sources["ru"][key]):
            raise ValueError(f"Placeholder mismatch: {key}")
    translated = {}
    for language, table in sources.items():
        refs = {ref for text in table.values() for ref in REFERENCE.findall(text)}
        examples = {
            "has_technology": {"technology": "tech_titans"},
            "has_origin": {"origin": "origin_necrophage"},
            "has_trait_species": {"trait": "trait_necrophage"},
            "has_policy_flag": {"policy": "policy_robot_pop_policy", "option": "robot_pops_outlawed"},
            "has_seen_any_bypass": {"bypass": "HYPER_RELAY_GALACTIC"},
            "owns_any_bypass": {"bypass": "HYPER_RELAY_GALACTIC"},
            "exists": {"target": "sttv_tooltip_this"},
            "is_same_value": {"target": "sttv_tooltip_prev"},
        }
        names = {key for arguments in examples.values() for key in arguments.values()}
        names.update(("councilor_storm_callers", "councilor_storm_callers_megacorp"))
        names.update(("tech_battleships", "tech_stinger_growth_2", "tech_starbase_5", "tech_arkship_tier_3",
                      "tech_zero_point_power", "tech_stingers", "origin_storm_chasers"))
        values = published(url, language, set(table) | refs | names)
        translated[language] = values
        for key, text in table.items():
            expected = REFERENCE.sub(lambda match: values[match[1]], text)
            if values[key] != expected or "$" in expected:
                raise ValueError(f"Published template or game reference differs: {language}/{key}")
        for name in scopes | {"always_no"}:
            arguments = {"calc_true_if": ["comparison", "value"], "exists": ["target"],
                         "is_same_value": ["target"]}.get(name, [])
            if slots(values["sttv_tooltip_" + name]) != arguments:
                raise ValueError(f"Unexpected scope arguments: {language}/{name}")
        if values["sttv_tooltip_always_no"] == values["sttv_tooltip_always"]:
            raise ValueError(f"Unconditional yes and no have the same label: {language}")
        phrases = []
        for name, arguments in examples.items():
            template = values["sttv_tooltip_" + name]
            if set(slots(template)) != set(arguments):
                raise ValueError(f"Unexpected arguments for {language}/{name}")
            phrases.append(template.format(**{arg: values[key] for arg, key in arguments.items()}))
        if len(set(phrases)) != len(phrases):
            raise ValueError(f"Distinct checks have identical example descriptions: {language}")
    return set(sources["en"]), translated


def inventory():
    spec = (PROJECT / "src/server/Docs/TZ_TOOLTIP_DICTIONARY_EN.md").read_text(encoding="utf-8")
    conditions, scopes, other = set(), set(), set()
    for heading, body in re.findall(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", spec, re.M | re.S):
        group = {"Game conditions": conditions, "Scopes and general checks": scopes}.get(heading, other)
        for line in body.splitlines():
            if line.startswith("|"):
                group.update(re.findall(r"`([\w?]+)`", line))
    if not conditions or not scopes or not other:
        raise ValueError("Missing condition inventory in the dictionary specification")
    return conditions, scopes, other


def walk(node):
    if node["kind"] == "assignment":
        yield node["key"]["text"], node["value"]
    for name, value in node.items():
        if name == "key":
            continue
        if isinstance(value, dict):
            yield from walk(value)
        elif isinstance(value, list):
            for child in value:
                yield from walk(child)


def scope_examples(db, translated):
    """Follow real direct children, including the weight rule that owns the Titans check."""
    cases = {
        "tech_titans": ("any_neighbor_country",),
        "tech_arcane_deciphering": ("federation", "any_member"),
        "tech_mega_engineering": ("any_owned_nonprimary_starbase", "solar_system", "space_owner?"),
    }
    result = {}
    for record in records(db, "technologies", ["weight_modifier"], {"_id": {"$in": list(cases)}}):
        tech = record["id"]
        chain = cases[tech]
        for block in fields(record["body"], "weight_modifier"):
            for modifier in fields(block, "modifier"):
                nodes = [modifier]
                for scope in chain:
                    nodes = [child for parent in nodes for child in fields(parent, scope)]
                if not any(scalar(node, "has_technology") == tech for node in nodes):
                    continue
                if tech == "tech_titans" and scalar(modifier, "factor") != "10":
                    raise ValueError("Unexpected Titans weight multiplier")
                result[tech] = list(chain)
    if result != {tech: list(chain) for tech, chain in cases.items()}:
        raise ValueError(f"Expected scoped technology checks are missing: {result}")
    titans = {}
    for language, text in translated.items():
        titans[language] = [text["sttv_tooltip_any_neighbor_country"],
                            text["sttv_tooltip_has_technology"].format(technology=text["tech_titans"])]
    return {"scope_paths_to_has_technology": result, "tech_titans": titans}


def survey(db, keys, translated):
    conditions, scopes, remaining = inventory()
    in_dictionary = conditions | scopes
    rules = load_config(PROJECT / "src/server/config/server.json")["key_rules"]
    seen = set()
    technical_flags, unknown = {}, {}
    expression_counts, samples = Counter(), {}
    sample_ids = {"tech_titans", "tech_mega_engineering", "tech_synthetic_leaders",
                  "tech_crystal_armor_1", "tech_storm_manipulation"}
    thresholds = {}
    technology_count = 0
    for record in records(db, "technologies", SECTIONS):
        technology_count += 1
        if record["id"] in sample_ids:
            samples[record["id"]] = record["body"]
        for section in record["body"]["items"]:
            name = section["key"]["text"]
            example = {"technology": record["id"], "section": name}
            unhandled = {}
            inspect(section["value"], (name,), in_dictionary, keys, expression_counts, unhandled)
            for key, detail in unhandled.items():
                unknown.setdefault(key, {**example, **detail})
            for key, value in walk(section["value"]):
                if key in in_dictionary:
                    seen.add(key)
                    if key in ("has_country_flag", "has_global_flag"):
                        technical_flags.setdefault(value["text"], example)
                    label = key + "_no" if value.get("text") == "no" else key
                    if determine_key(rules, "tooltip_condition", label) not in keys:
                        unknown.setdefault(label, example)
                    if key == "calc_true_if":
                        amounts = [item for item in value["items"] if item.get("key", {}).get("text") == "amount"]
                        if len(amounts) != 1 or amounts[0]["value"].get("kind") != "scalar":
                            raise ValueError(f"Invalid calc_true_if threshold: {example}")
                        amount = amounts[0]
                        comparison, number = amount["operator"], amount["value"]["text"]
                        if (comparison, number) not in thresholds:
                            threshold = {"comparison": comparison, "value": number}
                            labels = {lang: text["sttv_tooltip_calc_true_if"].format(**threshold)
                                      for lang, text in translated.items()}
                            thresholds[comparison, number] = {**example, "threshold": threshold,
                                                             "conditions": len(value["items"]) - 1, **labels}
                elif key not in remaining:
                    unknown.setdefault(key, example)
    if not technology_count or not (seen & conditions) or not (seen & scopes):
        raise ValueError("No subject conditions found in the published technologies")
    missing = sorted(key for key in conditions | scopes if determine_key(rules, "tooltip_condition", key) not in keys)
    examples = scope_examples(db, translated)
    examples["calc_true_if"] = list(thresholds.values())
    dlcs = catalog(db, rules, partial(selected_strings, db.localization))
    apocalypse, = [dlc["name"] for dlc in dlcs["items"] if dlc["id"] == "dlc017"]
    examples["expressions"] = example_phrases(samples, translated, apocalypse)
    synthetic_checks(in_dictionary, keys)
    expression_keys = {path[-1] for path in expression_counts if path[0] in ("assignment", "argument")}
    for key in remaining - expression_keys:
        missing.append(key)
    return {"technologies": technology_count, "templates_per_language": len(keys),
            "subject_conditions_seen": len(seen & conditions), "scopes_and_general_checks_seen": len(seen & scopes),
            "expression_keys_seen": len(expression_keys), "expression_counts": {
                "/".join(path): count for path, count in sorted(expression_counts.items())},
            "missing_templates": sorted(missing), "examples": examples, "new_or_unhandled": unknown,
            "flags_shown_by_id": technical_flags}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lookup-url", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    keys, translated = verify_templates(args.lookup_url)
    with database(settings(PROJECT / "config/loader.json", "network")) as db:
        report = survey(db, keys, translated)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{report['subject_conditions_seen']} conditions, {report['scopes_and_general_checks_seen']} "
          f"scopes and general checks, {report['expression_keys_seen']} expression keys, "
          f"{len(keys)} templates per language")
    if report["missing_templates"] or report["new_or_unhandled"]:
        raise SystemExit(f"Review dictionary coverage in {args.report}")
