"""One-shot Ubuntu receiver sent over SSH. Uses only Python's standard library."""

import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import PurePosixPath
import shutil
import stat
import sys
import tarfile
from uuid import uuid4


def digest(stream):
    result = hashlib.sha256()
    for chunk in iter(lambda: stream.read(128 * 1024), b''):
        result.update(chunk)
    return result.hexdigest()


@contextmanager
def parent_directory(root, name, create):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or path.suffix != '.png' or '\\' in name:
        raise ValueError(f'Invalid destination path: {name!r}')
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(root, flags)
    try:
        for part in path.parts[:-1]:
            if create:
                try:
                    os.mkdir(part, dir_fd=fd)
                except FileExistsError:
                    pass
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd, path.name
    finally:
        os.close(fd)


def current_hash(root, name):
    try:
        with parent_directory(root, name, False) as (directory, leaf):
            flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
            with os.fdopen(os.open(leaf, flags, dir_fd=directory), 'rb') as stream:
                if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                    raise ValueError(f'Expected regular file: {name}')
                return digest(stream)
    except FileNotFoundError:
        return None


def publish(root, member, source):
    with parent_directory(root, member.name, True) as (directory, leaf):
        temp = f'.sttv-upload-{uuid4().hex}.tmp'
        fd = os.open(temp, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o666, dir_fd=directory)
        try:
            with os.fdopen(fd, 'w+b') as stream:
                shutil.copyfileobj(source, stream)
                stream.seek(0)
                if digest(stream) != member.pax_headers['STTV.sha256']:
                    raise ValueError('SHA-256 mismatch')
            os.replace(temp, leaf, src_dir_fd=directory, dst_dir_fd=directory)
        finally:
            try:
                os.unlink(temp, dir_fd=directory)
            except FileNotFoundError:
                pass


def main():
    action, root = sys.argv[1:]
    if not os.path.isabs(root) or not os.path.isdir(root):
        raise ValueError(f'Expected an existing absolute destination directory: {root}')
    if action == 'hashes':
        hashes = {name: current_hash(root, name) for name in json.load(sys.stdin.buffer)}
        print(json.dumps(hashes))
    elif action == 'publish':
        with tarfile.open(fileobj=sys.stdin.buffer, mode='r|') as archive:
            for member in archive:
                if not member.isfile():
                    raise ValueError(f'Expected regular archive entry: {member.name}')
                try:
                    with archive.extractfile(member) as source:
                        publish(root, member, source)
                except (OSError, ValueError, KeyError, tarfile.TarError) as exc:
                    raise ValueError(f'{member.name}: {exc}') from exc
                print(json.dumps(member.name), flush=True)
    else:
        raise ValueError('Unknown receiver operation')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, tarfile.TarError) as error:
        sys.exit(str(error))
