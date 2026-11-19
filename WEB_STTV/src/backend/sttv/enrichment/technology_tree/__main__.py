"""Explicit local entry point; transport and UI integration are separate."""

import argparse
import json
from . import enrich_technology_tree


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('variables', 'config', 'combination'):
        parser.add_argument('--' + key)
    parser.add_argument('--recalculate', action='store_true')
    args = parser.parse_args()
    report = enrich_technology_tree(args.variables, args.config, args.combination, recalculate=args.recalculate)
    print(json.dumps({key: report[key] for key in ('status', 'action', 'database_written', 'counts', 'timings', 'error')},
                     ensure_ascii=False, indent=2))
    return 1 if report['status'] == 'failed' else 0


if __name__ == '__main__':
    raise SystemExit(main())
