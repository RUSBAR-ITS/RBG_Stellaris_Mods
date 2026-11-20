"""Command-line inputs and report output for snapshot checks."""

import argparse
import json
from pathlib import Path


def arguments(description, *, profiles=False):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--variables", type=Path, required=True,
                        help="Backend variables file selecting the prepared snapshot via WORK_DIR")
    parser.add_argument("--output", type=Path, required=True, help="Directory for research reports")
    if profiles:
        parser.add_argument("--profiles", type=Path, required=True,
                            help="matrix.json from accept_stage21.py")
    args = parser.parse_args()
    if not args.variables.is_file():
        parser.error(f"Missing variables file: {args.variables}")
    args.output.mkdir(parents=True, exist_ok=True)
    return args


def save(output, name, data):
    (output / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
