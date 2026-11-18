"""Track shared inputs and directory membership across the complete run."""

from sttv.common.errors import BuildError
from sttv.enrichment.localization.index import LocalizationIndex
from sttv.enrichment.localization.snapshot import Snapshot
from sttv.sources.files import selected_files


class Inputs(Snapshot):
    def observe(self, rows):
        from pathlib import Path
        for row in rows:
            path, checksum = Path(row['path']).resolve(), row['sha256']
            if path in self.entries and self.entries[path] != checksum:
                raise BuildError('input_changed', f'Input changed during processing: {path}')
            if path not in self.entries:
                self.entries[path] = checksum
                self.report['inputs'].append(dict(row))

    def __init__(self, report):
        super().__init__(report)
        self.selections, self.localizations = [], []

    def capture_selection(self, settings):
        self.selections.append((settings, selected_files(settings)))

    def capture_build(self, settings, report):
        for name in ('sources', 'inline_sources', 'static_variable_sources',
                     'scripted_effect_sources', 'scripted_trigger_sources', 'script_value_sources'):
            root = settings.inline_directory if name == 'inline_sources' else settings.game
            for relative, checksum in report.data[name].items():
                path = (root / relative).resolve()
                actual = self.record(path, name)
                if checksum != actual:
                    raise BuildError('input_changed', f'Input changed during parsing: {path}')

    def merge(self, snapshot, file_sets):
        for path, checksum in snapshot.entries.items():
            if self.record(path, 'localization') != checksum:
                raise BuildError('input_changed', f'Input changed during localization: {path}')
        self.localizations.extend(file_sets)

    def verify(self):
        super().verify()
        for settings, paths in self.selections:
            if selected_files(settings) != paths:
                raise BuildError('input_changed', 'Selected source file inventory changed')
        for directory, reading, paths in self.localizations:
            if LocalizationIndex.files(directory, reading) != paths:
                raise BuildError('input_changed', f'Localization file inventory changed: {directory}')
