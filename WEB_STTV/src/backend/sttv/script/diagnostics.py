"""Restore physical locations and invocation chains after data projection."""

from .traversal import source_location, walk


def annotate_error(error, document):
    location = getattr(error, "source_location", None)
    if location:
        for node in walk(document.items):
            if node.origin and source_location(node.origin) == location:
                error.provenance = node.origin
                break
    origin = getattr(error, "provenance", None)
    call_id = (location or origin or {}).get("inline_call_id")
    if call_id and not hasattr(error, "call_chain"):
        records = {record["id"]: record for record in document.metadata["inline_scripts"]}
        chain = []
        while call_id:
            record = records[call_id]
            chain.append({key: record[key] for key in ("id", "template", "call_site")})
            call_id = record["parent_id"]
        error.call_chain = list(reversed(chain))
        error.root_source = document.source.origin(0, 0)
