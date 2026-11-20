"""Loopback service configuration."""

from .helpers import TEXT, RELATIVE, LINE, obj, array


def configuration():
    return obj({'host': TEXT, 'port': {'type': 'integer', 'minimum': 1, 'maximum': 65535},
        'prefix': {'type': 'string', 'pattern': '^/[a-z0-9/_-]+[a-z0-9]$'},
        'variables': RELATIVE, 'tree_config': RELATIVE, 'allowed_origins': array(TEXT, uniqueItems=True),
        'max_request_bytes': LINE, 'history_limit': LINE, 'poll_interval_ms': LINE})
