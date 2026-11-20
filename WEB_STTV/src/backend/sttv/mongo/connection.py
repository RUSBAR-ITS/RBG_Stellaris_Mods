"""Open a TLS-verified, directly authenticated MongoDB client."""

import os
from pathlib import Path
from contextlib import ExitStack, contextmanager
from tempfile import TemporaryDirectory

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from document_package.errors import BuildError
from .vault import credentials


@contextmanager
def database(settings):
    profile = settings.profile
    with ExitStack() as stack:
        try:
            if 'vault' in profile:
                values = credentials(profile['vault'])
                password = values['password']
                settings.scratch.mkdir(parents=True, exist_ok=True)
                directory = stack.enter_context(TemporaryDirectory(dir=settings.scratch))
                ca = Path(directory) / 'ca.pem'
                ca.write_text(values['ca'], encoding='ascii')
            else:
                password = os.environ.get(profile['password_env'])
                if not password:
                    raise BuildError('missing_secret', 'MongoDB password environment variable is empty')
                ca = Path(profile['ca_file'])
            client = stack.enter_context(MongoClient(
                host=profile['host'], port=profile['port'], directConnection=True,
                username=profile['username'], password=password, authSource=profile['auth_source'],
                authMechanism=profile['mechanism'], tls=True, tlsCAFile=str(ca),
                serverSelectionTimeoutMS=10000, appname='sttv'))
            db = client[profile['database']]
            db.command('ping')
        except (OSError, BuildError, PyMongoError, ValueError, KeyError) as exc:
            code = exc.code if isinstance(exc, BuildError) else type(exc).__name__
            raise BuildError('mongo_connection', f'MongoDB profile {settings.name}: {code}') from None
        yield db
