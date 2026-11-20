"""Per-language priority lookup with explicit duplicate conflict handling."""

from fnmatch import fnmatchcase

from document_package.errors import BuildError
from .reader import read_entries


class LocalizationIndex:
    def __init__(self, settings, snapshot, report):
        self.tables, self.selected = {}, {}
        self.report = report
        self.file_sets = []
        reading = settings.options["reading"]
        for language, tiers in settings.sources.items():
            self.tables[language] = []
            for tier, directory in tiers:
                table = {}
                paths = self.files(directory, reading)
                self.file_sets.append((directory, reading, paths))
                for path in paths:
                    relative = path.relative_to(directory).as_posix()
                    for key, raw, line in read_entries(path, settings.options["languages"][language]["header"],
                                                       reading["encoding"], snapshot):
                        table.setdefault(key, []).append({"raw": raw,
                            "source": {"tier": tier, "file": relative, "line": line}})
                self.tables[language].append(table)
                for key, entries in sorted(table.items()):
                    if len(entries) > 1:
                        report["duplicates"].append({"language": language, "key": key, "tier": tier,
                            "conflicting": len({item["raw"] for item in entries}) > 1,
                            "sources": [item["source"] for item in entries]})

    @staticmethod
    def files(directory, reading):
        if not directory.is_dir():
            raise BuildError("source_unavailable", f"Localization directory unavailable: {directory}")
        iterator = directory.rglob("*") if reading["recursive"] else directory.iterdir()
        paths = sorted((p for p in iterator if p.is_file() and fnmatchcase(p.name, reading["pattern"])),
                       key=lambda path: path.relative_to(directory).as_posix())
        if any(not path.resolve().is_relative_to(directory) for path in paths):
            raise BuildError("unsafe_source", f"Localization file escapes its directory: {directory}")
        return paths

    def verify_files(self):
        for directory, reading, paths in self.file_sets:
            if self.files(directory, reading) != paths:
                raise BuildError("input_changed", f"Localization file inventory changed: {directory}")

    def lookup(self, language, key):
        for table in self.tables[language]:
            entries = table.get(key)
            if not entries:
                continue
            if len({entry["raw"] for entry in entries}) > 1:
                error = BuildError("localization_conflict", f"Conflicting {language} localization: {key}")
                error.context = {"source": entries[0]["source"]}
                raise error
            entry = entries[0]
            self.selected[(language, key)] = {"language": language, "key": key, "source": entry["source"]}
            return entry
        return None
