"""Validate prepared databases without reading the original game files."""

from collections import deque

from sttv.technologies.contracts import CONTRACTS, SCRIPT_CONTEXTS
from sttv.common.errors import BuildError
from sttv.common.schema import validate_schema
from sttv.script.rules import ScriptRules
from sttv.rules.validation import validate_registry
from sttv.technologies.provenance import validate_history


def occurrences(value):
    if isinstance(value, dict) and "occurrences" in value:
        return [item["value"] for item in value["occurrences"]]
    return [value]


def references(expression):
    if "tech" in expression:
        yield expression["tech"]
    else:
        for child in expression.get("all", expression.get("any", [])):
            yield from references(child)


def records(database):
    for collection in ("technologies", "categories", "tiers"):
        for identifier, record in database[collection].items():
            yield collection, identifier, record
            if collection == "technologies":
                for index, variant in enumerate(record["fields"].get("technology_swap", [])):
                    yield "variant", f"{identifier}.technology_swap[{index}]", variant


def validate_contexts(database, rules):
    for context, identifier, record in records(database):
        for key, value in record["fields"].items():
            field = CONTRACTS[context][key]
            kind = field.kind
            items = value if field.multiple else occurrences(value)
            for item in items:
                if kind in SCRIPT_CONTEXTS:
                    rules.validate(item, kind, path=f"{identifier}.fields.{key}")
                elif kind == "cost" and isinstance(item, dict) and "entries" in item:
                    rules.validate(item, "calculation", path=f"{identifier}.fields.cost")


def validate_references(database):
    technologies = database["technologies"]
    graph = {key: set() for key in technologies}
    for context, identifier, record in records(database):
        fields = record["fields"]
        for categories in occurrences(fields.get("category", [])):
            for category in categories:
                if category not in database["categories"]:
                    raise BuildError("missing_category", f"{identifier}: unknown category {category}")
        if "tier" in fields:
            for tier in occurrences(fields["tier"]):
                known = tier.get("resolved") if isinstance(tier, dict) else tier
                if known is not None and str(known) not in database["tiers"]:
                    raise BuildError("missing_tier", f"{identifier}: unknown tier {known}")
        if context == "technologies":
            for expression in occurrences(fields.get("prerequisites", {"all": []})):
                for previous in references(expression):
                    if previous not in technologies:
                        raise BuildError("missing_technology", f"{identifier}: unknown prerequisite {previous}")
                    graph[identifier].add(previous)
        if context in ("technologies", "variant"):
            name_key = identifier if context == "technologies" else record["name_key"]
            for source in record["name_sources"].values():
                if source is not None and source["key"] != name_key:
                    raise BuildError("name_provenance", f"{identifier}: mismatched name key")
    incoming = {key: len(dependencies) for key, dependencies in graph.items()}
    outgoing = {key: [] for key in graph}
    for key, dependencies in graph.items():
        for dependency in dependencies:
            outgoing[dependency].append(key)
    ready = deque(key for key, count in incoming.items() if not count)
    processed = 0
    while ready:
        key = ready.popleft()
        processed += 1
        for dependent in outgoing[key]:
            incoming[dependent] -= 1
            if incoming[dependent] == 0:
                ready.append(dependent)
    if processed != len(graph):
        raise BuildError("prerequisite_cycle", "Cycle in the union of prerequisite alternatives")


def validate_database(database, registry):
    validate_registry(registry)
    validate_schema(database, "database.schema.json")
    validate_history(database)
    validate_contexts(database, ScriptRules(registry))
    validate_references(database)
