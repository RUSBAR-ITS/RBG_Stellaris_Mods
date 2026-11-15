"""Noninteractive localization entry point for development and automation."""

import argparse
import json

from .operation import enrich_localization


def main():
    parser = argparse.ArgumentParser(description="Enrich a persisted technology database with RU/EN text")
    parser.add_argument("--variables", help="Global variables JSON path")
    parser.add_argument("--config", help="Localization configuration JSON path")
    args = parser.parse_args()
    report = enrich_localization(args.variables, args.config)
    print(json.dumps({key: report[key] for key in
                     ("status", "database_written", "paths", "counts", "seconds", "diagnostics")},
                     ensure_ascii=False, indent=2))
    return int(report["status"] != "success")


if __name__ == "__main__":
    raise SystemExit(main())
