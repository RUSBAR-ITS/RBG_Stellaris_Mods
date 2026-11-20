"""Inspect code-shaped argument strings separately from the outer source AST."""

from collections import Counter
import json
from count_text import settings
from stellaris_parser.script.nodes import Assignment, Block, Source
from stellaris_parser.script.parser import parse_source
from inline_audit_helpers import describe_call, LOGIC, walk


def main():
    selected = settings()
    base = selected.output
    inventory = json.loads((base / "inline_scripts_inventory.json").read_text(encoding="utf-8"))
    syntax = selected.syntax
    rows, failures, nested, logic = [], [], [], []
    for call in inventory["calls"]:
        for argument in call["arguments"]:
            if "code_like_text" not in argument.get("features", []):
                continue
            location = {"file": call["file"], "line": argument["line"], "name": argument["name"]}
            try:
                document = parse_source(Source(argument["text"], call["file"]), syntax, specials=False)
            except Exception as error:
                failures.append({**location, "message": str(error)})
                continue
            rows.append({**location, "target": call.get("target"), "text": argument["text"],
                         "items": len(document.items),
                         "item_types": [type(n).__name__ for n in document.items]})
            for node, ancestors in walk(document.items):
                if not isinstance(node, Assignment):
                    continue
                if node.key.text.casefold() == "inline_script":
                    row = describe_call(node, argument["text"], call["file"])
                    row["line"] += argument["line"] - 1
                    row["argument_name"] = argument["name"]
                    nested.append(row)
                elif node.key.text.casefold() in LOGIC and isinstance(node.value, Block):
                    logic.append({**location, "line": argument["line"] + node.span.line - 1,
                                  "operator": node.key.text})
    report = {"count": len(rows), "names": dict(Counter(r["name"] for r in rows)),
              "top_level_item_counts": dict(Counter(r["items"] for r in rows)),
              "failures": failures, "parameters": rows, "nested_inline_calls": nested,
              "logical_blocks": logic}
    (base / "inline_code_parameters.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "parameters"}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
