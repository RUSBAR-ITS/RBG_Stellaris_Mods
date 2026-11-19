"""Content-addressed PNG conversion with verified reuse and deduplication."""

from io import BytesIO
import hashlib
import os

from PIL import Image, __version__ as pillow_version

from sttv.common.errors import BuildError
from sttv.storage.identity import digest
from sttv.storage.settings import confined
from sttv.storage.publication import file_digest


class Images:
    def __init__(self, settings, publication, previous, snapshot, report):
        self.settings, self.publication = settings, publication
        self.snapshot, self.report = snapshot, report
        self.files, self.sources, self.cache = {}, {}, {}
        self.revision = digest({'options': settings.options, 'decoder': pillow_version, 'algorithm': 1})
        self.previous = previous if settings.options['reuse'] and previous.get('settings_revision') == self.revision else {}

    def get(self, relative, context):
        self.report['counts']['references'] += 1
        if relative in self.cache:
            return self.cache[relative]
        # Invalid paths are configuration/data errors, not missing image warnings.
        source = confined(self.settings.source, relative)
        try:
            raw = source.read_bytes()
            source_hash = self.snapshot.record(source, 'image', raw)
            old = self.previous.get('sources', {}).get(relative)
            if old and old['source_hash'] == source_hash:
                identifier = old['asset_id']
                descriptor = self.previous['files'][identifier]
                target = confined(self.settings.storage.root, descriptor['path'])
                if (target.is_file() and target.stat().st_size == descriptor['byte_size']
                        and file_digest(target) == descriptor['file_hash']):
                    self.files[identifier] = descriptor
                    self.sources[relative] = old
                    self.cache[relative] = identifier
                    self.report['counts']['reused'] += 1
                    return identifier
            with Image.open(BytesIO(raw)) as image:
                rgba = image.convert('RGBA')
                output = BytesIO()
                rgba.save(output, **self.settings.options['conversion'])
                width, height = rgba.size
            payload = output.getvalue()
        except (OSError, ValueError, NotImplementedError) as exc:
            self.report['diagnostics'].append({'severity': 'warning', 'code': 'image_unavailable',
                'source': relative, 'message': str(exc), **context})
            self.report['counts']['missing'] += 1
            self.cache[relative] = None
            return None
        identifier = hashlib.sha256(payload).hexdigest()
        path = f'{self.settings.options["directory"]}/{identifier}.png'
        target = confined(self.settings.storage.root, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if file_digest(target) != identifier:
                raise BuildError('asset_hash', f'Immutable resource is corrupt: {path}')
        else:
            temporary = self.publication.directory / f'{identifier}.png'
            with temporary.open('wb') as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, target)
            self.report['counts']['image_bytes_written'] += len(payload)
        self.files[identifier] = {'path': path, 'mime_type': 'image/png', 'file_hash': identifier,
            'byte_size': len(payload), 'width': width, 'height': height}
        self.sources[relative] = {'source_hash': source_hash, 'asset_id': identifier}
        self.cache[relative] = identifier
        self.report['counts']['converted'] += 1
        return identifier
