"""Check localization integrity without loading configurations or game files."""

from sttv.common.errors import BuildError
from sttv.script.serialization import walk_nodes


def invalid(message, path):
    raise BuildError("invalid_localization", message, field_path=path)


def validate_enrichments(database):
    enriched = {}
    for index, document in enumerate(database["documents"]):
        for local, node in walk_nodes(document["items"]):
            if "localization" in node.get("enrichments", {}):
                enriched[f"/documents/{index}{local}"] = node
    for path, node in enriched.items():
        if node["operator"] != "=" or node["value"]["kind"] != "block":
            invalid("Localization requires a block assignment", path)
        for language, fields in node["enrichments"]["localization"].items():
            for name, field in fields.items():
                if field["key"] is None:
                    if (any(field[key] is not None for key in ("raw", "text", "source", "inherited_from"))
                            or field["unresolved_references"]):
                        invalid("Missing text must have no selection or inheritance", path)
                    continue
                if any(field[key] is None for key in ("raw", "text", "source")):
                    invalid("Found text must include raw, resolved text and source", path)
                parent = field["inherited_from"]
                if parent is None:
                    if field["key"] != field["requested_key"]:
                        invalid("Direct text must match its requested key", path)
                    continue
                if (name != "description" or parent not in enriched
                        or path.rsplit("/value/items/", 1)[0] != parent):
                    invalid("Inheritance must reference the enclosing base technology", path)
                original = enriched[parent]["enrichments"]["localization"][language][name]
                if original["inherited_from"] is not None or original["key"] is None:
                    invalid("The inherited base description must be found and direct", path)
                if any(field[key] != original[key] for key in
                       ("key", "raw", "text", "source", "unresolved_references")):
                    invalid("Inherited text and source must match the base description", path)
