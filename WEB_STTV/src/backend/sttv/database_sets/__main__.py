"""Build the configured set only on an explicit command."""

import argparse
import json

from .operation import build_database_set

def main():
    parser = argparse.ArgumentParser(description='Build the configured localized STTV database set')
    parser.add_argument('--variables')
    parser.add_argument('--config')
    parser.add_argument('--prepare-assets', action='store_true')
    from sttv.libraries.operation import add_mode_arguments
    add_mode_arguments(parser)
    arguments = parser.parse_args()
    result = build_database_set(arguments.variables, arguments.config, library_mode=arguments.library_mode,
                                prepare_images=arguments.prepare_assets)
    print(json.dumps({key: result[key] for key in ('status', 'set_id', 'datasets', 'diagnostics', 'seconds')},
                     ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['status'] == 'success' else 1)


if __name__ == "__main__":
    main()
