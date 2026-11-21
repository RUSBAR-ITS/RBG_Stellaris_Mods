"""Game localization key selection and request-scoped translation resolution."""

import re
from collections.abc import Iterator
from dataclasses import dataclass, field


KEY = re.compile(r'[A-Za-z0-9_.:-]+')
# Lower-case named resources such as $energy|Y$ are localization references.
# Upper-case formatted slots such as $PLANET|Y$ need a value from the running game.
COLORED_KEY = re.compile(r'([a-z][a-z0-9_.:-]*)\|([MLGRBYHCKITtESWPVg_UAcvdrl0-3])')


def determine_key(rules, context, value):
    rule = rules.get(context)
    if rule is None or not isinstance(value, str) or not value:
        return None
    if 'map' in rule:
        return rule['map'].get(value)
    return rule.get('prefix', '') + value + rule['suffix']


def fragments(text):
    """Yield literal spans and complete references outside opaque game constructs."""
    start = index = 0
    while index < len(text):
        char = text[index]
        index += 1
        if char == '[':
            depth = 1
            while index < len(text) and depth:
                depth += (text[index] == '[') - (text[index] == ']')
                index += 1
        elif char in ('£', '$'):
            end = text.find(char, index)
            if end == -1:
                continue
            name = text[index:end]
            colored = COLORED_KEY.fullmatch(name)
            if char == '$' and (KEY.fullmatch(name) or colored):
                if start < index - 1:
                    yield text[start:index - 1], None, None
                yield text[index - 1:end + 1], colored[1] if colored else name, colored[2] if colored else None
                start = end + 1
            index = end + 1
    if start < len(text):
        yield text[start:], None, None


@dataclass
class Frame:
    key: str
    tokens: Iterator
    parts: list[str] = field(default_factory=list)
    cyclic: bool = False
    color: str | None = None


def render(root, definitions, cache):
    if root in cache:
        return cache[root]
    if root not in definitions:
        return None
    frames = [Frame(root, iter(definitions[root]))]
    active = {root}
    while frames:
        current = frames[-1]
        token = next(current.tokens, None)
        if token is None:
            result = ''.join(current.parts)
            # A cycle's closing fragment depends on the path from this particular root.
            if not current.cyclic:
                cache[current.key] = result
            frames.pop()
            active.remove(current.key)
            if not frames:
                return result
            frames[-1].parts.append(f'§{current.color}{result}§!' if current.color else result)
            frames[-1].cyclic |= current.cyclic
            continue
        literal, reference, color = token
        if reference in active:
            current.cyclic = True
            current.parts.append(literal)
        elif reference in cache:
            value = cache[reference]
            current.parts.append(f'§{color}{value}§!' if color else value)
        elif reference in definitions:
            active.add(reference)
            frames.append(Frame(reference, iter(definitions[reference]), color=color))
        else:
            current.parts.append(literal)


def lookup(language, keys, read_strings):
    pending = set(keys)
    visited = set()
    definitions = {}
    while pending:
        visited.update(pending)
        references = set()
        for key, text in read_strings(language, sorted(pending)):
            tokens = list(fragments(text))
            definitions[key] = tokens
            references.update(reference for _, reference, _ in tokens if reference is not None)
        pending = references - visited
    cache = {}
    results = {k: render(k, definitions, cache) for k in dict.fromkeys(keys)}
    return {'language': language, 'items': [{'key': k, 'text': results[k]} for k in keys]}
