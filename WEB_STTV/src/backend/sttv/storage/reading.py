"""Read and hash the same byte stream, releasing unrelated root objects."""

import codecs
import hashlib

from sttv.common.errors import BuildError
from .stream import Stream
from .objects import object_row


class HashedText:
    def __init__(self, handle):
        self.handle, self.digest, self.bytes = handle, hashlib.sha256(), 0
        self.decoder = codecs.getincrementaldecoder('utf-8')('strict')

    def read(self, size):
        while True:
            raw = self.handle.read(size)
            self.digest.update(raw)
            self.bytes += len(raw)
            text = self.decoder.decode(raw, final=not raw)
            if text or not raw:
                return text


def read(path, kind, descriptor, expected_objects, extract=None, full=False):
    try:
        return _read(path, kind, descriptor, expected_objects, extract, full)
    except Exception as exc:
        exc.context = {**getattr(exc, 'context', {}), 'database': kind,
            'document_id': descriptor['document_id'], 'source': descriptor['source'],
            'path': str(path), 'pointer': getattr(exc, 'field_path', None)}
        raise


def _read(path, kind, descriptor, expected_objects, extract, full):
    before = signature(path)
    if before[0] != descriptor['byte_size']:
        raise BuildError('document_size', f'Unexpected document size: {path}')
    header, objects, result, count = {}, [], [], 0
    with path.open('rb') as handle:
        hashed = HashedText(handle)
        stream = Stream(hashed)
        for key in stream.members():
            if key == 'items':
                for index in stream.indices():
                    node = stream.value()
                    pointer = f'/items/{index}'
                    row = object_row(kind, descriptor['document_id'], pointer, node)
                    if row is not None:
                        objects.append(row)
                    if full:
                        result.append(node)
                    elif extract is not None:
                        value = extract(pointer, node)
                        if value is not None:
                            result.append(value)
                    count += 1
            elif key == 'metadata' and not full:
                stream.raw(retain=False)
                header[key] = None
            else:
                header[key] = stream.value()
        if stream.peek():
            raise BuildError('json_read_error', f'Trailing JSON data: {path}')
    if signature(path) != before:
        raise BuildError('changed_input', f'Document changed while reading: {path}')
    actual = hashed.digest.hexdigest()
    if actual != descriptor['file_hash']:
        error = BuildError('document_hash', f'{path}: expected {descriptor["file_hash"]}, actual {actual}')
        error.context = {'expected_hash': descriptor['file_hash'], 'actual_hash': actual}
        raise error
    expected = {'format': 'sttv.parse_document', 'format_version': 1, 'database': kind,
                'document_id': descriptor['document_id'], 'source': descriptor['source']}
    if (set(header) != {*expected, 'metadata'} or any(header.get(k) != v for k, v in expected.items())
            or count != descriptor['item_count'] or objects != expected_objects):
        raise BuildError('document_index', f'Document envelope or object index disagrees with manifest: {path}')
    if full:
        header['items'] = result
        result = header
    return result, {'bytes': hashed.bytes, 'signature': before}


def signature(path):
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_ino
