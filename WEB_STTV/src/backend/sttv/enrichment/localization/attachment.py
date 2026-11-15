"""Attach four text fields while keeping the original syntax tree intact."""

from copy import deepcopy

from sttv.common.errors import BuildError
from sttv.script.serialization import walk_nodes
from .report import count_field, diagnostic, failure


def remove_previous(database):
    for document in database["documents"]:
        for _, node in walk_nodes(document["items"]):
            if "enrichments" in node:
                node["enrichments"].pop("localization", None)
                if not node["enrichments"]:
                    del node["enrichments"]


def localize_field(target, language, field, settings, resolver):
    suffix = settings.options["keys"]["description_suffix"] if field == "description" else ""
    key = target.key + suffix
    result = {"requested_key": key, "key": None, "raw": None, "text": None,
              "source": None, "inherited_from": None, "unresolved_references": []}
    resolved = resolver.resolve(language, key)
    chains = resolved["unresolved_chains"] if resolved else []
    if (resolved is None and field == "description" and target.parent is not None
            and settings.options["inherit_description"]):
        parent = target.parent.node.get("enrichments", {}).get("localization", {}).get(language, {}).get(field)
        if parent and parent["key"] is not None:
            result.update(deepcopy(parent))
            result.update(requested_key=key, inherited_from=target.parent.path)
            chains = resolver.resolve(language, parent["key"])["unresolved_chains"]
    elif resolved is not None:
        result.update({key: value for key, value in resolved.items() if key != "unresolved_chains"})
    return result, chains


def attach(database, targets, settings, resolver, report):
    remove_previous(database)
    report["counts"]["technologies"] = sum(target.parent is None for target in targets)
    report["counts"]["variants"] = sum(target.parent is not None for target in targets)
    for target in targets:
        localized = {}
        for language in settings.options["languages"]:
            localized[language] = {}
            for field in ("name", "description"):
                context = {"node": target.path, "language": language, "field": field,
                    "requested_key": target.key + (settings.options["keys"]["description_suffix"]
                                                     if field == "description" else "")}
                try:
                    value, chains = localize_field(target, language, field, settings, resolver)
                except BuildError as exc:
                    failure(report, exc, "resolution", **context)
                    continue
                localized[language][field] = value
                count_field(report, language, field, value)
                if value["key"] is None:
                    diagnostic(report, "warning", "missing_localization", "Localization key not found",
                               "resolution", **context)
                elif value["unresolved_references"]:
                    for chain in chains:
                        diagnostic(report, "warning", "unresolved_localization",
                                   f"Unresolved token preserved: {chain[-1]}", "resolution",
                                   source=value["source"], chain=list(chain), **context)
        target.node.setdefault("enrichments", {})["localization"] = localized
