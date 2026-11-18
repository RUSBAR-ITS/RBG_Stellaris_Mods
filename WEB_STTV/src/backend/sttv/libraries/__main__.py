"""Prepare or verify the configured libraries without building databases."""

import argparse
import json
from pathlib import Path

from sttv.common.paths import PRODUCT_ROOT
from sttv.sources.settings import load_settings
from sttv.common.schema import schema_operation
from .operation import add_mode_arguments, library_operation

parser = argparse.ArgumentParser(description='Prepare or reuse STTV source libraries')
parser.add_argument('--variables', default=str(PRODUCT_ROOT / 'global_variables.json'))
parser.add_argument('--config', default=str(PRODUCT_ROOT / 'config/backend.json'))
add_mode_arguments(parser)
args = parser.parse_args()

@schema_operation
def execute(args):
    settings = load_settings(Path(args.variables), Path(args.config), dataset='technologies')
    with library_operation(settings, args.library_mode) as snapshot:
        result = snapshot.report
    return result


try:
    result = execute(args)
    print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as exc:
    print(json.dumps({'status': 'failed', 'code': getattr(exc, 'code', 'library_error'), 'message': str(exc)}))
    raise SystemExit(1)
