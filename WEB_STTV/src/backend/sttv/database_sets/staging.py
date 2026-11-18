"""Deterministic identity and sequential staging without retaining all trees."""

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

from sttv.common.schema import schema_validator


def canonical_hash(value):
    digest = hashlib.sha256()
    encoder = json.JSONEncoder(sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    for chunk in encoder.iterencode(value):
        digest.update(chunk.encode('utf-8'))
    return digest.hexdigest()


class Staging:
    def __init__(self):
        self.paths = {}

    def identify(self, set_id, settings):
        for kind, path in list(self.paths.items()):
            metadata = {'kind': kind, 'set_id': set_id}
            validator = schema_validator('database.schema.json')
            validator.evolve(schema=validator.schema['properties']['dataset']).validate(metadata)
            # Add validated root metadata to the already reread, validated tree bytes.
            destination, final = settings[kind].database, None
            try:
                with path.open('rb') as source, tempfile.NamedTemporaryFile(
                        mode='wb', dir=destination.parent, prefix=destination.name + '.',
                        suffix='.tmp', delete=False) as output:
                    final = Path(output.name)
                    if source.read(2) != b'{\n':
                        raise ValueError('Staged database must begin with a formatted root object')
                    prefix = json.dumps({'dataset': metadata}, ensure_ascii=False,
                                        sort_keys=True, indent=2)[:-2] + ',\n'
                    output.write(prefix.encode('utf-8'))
                    shutil.copyfileobj(source, output)
                    output.flush()
                    os.fsync(output.fileno())
                self.paths[kind] = final
                path.unlink()
            except BaseException:
                if final is not None:
                    final.unlink(missing_ok=True)
                raise

    def publish(self, settings, report):
        for kind, path in self.paths.items():
            os.replace(path, settings[kind].database)
            report['datasets'][kind]['written'] = True

    def close(self):
        for path in self.paths.values():
            path.unlink(missing_ok=True)
