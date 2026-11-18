"""Own configured output directories even when callers choose different manifests."""

import os
from contextlib import contextmanager

from sttv.common.errors import BuildError
from sttv.common.paths import output_path


@contextmanager
def ownership(settings):
    names = [row['output'] for row in settings.libraries['libraries']]
    names.extend(settings.libraries[key] for key in ('manifest', 'report'))
    directories = {output_path(settings.work, name, settings.protected).parent for name in names}
    owned = []
    try:
        for directory in sorted(directories):
            directory.mkdir(parents=True, exist_ok=True)
            lock = directory / '.sttv-libraries.lock'
            try:
                descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError as exc:
                raise BuildError('library_busy', f'Library directory is already owned: {lock}') from exc
            owned.append(lock)
            try:
                os.write(descriptor, str(os.getpid()).encode('ascii'))
            finally:
                os.close(descriptor)
        yield
    finally:
        for lock in reversed(owned):
            lock.unlink(missing_ok=True)
