"""Command-line entry point for database building with an explicit rule profile."""

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from sttv.builder import build
from sttv.common.paths import PRODUCT_ROOT


def main():
    parser = argparse.ArgumentParser(description="Build the Stellaris technology database.")
    parser.add_argument("--variables", type=Path,
                        default=PRODUCT_ROOT / "global_variables.json")
    parser.add_argument("--config", type=Path,
                        default=PRODUCT_ROOT / "config" / "backend.json")
    arguments = parser.parse_args()
    result = build(arguments.variables, arguments.config)
    stream = sys.stdout if result["status"] == "success" else sys.stderr
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2), file=stream)
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
