"""Read documented log sections and script definitions without executing them."""

import re

from sttv.common.errors import BuildError
from sttv.script.parser import parse_text
from sttv.script.serialization import DataEntry, data_entries
from .observations import finish
from .walker import Walker

DOC_HEADER = re.compile(r"^([A-Za-z0-9_:.]+) - (.*)$")


def parameter_names(nodes):
    def names(entries):
        for entry in entries:
            yield from (parameter.name for parameter in entry.parameters)
            if isinstance(entry.value, list):
                yield from names(entry.value)
    return sorted(set(names(nodes)))


def documentation(walker, text, syntax):
    operators = "|".join(re.escape(value) for value in sorted(syntax.lexical["operators"], key=len, reverse=True))
    example_pattern = re.compile(r"^\s*([A-Za-z0-9_:.]+)\s*(" + operators + r")\s*(.*)$")
    lines = text.splitlines()
    headers = [(index, match) for index, line in enumerate(lines)
               if (match := DOC_HEADER.match(line))]
    if not headers or "== TRIGGER DOCUMENTATION ==" not in text:
        raise BuildError("unsupported_documentation", "Expected a TRIGGER DOCUMENTATION log")
    rows = []
    for position, (start, match) in enumerate(headers):
        end = headers[position + 1][0] if position + 1 < len(headers) else len(lines)
        segment = lines[start + 1:end]
        scopes = next((line.removeprefix("Supported Scopes:").split()
                       for line in segment if line.startswith("Supported Scopes:")), [])
        examples = [found for line in segment if (found := example_pattern.match(line))
                    and found[1] == match[1]]
        operators = sorted({found[2] for found in examples})
        value = examples[0][3] if examples else ""
        node = DataEntry(match[1], examples[0][2] if examples else None, value, start + 1)
        row = walker.record(node, "condition", None, match[1], form="documentation",
                            basis="documentation", documented_scopes=sorted(set(scopes)),
                            documented_operators=operators)
        row["current_rule"] = walker.rules.lookup("condition", match[1])
        if not scopes:
            row["issues"].append("incomplete_documentation")
        if value.startswith("{"):
            row["argument_kind"] = "block"
        elif not value or "<" in value or "/" in value:
            row["argument_kind"] = "unknown"
        rule = row["current_rule"]
        if rule is None:
            row["issues"].append("unsupported_command")
        else:
            if set(operators) - set(rule["operators"]):
                row["issues"].append("documented_operator")
            if scopes and rule["scopes"] is not None and (
                "all" in scopes or set(scopes) - set(rule["scopes"])
            ):
                row["issues"].append("documented_scope")
            expected = walker.registry["value_types"][rule["type"]]["kind"]
            if row["argument_kind"] not in (expected, "unknown") and not (
                expected == "string" and row["argument_kind"] in ("identifier", "number", "boolean")
            ):
                row["issues"].append("documented_argument")
        rows.append(finish(row))
    return rows


def script_definitions(walker, text, kind, file, syntax):
    nodes = data_entries(parse_text(text, syntax, file), purpose="analysis")
    if kind == "inline_scripts":
        name = file[:-4] if file.endswith(".txt") else file
        parameters = parameter_names(nodes)
        first = nodes[0].line if nodes else 1
        row = walker.record(DataEntry(name, "=", "", first), None, None, name,
                            form="definition", argument_kind="inline", parameters=parameters)
        spec = walker.registry["inline_scripts"].get(name)
        if spec is None:
            row["issues"].append("unsupported_inline")
        elif set(parameters) != set(spec["parameters"]):
            row["issues"].append("inline_parameters")
        walker.rows.append(finish(row))
        walker.commands(nodes, None, None, name)
    else:
        for node in nodes:
            if node.key and node.key.startswith("@"):
                continue
            if not node.key or node.operator != "=" or not isinstance(node.value, list):
                raise BuildError("unsupported_trigger", "Expected a scripted-trigger definition",
                                 line=node.line)
            parameters = parameter_names(node.value)
            row = walker.record(node, "condition", None, node.key, form="definition",
                                argument_kind="block" if parameters else "boolean",
                                parameters=parameters)
            row["current_rule"] = walker.rules.lookup("condition", node.key)
            if row["current_rule"] is None:
                row["issues"].append("unsupported_command")
            else:
                row["issues"].append("definition_review")
            walker.rows.append(finish(row))
            walker.commands(node.value, "condition", None, node.key)
    return walker.rows
