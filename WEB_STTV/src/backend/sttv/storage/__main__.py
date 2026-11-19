"""Audit prepared documents without rebuilding them."""

import argparse
import json
from pathlib import Path

from sttv.common.persistence import save_json
from sttv.common.paths import REPOSITORY_ROOT, PRODUCT_ROOT, PRODUCT_DIRECTORIES
from sttv.common.errors import BuildError
from .audit import audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['audit'])
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    path = args.report.resolve()
    if (not path.is_relative_to(REPOSITORY_ROOT) or path == args.manifest.resolve()
            or any(path.is_relative_to(PRODUCT_ROOT / p) for p in PRODUCT_DIRECTORIES)
            or path.is_relative_to(REPOSITORY_ROOT / '.git')
            or path.is_relative_to(args.manifest.resolve().parent)):
        raise BuildError('unsafe_output', 'Audit report must be in workspace outside the set and protected files')
    result = audit(args.manifest)
    save_json(path, result, 'storage_report.schema.json')
    print(json.dumps({k: result[k] for k in ('status', 'snapshot_revision', 'timings', 'diagnostics')}))
    return 0 if result['status'] == 'success' else 1


if __name__ == '__main__':
    raise SystemExit(main())
