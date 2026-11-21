"""Drop the explicitly named test database from the workstation using its maintenance identity."""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from pymongo import MongoClient

from sttv_loader.settings import settings
from sttv_loader.vault import vault_request


def drop(config, name):
    options = settings(Path(config).resolve(), 'network')
    target = options.profile
    admin = options.options['maintenance']
    if name != admin['drop_database'] or name != target['database'] or name in ('admin', 'local', 'config'):
        raise ValueError('Maintenance database does not match the requested loader target')
    vault = target['vault']
    token = vault_request(vault, 'POST', f'auth/{vault["auth_mount"]}/login')['auth']['client_token']
    try:
        identity = vault_request(vault, 'GET', admin['vault_path'], token)['data']['data']
        ca = vault_request(vault, 'GET', vault['ca']['path'], token)['data']['data'][vault['ca']['field']]
    finally:
        vault_request(vault, 'POST', 'auth/token/revoke-self', token)
    options.scratch.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=options.scratch) as tmp:
        pair = Path(tmp) / 'identity.pem'
        trust = Path(tmp) / 'ca.pem'
        pair.write_text(identity['private_key_pem'].strip() + chr(10) + identity['certificate_pem'].strip() + chr(10),
                        encoding='ascii')
        trust.write_text(ca, encoding='ascii')
        with MongoClient(target['host'], target['port'], directConnection=True, tls=True,
                         tlsCAFile=str(trust), tlsCertificateKeyFile=str(pair),
                         tlsCertificateKeyFilePassword=identity['private_key_password'],
                         authMechanism='MONGODB-X509', authSource='$external',
                         serverSelectionTimeoutMS=10000) as client:
            if client[name]['sttv__publication'].find_one({'_id': 'writer'}, {'_id': 1}):
                raise RuntimeError('Loader publication is active')
            client.drop_database(name)
            if client[name].list_collection_names():
                raise RuntimeError('The database still contains collections after drop')


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--config', required=True)
    cli.add_argument('--database', required=True)
    args = cli.parse_args()
    drop(args.config, args.database)
