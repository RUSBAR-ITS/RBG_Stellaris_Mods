"""Publish immutable documents before atomically switching the manifest."""

import hashlib
import os
from pathlib import Path
import shutil
from tempfile import mkdtemp

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.paths import REPOSITORY_ROOT
from .identity import FORMATTED, digest
from .manifest import check
from .settings import confined


def file_digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


class Publication:
    def __init__(self, settings):
        self.settings = settings
        self.directory = None
        self.lock = settings.root / '.storage.lock'
        self.handle = None
        self.published = False
        self.written_bytes = 0
        self.new_files = []

    def __enter__(self):
        self.settings.root.mkdir(parents=True, exist_ok=True)
        try:
            self.handle = self.lock.open('x', encoding='utf-8')
        except FileExistsError as exc:
            raise BuildError('storage_busy', f'Set is already being written: {self.settings.root}') from exc
        try:
            self.handle.write(str(os.getpid()))
            self.handle.flush()
            self.before = file_digest(self.settings.manifest) if self.settings.manifest.exists() else None
            self.configs = {path: file_digest(path) for path in self.settings.config_files}
            self.settings.staging.mkdir(parents=True, exist_ok=True)
            if self.settings.staging.drive != self.settings.root.drive:
                raise BuildError('storage_filesystem', 'Staging and set must be on the same filesystem')
            self.directory = Path(mkdtemp(prefix='operation-', dir=self.settings.staging)).resolve()
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def accept(self, fragment, kind):
        source = Path(fragment['path']).resolve()
        if not source.is_relative_to(REPOSITORY_ROOT):
            raise BuildError('unsafe_output', 'Prepared documents must be inside the workspace')
        descriptor = dict(fragment['descriptor'])
        descriptor['path'] = f'{self.settings.documents}/{kind}/{descriptor["document_id"]}/{descriptor["file_hash"]}.json'
        target = confined(self.settings.root, descriptor['path'])
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.stat().st_size != descriptor['byte_size'] or file_digest(target) != descriptor['file_hash']:
                raise BuildError('document_hash', f'Existing immutable version is corrupt: {target}')
            if source != target:
                source.unlink()
        else:
            os.replace(source, target)
            self.new_files.append(descriptor['path'])
            self.written_bytes += descriptor['byte_size']
        return {'descriptor': descriptor, 'objects': fragment['objects']}

    def publish(self, manifest, verify=None):
        check(manifest)
        temporary = self.settings.manifest.with_name(self.settings.manifest.name + '.partial')
        try:
            with temporary.open('w', encoding='utf-8', newline='\n') as handle:
                for chunk in FORMATTED.iterencode(manifest):
                    handle.write(chunk)
                handle.write('\n')
                handle.flush()
                os.fsync(handle.fileno())
            if verify:
                verify()
            current = file_digest(self.settings.manifest) if self.settings.manifest.exists() else None
            if current != self.before or any(file_digest(p) != h for p, h in self.configs.items()):
                raise BuildError('changed_input', 'Manifest or storage configuration changed before publication')
            if current is not None and digest(read_json(self.settings.manifest)) == digest(manifest):
                return False
            os.replace(temporary, self.settings.manifest)
            self.published = True
            return True
        finally:
            temporary.unlink(missing_ok=True)

    def __exit__(self, *_):
        if self.directory is not None:
            if self.directory.parent != self.settings.staging.resolve() or not self.directory.name.startswith('operation-'):
                raise BuildError('unsafe_output', 'Refusing cleanup outside owned staging directory')
            shutil.rmtree(self.directory)
            self.directory = None
        if self.handle is not None:
            self.handle.close()
            self.lock.unlink(missing_ok=True)
            self.handle = None
