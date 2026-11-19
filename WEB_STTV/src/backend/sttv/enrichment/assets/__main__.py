"""Explicit image preparation for a new or existing database set."""

import argparse
import json
from .operation import prepare_assets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variables')
    parser.add_argument('--config')
    parser.add_argument('--storage')
    args = parser.parse_args()
    result = prepare_assets(args.variables, args.config, storage_path=args.storage)
    print(json.dumps({key: result.get(key) for key in ('status', 'counts', 'timings', 'diagnostics')}, ensure_ascii=False))
    raise SystemExit(0 if result['status'] == 'success' else 1)


if __name__ == '__main__':
    main()
