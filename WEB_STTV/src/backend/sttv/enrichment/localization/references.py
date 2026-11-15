"""Expand ordinary localization references while retaining opaque game tokens."""

import re

from sttv.common.errors import BuildError


def tokens(text, delimiter):
    start, index = 0, 0
    while index < len(text):
        char = text[index]
        if char == "[":
            depth, end = 1, index + 1
            while end < len(text) and depth:
                depth += (text[end] == "[") - (text[end] == "]")
                end += 1
            index = end
        elif char in ("£", delimiter):
            end = text.find(char, index + 1)
            if end < 0:
                index = len(text)
                continue
            if char == delimiter:
                yield text[start:index], None
                yield text[index:end + 1], text[index + 1:end]
                start = end + 1
            index = end + 1
        else:
            index += 1
    yield text[start:], None


class Resolver:
    def __init__(self, index, options):
        self.index, self.options = index, options
        self.key_pattern = re.compile(options["key_pattern"])

    def resolve(self, language, key, chain=()):
        trail = (*chain, key)
        if key in chain:
            self.error("localization_cycle", "Cyclic localization reference", trail)
        try:
            entry = self.index.lookup(language, key)
        except BuildError as exc:
            exc.context = {**getattr(exc, "context", {}), "chain": list(trail)}
            raise
        if entry is None:
            return None
        if len(trail) > self.options["max_depth"]:
            self.error("localization_depth", "Localization reference depth exceeded", trail)
        parts, unresolved, chains, length = [], set(), set(), 0
        for token, reference in tokens(entry["raw"], self.options["delimiter"]):
            if reference is not None and self.key_pattern.fullmatch(reference):
                child = self.resolve(language, reference, trail)
                if child is None:
                    unresolved.add(token)
                    chains.add((*trail, reference))
                else:
                    token = child["text"]
                    unresolved.update(child["unresolved_references"])
                    chains.update(child["unresolved_chains"])
            length += len(token)
            if length > self.options["max_characters"]:
                self.error("localization_size", "Localized text size exceeded", trail)
            parts.append(token)
        return {"key": key, "raw": entry["raw"], "text": "".join(parts), "source": entry["source"],
                "unresolved_references": sorted(unresolved), "unresolved_chains": sorted(chains)}

    @staticmethod
    def error(code, message, trail):
        error = BuildError(code, f"{message}: {' -> '.join(trail)}")
        error.context = {"chain": list(trail)}
        raise error
