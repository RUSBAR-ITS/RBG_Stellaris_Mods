"""Shared dataset roles and root definition identity rules."""

from .json_io import read_json
from .paths import PRODUCT_ROOT

REGISTRY_PATH = PRODUCT_ROOT / 'config/datasets.json'
REGISTRY = read_json(REGISTRY_PATH)
KINDS = tuple(REGISTRY['datasets'])


def definition(kind):
    return REGISTRY['datasets'][kind]
