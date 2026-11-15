"""Resolve only explicitly selected analysis sources; disabled sources stay unread."""

from sttv.common.errors import BuildError
from sttv.common.paths import path_from
from sttv.sources.settings import substitute


def selected_sources(settings, options):
    result = []
    for collection, spec in settings.options["definitions"].items():
        directory = path_from(spec["subdirectory"], settings.technology)
        if not directory.is_relative_to(settings.technology):
            raise BuildError("unsafe_source", "Definition directory escapes TECH_PATH")
        result.append({
            "id": "TECH_PATH:" + collection, "kind": collection, "path": str(directory),
            "pattern": spec["pattern"], "recursive": spec["recursive"], "encoding": spec["encoding"],
            "enabled": True, "game_version": settings.options["rules"]["game_version"],
        })
    for spec in options["sources"]:
        item = dict(spec)
        if item["enabled"]:
            def lookup(name):
                if name not in settings.variables:
                    raise BuildError("unknown_variable", f"Unknown analysis source variable: {name}")
                return settings.variables[name]
            value = substitute(item["path"], lookup)
            item["path"] = str(path_from(value, settings.game))
        result.append(item)
    names = [item["id"] for item in result]
    if len(names) != len(set(names)):
        raise BuildError("duplicate_source", "Analysis source identifiers must be unique")
    return result
