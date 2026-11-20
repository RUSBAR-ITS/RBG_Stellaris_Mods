"""Direct SCRAM connection with Vault credentials and Windows certificate-store login."""

import json
import subprocess


from document_package.errors import BuildError


def vault_request(options, method, path, token=None):
    args = ['curl.exe', '-q', '--silent', '--show-error', '--noproxy', '*', '--proto', '=https',
            '--connect-timeout', '5', '--max-time', '20', '--cert', options['certificate'],
            '--request', method, '--write-out', '\n%{http_code}']
    if token is None:
        args += ['--header', 'Content-Type: application/json', '--data-binary', '@-']
        payload = json.dumps({'name': options['role']})
    else:
        args += ['--header', '@-']
        payload = f'X-Vault-Token: {token}\n'
    result = subprocess.run([*args, options['address'] + '/v1/' + path], input=payload.encode(),
                            capture_output=True)
    if result.returncode:
        raise BuildError('vault_connection', f'Vault connection failed (curl {result.returncode})')
    body, _, status = result.stdout.rpartition(b'\n')
    if status not in (b'200', b'204'):
        raise BuildError('vault_request', f'Vault {method} {path}: HTTP {status.decode("ascii")}')
    return json.loads(body) if body else None


def credentials(options):
    auth = vault_request(options, 'POST', f'auth/{options["auth_mount"]}/login')
    token = auth['auth']['client_token']
    try:
        values = {}
        for name in ('ca', 'password'):
            ref = options[name]
            secret = vault_request(options, 'GET', ref['path'], token)
            values[name] = secret['data']['data'][ref['field']]
        return values
    finally:
        vault_request(options, 'POST', 'auth/token/revoke-self', token)
