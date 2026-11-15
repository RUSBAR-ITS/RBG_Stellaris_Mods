"""Select direct technology and variant assignments from persisted documents."""

from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import PurePosixPath

from sttv.common.errors import BuildError


@dataclass
class Target:
    path: str
    node: dict
    key: str
    parent: object = None


def assignment(node, key=None):
    return (node["kind"] == "assignment" and node["operator"] == "="
            and (key is None or node["key"]["text"] == key))


def select_targets(database, settings):
    options, targets = settings.options, []
    directory = PurePosixPath(settings.selection_directory)
    for index, document in enumerate(database["documents"]):
        path = PurePosixPath(document["source"]["file"])
        try:
            relative = path.relative_to(directory)
        except ValueError:
            continue
        if (not options["selection"]["recursive"] and len(relative.parts) != 1
                or not fnmatchcase(path.name, options["selection"]["pattern"])):
            continue
        for number, node in enumerate(document["items"]):
            if not assignment(node) or node["value"]["kind"] != "block":
                continue
            base = Target(f"/documents/{index}/items/{number}", node, node["key"]["text"])
            if not base.key:
                raise BuildError("invalid_target", "Technology name is empty", field_path=base.path)
            targets.append(base)
            for offset, child in enumerate(node["value"]["items"]):
                if not assignment(child, options["keys"]["variant"]):
                    continue
                pointer = f"{base.path}/value/items/{offset}"
                names = [item for item in child["value"].get("items", [])
                         if item["kind"] == "assignment" and item["key"]["text"] == options["keys"]["name"]]
                if (child["value"]["kind"] != "block" or len(names) != 1
                        or not assignment(names[0]) or names[0]["value"]["kind"] != "scalar"
                        or not names[0]["value"]["text"]):
                    error = BuildError("invalid_target", f"Variant needs one scalar name: {pointer}",
                                       line=child["span"]["line"] if "line" in child["span"] else None)
                    error.context = {"node": pointer}
                    raise error
                targets.append(Target(pointer, child, names[0]["value"]["text"], base))
    if not targets:
        raise BuildError("no_localization_targets", "No technology objects matched the selection")
    return targets
