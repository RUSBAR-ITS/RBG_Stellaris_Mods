"""Inspect inline arguments and template nodes without expanding game scripts."""

from collections import Counter
import re

from stellaris_parser.script.nodes import Assignment, Block, Conditional, Formula, Scalar, TaggedBlock

LOGIC = frozenset({"and", "or", "not", "nand", "nor"})
NUMBER = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)")
CODE = re.compile(r"(?:[A-Za-z_$][\w.$:?@-]*\s*(?:=|!=|<=|>=|<|>))")
LOGICAL_CODE = re.compile(r"(?i)\b(?:and|or|not|nand|nor)\s*=")


def children(node):
    if isinstance(node, Assignment):
        return [node.key, node.value]
    if isinstance(node, (Block, Conditional)):
        return node.items
    if isinstance(node, TaggedBlock):
        return [node.tag, node.block]
    return []


def walk(items, ancestors=()):
    for node in items:
        yield node, ancestors
        yield from walk(children(node), (*ancestors, node))


def features(value):
    if not isinstance(value, Scalar):
        return [type(value).__name__]
    result = ["quoted" if value.quoted else "unquoted"]
    if not value.text:
        result.append("empty")
    if NUMBER.fullmatch(value.text):
        result.append("numeric_text")
    if value.text.casefold() in {"yes", "no"}:
        result.append("boolean_text")
    if value.text.startswith("@"):
        result.append("at_reference")
    if value.parameters:
        result.append("dollar_parameters")
    if "\n" in value.text:
        result.append("multiline")
    if CODE.search(value.text):
        result.append("code_like_text")
    if LOGICAL_CODE.search(value.text):
        result.append("logical_code_text")
    return result


def describe_scalar(node):
    if not isinstance(node, Scalar):
        return {"type": type(node).__name__}
    return {"type": "Scalar", "text": node.text, "raw": node.raw,
            "features": features(node), "parameters": [
                {"name": p.name, "default": p.default} for p in node.parameters]}


def describe_call(node, source, file):
    result = {"file": file, "line": node.span.line, "key": node.key.raw,
              "operator": node.operator, "type": type(node.value).__name__,
              "source": source[node.span.start:node.span.end], "arguments": []}
    if isinstance(node.value, Scalar):
        result["path"] = describe_scalar(node.value)
    elif isinstance(node.value, Block):
        scripts, names = [], []
        for child in node.value.items:
            if not isinstance(child, Assignment):
                result.setdefault("other_children", []).append(type(child).__name__)
                continue
            entry = {"name": child.key.text, "key_raw": child.key.raw,
                     "operator": child.operator, "line": child.span.line,
                     **describe_scalar(child.value)}
            if child.key.text.casefold() == "script":
                scripts.append(entry)
            else:
                names.append(child.key.text)
                result["arguments"].append(entry)
        result["script_fields"] = scripts
        result["duplicate_arguments"] = [key for key, n in Counter(names).items() if n > 1]
        result["duplicate_arguments_casefold"] = [
            key for key, n in Counter(s.casefold() for s in names).items() if n > 1]
        if len(scripts) == 1:
            result["path"] = scripts[0]
    return result


def describe_template(document):
    placeholders, conditionals, logic = [], [], Counter()
    formulas = 0
    for node, ancestors in walk(document.items):
        if isinstance(node, Scalar):
            for parameter in node.parameters:
                placeholders.append({"name": parameter.name, "default": parameter.default,
                                     "line": parameter.span.line, "raw": node.raw,
                                     "whole_scalar": parameter.raw == node.text})
        elif isinstance(node, Conditional):
            conditionals.append({"parameter": node.parameter, "negated": node.negated,
                                 "line": node.span.line})
        elif isinstance(node, Formula):
            formulas += 1
        elif (isinstance(node, Assignment) and node.key.text.casefold() in LOGIC
              and isinstance(node.value, Block)):
            logic[node.key.text.casefold()] += 1
    return {"placeholders": placeholders, "conditionals": conditionals,
            "logical_blocks": dict(logic), "formulas": formulas,
            "has_content": bool(document.items)}
