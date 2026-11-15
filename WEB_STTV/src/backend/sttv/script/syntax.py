"""Validate explicit configuration before constructing an independent parser."""

from copy import deepcopy
from dataclasses import dataclass

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.schema import validate_schema


@dataclass(frozen=True)
class Syntax:
    lexical: dict
    constructs: dict
    logical_operators: dict

    def logical_name(self, name):
        sensitive = self.logical_operators["case_sensitive"]
        return next((item for item in self.logical_operators["operators"]
                     if matches(name, item, sensitive)), None)

    def is_inline(self, name):
        spec = self.constructs["inline_script"]
        return matches(name, spec["keyword"], spec["case_sensitive"])


def matches(value, name, sensitive):
    return value == name if sensitive else value.casefold() == name.casefold()


def configuration_error(message, path):
    raise BuildError("syntax_configuration", message, field_path=path)


def validate_markers(lexical, constructs):
    markers = [("line_comment", lexical["line_comment"]),
               ("string.quote", lexical["string"]["quote"]),
               *[(f"block.{k}", v) for k, v in lexical["block"].items()],
               *[(f"operators.{i}", v) for i, v in enumerate(lexical["operators"])],
               ("parameters.open", constructs["parameters"]["open"]),
               ("conditional.open", constructs["conditional"]["open"]),
               ("conditional.body_close", constructs["conditional"]["body_close"]),
               *[(f"formulas.{i}.open", v["open"])
                 for i, v in enumerate(constructs["formulas"])]]
    whitespace = lexical["whitespace"]
    for i, (path, value) in enumerate(markers):
        if any(char in whitespace or char in "\r\n" for char in value) or "\ufeff" in value:
            configuration_error("A marker contains whitespace or BOM", path)
        for other_path, other in markers[:i]:
            if not (value.startswith(other) or other.startswith(value)):
                continue
            family = path.split(".")[0]
            if (family == other_path.split(".")[0] and family in ("operators", "formulas")
                    and value != other):
                continue
            configuration_error(f"Ambiguous markers: {other_path} and {path}", path)
    internal = [*lexical["string"].items(), *constructs["parameters"].items(),
                *constructs["conditional"].items(),
                *(item for spec in constructs["formulas"] for item in spec.items())]
    for key, value in internal:
        if isinstance(value, str) and any(char in whitespace or char in "\r\n" for char in value):
            configuration_error("A delimiter contains whitespace", key)
    quote, escape = lexical["string"]["quote"], lexical["string"]["escape"]
    if quote.startswith(escape) or escape.startswith(quote):
        configuration_error("String quote and escape must differ", "string.escape")
    for spec in constructs["formulas"]:
        inner_openers = [quote, lexical["line_comment"], constructs["parameters"]["open"],
                         *(item["open"] for item in constructs["formulas"])]
        if any(spec["close"].startswith(marker) or marker.startswith(spec["close"])
               for marker in inner_openers):
            configuration_error("Formula closer conflicts with an inner opener", "formulas")
    conditional = constructs["conditional"]
    if (conditional["negation"].startswith(conditional["header_close"])
            or conditional["header_close"].startswith(conditional["negation"])):
        configuration_error("Conditional negation conflicts with header closer", "conditional")
    params = constructs["parameters"]
    if any(params["default_separator"] in params[k] or params[k] in params["default_separator"]
           for k in ("open", "close")):
        configuration_error("Parameter separator conflicts with its delimiters", "parameters")
    for tag in constructs["tagged_blocks"]:
        if any(char in whitespace for char in tag) or any(value in tag for _, value in markers):
            configuration_error("A block tag must be an unquoted atom", "tagged_blocks")


def validate_keywords(lexical, constructs, logical):
    inline = constructs["inline_script"]
    delimiters = [lexical["line_comment"], *lexical["string"].values(),
                  *lexical["block"].values(), *lexical["operators"],
                  *constructs["parameters"].values(), *constructs["conditional"].values(),
                  *(v for spec in constructs["formulas"] for v in spec.values())]
    for name in [inline["keyword"], *logical["operators"]]:
        if (any(char.isspace() or char == "\ufeff" for char in name)
                or any(marker in name for marker in delimiters if isinstance(marker, str))):
            configuration_error("A keyword must be an unquoted atom", "operators")
    sensitive = logical["case_sensitive"]
    names = [name if sensitive else name.casefold() for name in logical["operators"]]
    if len(set(names)) != len(names):
        configuration_error("Duplicate logical operators", "operators")
    for name in logical["operators"]:
        if matches(name, inline["keyword"], sensitive and inline["case_sensitive"]):
            configuration_error("Logical and inline keywords conflict", "operators")
    if logical["assignment_operator"] not in lexical["operators"]:
        configuration_error("Logical assignment sign is not a lexical operator", "assignment_operator")
    if "=" not in lexical["operators"]:
        configuration_error("Inline calls require the assignment sign", "inline_script")


def make_syntax(lexical, constructs, logical_operators):
    validate_schema(lexical, "parser_lexical.schema.json")
    validate_schema(constructs, "parser_constructs.schema.json")
    validate_schema(logical_operators, "parser_logical_operators.schema.json")
    validate_markers(lexical, constructs)
    validate_keywords(lexical, constructs, logical_operators)
    return Syntax(deepcopy(lexical), deepcopy(constructs), deepcopy(logical_operators))


def load_syntax(lexical_path, constructs_path, logical_path):
    values = []
    for path, name in ((lexical_path, "parser_lexical.schema.json"),
                       (constructs_path, "parser_constructs.schema.json"),
                       (logical_path, "parser_logical_operators.schema.json")):
        try:
            value = read_json(path)
            validate_schema(value, name)
            values.append(value)
        except BuildError as exc:
            raise BuildError(exc.code, f"{path}: {exc}", field_path=exc.field_path) from exc
    try:
        validate_markers(*values[:2])
        validate_keywords(*values)
        return Syntax(*deepcopy(values))
    except BuildError as exc:
        raise BuildError(exc.code, f"{lexical_path}; {constructs_path}; {logical_path}: {exc}",
                         field_path=exc.field_path) from exc
