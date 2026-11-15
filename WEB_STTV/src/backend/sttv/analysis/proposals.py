"""Explicit alternatives for human review, never executable profile patches."""


def proposal(action, row, **values):
    return {
        "action": action, "template": None, "context": row["context"], "scope": None,
        "operator": None, "value_type": None, "parameters": [],
        "explanation": "Review this alternative against the source and target version.", **values,
    }


def alternatives(row, registry, templates, limit):
    issues = set(row["issues"])
    if row["inline_path"] or (row["form"] == "definition" and row["argument_kind"] == "inline"):
        spec = registry["inline_scripts"].get(row["inline_path"] or row["command"])
        missing = set(row["parameters"]) - set(spec["parameters"] if spec else [])
        return [proposal("add_inline_parameter" if missing else "review_signature", row,
                         parameters=sorted(missing),
                         explanation="Parameter names are observed; types and requiredness need review.")]
    if "unsupported_field" in issues:
        return [proposal("review_contract", row,
                         explanation="A new database field requires a model and converter change.")]
    result = []
    if issues & {"invalid_operator", "documented_operator"}:
        operators = row["documented_operators"] or [row["operator"]]
        for operator in operators:
            if operator and operator not in row["current_rule"]["operators"]:
                result.append(proposal("add_operator", row, operator=operator))
    if issues & {"invalid_scope", "documented_scope"}:
        scopes = row["documented_scopes"] or [row["scope"]]
        for scope in scopes:
            if scope and scope != "all" and scope not in (row["current_rule"]["scopes"] or []):
                result.append(proposal("add_scope", row, scope=scope))
        if "all" in scopes:
            result.append(proposal("add_scope", row, explanation=(
                "Documentation says all scopes; review the complete accepted scope set explicitly.")))
    if issues & {"invalid_inline", "unsupported_inline"}:
        result.append(proposal("review_signature", row, parameters=row["parameters"],
                               explanation="Review the inclusion path, invocation form and parameters."))
    kinds = {row["argument_kind"]}
    if "number" in kinds:
        kinds.add("integer")
    if "reference" in kinds:
        kinds.update(("number", "integer", "string"))
    if issues & {"unsupported_command", "invalid_argument", "invalid_number", "documented_argument"}:
        action = "add_command" if row["current_rule"] is None else "add_argument_form"
        for name, template in sorted(templates.items()):
            kind = registry["value_types"][template["type"]]["kind"]
            if kind not in kinds:
                continue
            if row["scope"] and template["scopes"] is not None and row["scope"] not in template["scopes"]:
                continue
            if row["operator"] and row["operator"] not in template["operators"]:
                continue
            result.append(proposal(action, row, template=name, value_type=template["type"],
                                   scope=row["scope"], parameters=row["parameters"],
                                   explanation="Candidate template inferred from observed argument form."))
            if len(result) >= limit:
                break
    if not result:
        action = "review_block" if row["form"] == "block" else "review_signature"
        result.append(proposal(action, row, parameters=row["parameters"],
                               explanation="Evidence is insufficient to select a safe profile change."))
    return result
