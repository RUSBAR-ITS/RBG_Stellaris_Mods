"""Select the runtime profile from a component's own configuration."""

from dataclasses import dataclass
from pathlib import Path
import re

from document_package.errors import BuildError
from document_package.json_io import read_json


@dataclass(frozen=True)
class Settings:
    name: str
    profile: dict
    options: dict
    scratch: Path


def settings(path, override=None):
    path = Path(path)
    options = read_json(path)
    mongo = options['mongodb']
    name = override or mongo['active_profile']
    if name not in mongo['profiles']:
        raise BuildError('unknown_profile', f'Unknown MongoDB profile: {name}')
    profile = mongo['profiles'][name]
    for key in ('host', 'port', 'database', 'username', 'auth_source', 'mechanism'):
        if not profile.get(key):
            raise BuildError('invalid_profile', f'MongoDB profile {name}: missing {key}')
    if profile['mechanism'] != 'SCRAM-SHA-256':
        raise BuildError('invalid_profile', f'MongoDB profile {name}: unsupported mechanism')
    if 'vault' not in profile and not (profile.get('ca_file') and profile.get('password_env')):
        raise BuildError('invalid_profile', f'MongoDB profile {name}: missing CA or password reference')
    if 'ca_file' in profile:
        profile = {**profile, 'ca_file': str((path.parent / profile['ca_file']).resolve())}
    return Settings(name, profile, options, (path.resolve().parent / options['scratch_directory']).resolve())


def collection_name(name):
    if not isinstance(name, str) or not re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_]*', name):
        raise BuildError('invalid_collection', f'Invalid collection: {name!r}')
    return name
