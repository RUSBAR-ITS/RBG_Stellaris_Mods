"""Reject publication if any bytes consumed by the builder have changed."""

from hashlib import sha256

from sttv.common.errors import BuildError


def verify_inputs(settings, report):
    for name in ('sources', 'inline_sources', 'static_variable_sources',
                 'scripted_effect_sources', 'scripted_trigger_sources', 'script_value_sources'):
        root = settings.inline_directory if name == 'inline_sources' else settings.game
        for relative, expected in report.data[name].items():
            path = root / relative
            if not path.resolve().is_relative_to(root):
                raise BuildError('source_changed', f'Source link changed: {relative}')
            if sha256(path.read_bytes()).hexdigest() != expected:
                raise BuildError('source_changed', f'Source changed during build: {relative}')
