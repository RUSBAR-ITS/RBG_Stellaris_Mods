"""Select overlaid library inputs and identify exactly the bytes used in a run."""

from dataclasses import dataclass
from hashlib import file_digest, sha256
import json

from document_package.package import confined
from ..script.inlining.loader import exception_files
from ..sources import SourceFile, relative_path


def digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class LibraryFile(SourceFile):
    kind: str
    template: str | None

    def row(self, checksum):
        return {'relative': self.relative, 'path': str(self.path), 'sha256': checksum, 'kinds': [self.kind]}


def select(settings):
    jobs = []
    for kind, directory in settings.directories.items():
        files = settings.sources.collect([directory], settings.reading['pattern'])
        if kind == 'inline_script':
            for name in exception_files(settings.exceptions).values():
                relative = directory / relative_path(name)
                if relative in files:
                    continue
                for root in settings.sources.roots:
                    path = confined(root, relative)
                    if path.is_file():
                        files[relative] = SourceFile(relative.as_posix(), path, path.stat().st_size)
                        break
        for rel, file in files.items():
            template = rel.relative_to(directory).as_posix() if kind == 'inline_script' else None
            jobs.append(LibraryFile(file.relative, file.path, file.size, kind, template))
    return sorted(jobs, key=lambda job: (job.kind, job.relative))


def source_rows(jobs):
    rows = []
    for job in jobs:
        with job.path.open('rb') as stream:
            rows.append(job.row(file_digest(stream, 'sha256').hexdigest()))
    return rows
