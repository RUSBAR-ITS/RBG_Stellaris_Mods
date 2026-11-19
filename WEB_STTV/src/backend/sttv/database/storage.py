"""Explicit validation of a standalone parse document."""

from sttv.common.schema import schema_operation


@schema_operation
def read_database(path):
    """Load a persisted tree without loading game or parser configuration."""
    from sttv.common.json_io import read_json
    from .validation import validate_database
    value = read_json(path)
    validate_database(value)
    return value
