"""Check documentation links, headings, and embedded JSON without source writes."""

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("project", type=Path, help="Project directory containing Markdown files and optional Docs/")
root = parser.parse_args().project.resolve()
if not root.is_dir():
    parser.error(f"Missing project directory: {root}")
files = sorted(root.glob("*.md")) + sorted((root / "Docs").glob("*.md"))
errors = []
anchors = {}
texts = {}
for path in files:
    text = path.read_text(encoding="utf-8-sig")
    texts[path.resolve()] = text
    clean = re.sub(r"\x60{3}.*?\x60{3}", "", text, flags=re.S)
    headings = re.findall(r"^#{1,6} (.+)$", clean, re.M)
    anchors[path.resolve()] = {
        re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-") for heading in headings
    }
    toc_marker = "## " + ("Contents" if path.stem.endswith("_EN") else "\u041e\u0433\u043b\u0430\u0432\u043b\u0435\u043d\u0438\u0435")
    if toc_marker not in text[:500]:
        errors.append(f"{path.name}: missing opening contents")
    toc = text.partition(toc_marker)[2].split("\n## ", 1)[0]
    for heading in headings[2:]:
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        if f"(#{slug})" not in toc:
            errors.append(f"{path.name}: missing TOC entry {heading}")
    for block in re.findall(r"\x60{3}json\s*\n(.*?)\n\x60{3}", text, re.S):
        try:
            json.loads(block)
        except ValueError as exc:
            errors.append(f"{path.name}: invalid JSON block: {exc}")
for path in files:
    text = texts[path.resolve()]
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if "://" in target or target.startswith("mailto:"):
            continue
        file, _, fragment = unquote(target).partition("#")
        destination = (path.parent / file).resolve() if file else path.resolve()
        if not destination.exists():
            errors.append(f"{path.name}: missing target {target}")
        elif fragment and destination in anchors and fragment not in anchors[destination]:
            errors.append(f"{path.name}: missing anchor {target}")
for path in files:
    if not path.stem.endswith("_RU"):
        continue
    counterpart = path.with_name(path.name.replace("_RU.md", "_EN.md"))
    if counterpart not in files:
        errors.append(f"{path.name}: missing English counterpart")
    elif len(re.findall(r"^#{1,6} ", texts[path.resolve()], re.M)) != len(
            re.findall(r"^#{1,6} ", texts[counterpart.resolve()], re.M)):
        errors.append(f"{path.name}: language heading counts differ")
print(json.dumps({"markdown_files": len(files), "errors": errors}, ensure_ascii=True, indent=2))
raise SystemExit(bool(errors))
