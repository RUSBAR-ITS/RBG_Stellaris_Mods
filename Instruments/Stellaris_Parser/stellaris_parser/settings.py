"""Resolve a caller's source configuration relative to its own directory."""

from dataclasses import dataclass
from pathlib import Path

from document_package.errors import BuildError
from .localization.snapshot import Snapshot


@dataclass
class LocalizationSettings:
    directory: Path
    options: dict
    sources: dict
    snapshot: Snapshot | None = None


def check_output(output, protected):
    for root in protected:
        root = root.resolve()
        if output.is_relative_to(root) or root.is_relative_to(output):
            raise BuildError('unsafe_output', f'Output overlaps input: {root}')


def prepare_settings(path, output):
    path, output = Path(path).resolve(), Path(output).resolve()
    snapshot = Snapshot({'inputs': []})
    config = snapshot.json(path, 'configuration')
    loc = config['localization']
    sources = {lang: [(tier, (path.parent / loc['directories'][tier]).resolve())
                      for tier in spec['sources']] for lang, spec in loc['languages'].items()}
    check_output(output, [path, *(path.parent / r for r in config.get('roots', [])),
                          *(directory for tiers in sources.values() for _, directory in tiers)])
    if type(config['batch_size']) is not int or config['batch_size'] < 1:
        raise BuildError('invalid_config', 'batch_size must be a positive integer')
    return LocalizationSettings(output, {**loc, 'batch_size': config['batch_size']}, sources, snapshot)
