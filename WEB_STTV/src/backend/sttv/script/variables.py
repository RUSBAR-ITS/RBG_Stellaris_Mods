"""Resolve only unambiguous numeric definitions from the same source file."""

import re
from collections import defaultdict

from sttv.common.errors import BuildError
from sttv.common.json_io import numeric_value


class Variables:
    def __init__(self, entries):
        self.definitions = []
        self.by_name = defaultdict(list)
        for entry in entries:
            if not entry.key or not entry.key.startswith("@"):
                continue
            if (entry.operator != "=" or not isinstance(entry.value, str)
                    or not re.fullmatch(r"@[A-Za-z0-9_]+", entry.key)):
                raise BuildError("invalid_variable_definition", "Invalid local variable",
                                 line=entry.line)
            self.definitions.append({"name": entry.key, "value": entry.value,
                                     "line": entry.line})
            self.by_name[entry.key].append(entry.value)

    def resolve(self, name, trail=()):
        if name in trail:
            return None, "cyclic_local_variable"
        values = set(self.by_name.get(name, []))
        if not values:
            return None, "external_variable"
        if len(values) != 1:
            return None, "ambiguous_local_variable"
        value = values.pop()
        if re.fullmatch(r"@[A-Za-z0-9_]+", value):
            return self.resolve(value, trail + (name,))
        try:
            return numeric_value(value), None
        except BuildError:
            return None, "unresolved_local_variable"

    def number(self, text, integer, report, location):
        if not isinstance(text, str):
            raise BuildError("invalid_number", "Expected scalar number or variable")
        if text.startswith("@"):
            if not re.fullmatch(r"@[A-Za-z0-9_]+", text):
                raise BuildError("invalid_variable", f"Invalid variable reference: {text}")
            value, reason = self.resolve(text)
            if reason:
                report.add("warning", reason, "conversion",
                           f"Variable remains unresolved: {text}", **location)
            elif integer and not isinstance(value, int):
                raise BuildError("invalid_integer", f"Variable is not an integer: {text}")
            return {"variable": text, "resolved": value}
        return numeric_value(text, integer)
