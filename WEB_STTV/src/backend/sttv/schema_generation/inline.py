"""Closed contracts for inline settings, history, and source provenance."""

from .helpers import BOOL, LINE, NULL, RELATIVE, STRING, TEXT, array, obj, union


def counts():
    return obj({key: {"type": "integer", "minimum": 0} for key in
                ("encountered", "expanded", "failed", "template_files", "max_depth")})


def location():
    return obj({"root": {"enum": ["STELLARIS_ROOT", "TECH_PATH", "INLINE_SCRIPTS_DIR", "PRODUCT_ROOT", "PARSER_CONFIG", "WORK_DIR"]},
                "file": RELATIVE, "line": LINE, "column": LINE,
                "expansion_id": union(TEXT, NULL)})


def span():
    return obj({key: {"type": "integer", "minimum": 0 if key in ("start", "end") else 1}
                for key in ("start", "end", "line", "column", "end_line", "end_column")})


def origin():
    properties = {key: val for key, val in location()["properties"].items() if key not in ("line", "column")}
    properties.update(span=span(), generated_span=span(), fragments=array({"$ref": "#/$defs/origin"}),
                      placeholder={"$ref": "#/$defs/origin"}, synthetic=BOOL)
    return obj(properties, ["root", "file", "span", "expansion_id"])


def call():
    kinds = {
        'inline_script': ['reference', 'arguments'],
        'scripted_effect': ['boolean', 'arguments'],
        'scripted_trigger': ['boolean', 'arguments', 'test'],
        'script_value': ['reference', 'arguments'],
    }
    sequence = obj(dict(container=TEXT, index={'type': 'integer', 'minimum': 0},
                        count={'type': 'integer', 'minimum': 0}))
    single = obj(dict(node=TEXT))
    named = obj(dict(name=TEXT, file=RELATIVE, span=span()))
    result = obj(dict(id=TEXT, parent_id=union(TEXT, NULL), kind={'enum': list(kinds)},
                      call_site={'$ref': '#/$defs/origin'}, target=union(obj(dict(file=RELATIVE)), named),
                      invocation=obj(dict(operator=union(TEXT, NULL),
                         form={'enum': ['reference', 'arguments', 'boolean', 'test']}, raw=STRING)),
                      directives=array(TEXT), arguments=array(obj(dict(name=TEXT, raw=STRING, value=STRING))),
                      insertion=union(sequence, single)))
    result['allOf'] = []
    for kind, forms in kinds.items():
        specific = dict(target=obj(dict(file=RELATIVE)) if kind == 'inline_script' else named,
                        invocation={'properties': {'form': {'enum': forms},
                                      'operator': NULL if kind == 'script_value' else TEXT}},
                        insertion=single if kind == 'script_value' else sequence)
        if kind == 'script_value':
            specific['directives'] = array(TEXT, maxItems=0)
        result['allOf'].append({'if': {'properties': {'kind': {'const': kind}}},
                                'then': {'properties': specific}})
    return result


def chain():
    return array(obj({"id": TEXT, "kind": TEXT, "template": union(TEXT, NULL),
                      "call_site": {"$ref": "#/$defs/origin"}}))
