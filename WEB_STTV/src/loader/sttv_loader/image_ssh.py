"""Run the image receiver using the workstation's SSH client and pinned host key."""

import base64
import os
from contextlib import contextmanager
from pathlib import Path
import shlex
import subprocess

from . import image_receiver
from .vault import vault_request


@contextmanager
def ssh_receiver(base, options, workspace, destination):
    vault = options['vault']
    auth = vault_request(vault, 'POST', f'auth/{vault["auth_mount"]}/login')
    token = auth['auth']['client_token']
    try:
        entry = vault_request(vault, 'GET', vault['path'], token)['data']['data']
        private = entry[vault['key_field']]
        phrase = entry[vault['passphrase_field']]
    finally:
        vault_request(vault, 'POST', 'auth/token/revoke-self', token)

    key = workspace / 'identity'
    askpass = workspace / 'askpass'
    ssh_config = workspace / 'ssh_config'
    try:
        key.write_text(private.strip() + '\n', encoding='ascii', newline='\n')
        askpass.write_text('#!/bin/sh\nprintf "%s\\n" "$STTV_IMAGE_KEY_PASSPHRASE"\n',
                           encoding='ascii', newline='\n')
        hosts = (base / options['known_hosts']).resolve(strict=True)
        ssh_config.write_text(f'UserKnownHostsFile "{hosts.as_posix()}"\n', encoding='utf-8', newline='\n')
        ssh = [str((base / options['executable']).resolve(strict=True)), '-F', ssh_config.as_posix(), '-T',
               '-o', 'IdentitiesOnly=yes', '-o', 'StrictHostKeyChecking=yes',
               '-o', 'UpdateHostKeys=no', '-o', 'ConnectTimeout=10',
               '-o', 'PreferredAuthentications=publickey', '-i', key.as_posix(),
               '-p', str(options['port']), '-l', options['user'], '--', options['host']]
        env = {**os.environ, 'SSH_ASKPASS_REQUIRE': 'force', 'SSH_ASKPASS': askpass.as_posix(),
               'STTV_IMAGE_KEY_PASSPHRASE': phrase, 'DISPLAY': 'local'}
        # Keep the remote command on one line when Windows invokes OpenSSH.
        script = base64.b64encode(Path(image_receiver.__file__).read_bytes()).decode('ascii')
        bootstrap = f"import base64; exec(base64.b64decode('{script}'))"

        def execute(action, *, payload=None, stream=None):
            command = shlex.join(['python3', '-B', '-c', bootstrap, action, destination])
            return subprocess.run([*ssh, command], input=payload, stdin=stream, env=env,
                                  capture_output=True)
        yield execute
    finally:
        key.unlink(missing_ok=True)
        askpass.unlink(missing_ok=True)
        ssh_config.unlink(missing_ok=True)
