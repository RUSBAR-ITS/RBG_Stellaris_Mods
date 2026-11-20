"""Inventory every vanilla inline call and template using the existing parser."""

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
from count_text import PRODUCT, read_json, settings
from stellaris_parser.script.nodes import Assignment, Source
from stellaris_parser.script.parser import parse_source
from inline_audit_helpers import describe_call, describe_template, walk


def main():
    selected = settings("Optional previous inline inventory JSON for comparison on identical sources")
    game, syntax = selected.game, selected.syntax
    manifest = read_json(selected.output / 'source_manifest.json')
    protected = [*sorted((PRODUCT / "script").rglob("*.py")),
                 *sorted((PRODUCT / "config").rglob("*.json")),
                 *sorted((PRODUCT / "schemas").rglob("*.json"))]
    baseline = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    calls, templates, failures, changed = [], {}, [], []
    prefix = "common/inline_scripts/"
    parsed = 0
    for entry in manifest:
        relative = entry["file"]
        raw = (game / relative).read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
            changed.append(relative)
        text = raw.decode("utf-8-sig")
        is_template = relative.startswith(prefix)
        if entry["status"] != "counted" or not (is_template or re.search(r"(?i)\binline_script\b", text)):
            continue
        try:
            document = parse_source(Source(text, relative), syntax, specials=False)
        except Exception as error:
            failures.append({"file": relative, "message": str(error)})
            continue
        parsed += 1
        if is_template:
            templates[relative] = describe_template(document)
        for node, ancestors in walk(document.items):
            if isinstance(node, Assignment) and node.key.text.casefold() == "inline_script":
                row = describe_call(node, text, relative)
                row["parents"] = [a.key.text for a in ancestors if isinstance(a, Assignment)]
                calls.append(row)
        if parsed % 200 == 0:
            print(f"Parsed {parsed} relevant files", flush=True)

    argument_features, path_features, argument_names = Counter(), Counter(), Counter()
    resolution, references, edges, issues = Counter(), Counter(), defaultdict(set), []
    for call in calls:
        for arg in call["arguments"]:
            argument_names[arg["name"]] += 1
            argument_features.update(arg.get("features", [arg["type"]]))
        path = call.get("path")
        if not path or path["type"] != "Scalar":
            call["resolution"] = "invalid_path_form"
        elif path["parameters"]:
            call["resolution"] = "parameterized_path"
        else:
            relative = prefix + path["text"] + ".txt"
            call["target"] = relative
            call["resolution"] = "exists" if (game / relative).is_file() else "missing_txt"
            references[relative] += 1
            if call["file"].startswith(prefix):
                edges[call["file"]].add(relative)
            if call["resolution"] == "missing_txt":
                call["extensionless_exists"] = (game / (prefix + path["text"])).is_file()
        if path:
            path_features.update(path.get("features", [path["type"]]))
        resolution[call["resolution"]] += 1
        if (call["type"] == "Block" and (len(call["script_fields"]) != 1
                or call["duplicate_arguments"] or call["duplicate_arguments_casefold"]
                or call.get("other_children"))):
            issues.append({"file": call["file"], "line": call["line"]})
    cycles, longest = [], []

    def visit(file, trail):
        nonlocal longest
        if file in trail:
            cycles.append([*trail, file])
            return
        trail = [*trail, file]
        if len(trail) > len(longest):
            longest = trail
        for target in sorted(edges.get(file, ())):
            visit(target, trail)

    for file in sorted(edges):
        visit(file, [])
    for file, template in templates.items():
        template["static_reference_count"] = references[file]
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == digest for p, digest in baseline.items())
    end_changes = [r["file"] for r in manifest if hashlib.sha256((game / r["file"]).read_bytes()).hexdigest() != r["sha256"]]
    assert not failures and not changed and not end_changes
    summary = {"corpus_files": len(manifest), "parsed_relevant_files": parsed,
               "calls": len(calls), "call_files": len({c["file"] for c in calls}),
               "call_forms": dict(Counter(c["type"] for c in calls)),
               "key_spellings": dict(Counter(c["key"] for c in calls)),
               "operators": dict(Counter(c["operator"] for c in calls)),
               "argument_occurrences": sum(argument_names.values()),
               "argument_name_count": len(argument_names), "argument_features": dict(argument_features),
               "path_features": dict(path_features), "resolution": dict(resolution),
               "distinct_static_targets": len(references), "templates_txt": len(templates),
               "templates_with_content": sum(t["has_content"] for t in templates.values()),
               "templates_with_no_static_calls": [p for p, t in templates.items() if t["has_content"] and not t["static_reference_count"]],
               "calls_inside_templates": sum(c["file"].startswith(prefix) for c in calls),
               "templates_with_calls": len({c["file"] for c in calls if c["file"].startswith(prefix)}),
               "templates_with_static_calls": len(edges), "static_cycles": cycles,
               "longest_static_chain": longest,
               "templates_with_conditionals": sum(bool(t["conditionals"]) for t in templates.values()),
               "templates_with_defaults": sum(any(p["default"] is not None for p in t["placeholders"]) for t in templates.values()),
               "templates_with_logical_blocks": sum(bool(t["logical_blocks"]) for t in templates.values()),
               "block_shape_issues": issues, "parse_failures": failures,
               "source_hashes_unchanged": True, "product_code_and_config_unchanged": True}
    if selected.reference:
        previous = read_json(selected.reference)["calls"]
        def signatures(rows):
            return Counter((row["file"], row["line"], row["source"]) for row in rows)
        assert signatures(calls) == signatures(previous)
        summary["calls_match_previous_audit"] = True
    output = selected.output / "inline_scripts_inventory.json"
    output.write_text(json.dumps({"summary": summary, "argument_names": dict(argument_names),
                                  "calls": calls, "templates": templates, "protected_baseline": baseline},
                                 ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
