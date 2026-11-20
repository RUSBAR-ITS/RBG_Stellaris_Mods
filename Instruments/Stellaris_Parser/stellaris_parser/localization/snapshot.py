"""Track read inputs and reject changes before database replacement."""

import hashlib
from pathlib import Path

from document_package.errors import BuildError
from document_package.json_io import read_json


def digest(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


class Snapshot:
    def __init__(self, report):
        self.entries = {}
        self.report = report

    def record(self, path, kind, content=None):
        path = Path(path).resolve()
        checksum = digest(path) if content is None else hashlib.sha256(content).hexdigest()
        previous = self.entries.get(path)
        if previous and previous != checksum:
            raise BuildError("input_changed", f"Input changed during processing: {path}")
        if previous is None:
            self.entries[path] = checksum
            self.report["inputs"].append({"path": str(path), "sha256": checksum, "kind": kind})
        return checksum

    def json(self, path, kind):
        self.record(path, kind)
        return read_json(path)

    def verify(self):
        for path, expected in self.entries.items():
            if digest(path) != expected:
                raise BuildError("input_changed", f"Input changed before publication: {path}")
