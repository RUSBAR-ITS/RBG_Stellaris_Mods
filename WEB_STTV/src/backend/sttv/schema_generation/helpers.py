"""Small composable builders for closed JSON Schema documents."""

STRING = {"type": "string"}
TEXT = {"type": "string", "minLength": 1}
NULL = {"type": "null"}
BOOL = {"type": "boolean"}
LINE = {"type": "integer", "minimum": 1}
NUMBER = {"type": "number"}
IDENTIFIER = {"type": "string", "pattern": r"^[A-Za-z0-9_:.?/-]+$"}
RELATIVE = {"type": "string", "pattern": r"^(?![A-Za-z]:)(?![/\\])(?!.*(?:^|[/\\])\.\.(?:[/\\]|$)).+$"}
VARIABLE_NAME = {"type": "string", "pattern": r"^@[A-Za-z0-9_]+$"}
HASH = {"type": "string", "pattern": "^[a-f0-9]{64}$"}


def obj(properties, required=None):
    return {"type": "object", "properties": properties,
            "required": list(properties) if required is None else required,
            "additionalProperties": False}


def array(items, **extra):
    return {"type": "array", "items": items, **extra}


def ref(name):
    return {"$ref": "#/$defs/" + name}


def union(*items):
    return {"anyOf": list(items)}


def mapping(value, keys=IDENTIFIER):
    return {"type": "object", "propertyNames": keys, "additionalProperties": value}


def repeated(item):
    return union(item, obj({"occurrences": array(
        obj({"source": ref("source"), "value": item}), minItems=2)}))


def document(value):
    return dict(value, **{"$schema": "https://json-schema.org/draft/2020-12/schema"})
