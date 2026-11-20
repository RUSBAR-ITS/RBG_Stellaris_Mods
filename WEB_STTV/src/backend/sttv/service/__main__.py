"""Start the local database operation service explicitly."""

import argparse
from .settings import load
from .operations import Operations
from .http import create_server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config')
    options, variables, config, settings = load(parser.parse_args().config)
    operations = Operations(options, variables, config, settings)
    server = create_server(options, operations)
    print(f'STTV service: http://{options["host"]}:{options["port"]}{options["prefix"]}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        operations.close()


if __name__ == '__main__':
    main()
