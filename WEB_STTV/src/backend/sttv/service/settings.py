"""Keep service addresses and the registered set outside transport code."""

import ipaddress
from pathlib import Path

from sttv.common.paths import PRODUCT_ROOT
from sttv.common.json_io import read_json
from sttv.common.schema import validate_schema
from sttv.common.errors import BuildError
from sttv.storage.settings import confined
from sttv.enrichment.technology_tree.settings import load as tree_settings


def load(path=None):
    options = read_json(Path(path or PRODUCT_ROOT / 'config/service.json'))
    validate_schema(options, 'service.schema.json')
    if not ipaddress.ip_address(options['host']).is_loopback:
        raise BuildError('service_address', 'The service must listen on a loopback address')
    variables = confined(PRODUCT_ROOT, options['variables'])
    config = confined(PRODUCT_ROOT, options['tree_config'])
    settings = tree_settings(variables, config)
    return options, variables, config, settings
