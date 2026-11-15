"""Group evidence and bind review recommendations to an exact profile fingerprint."""

from collections import defaultdict

from sttv.common.errors import BuildError
from sttv.rules.compiler import expanded_templates, fingerprint
from .proposals import alternatives


def recommend(observations, profile, registry, limit):
    grouped = defaultdict(list)
    for row in observations:
        section = ("inline_scripts" if row["inline_path"] or (row["form"] == "definition"
                   and row["argument_kind"] == "inline") else
                   "fields" if "unsupported_field" in row["issues"] else "commands")
        context = None if section == "inline_scripts" else row["context"]
        grouped[(section, context, row["inline_path"] or row["command"])].append(row)
    templates = expanded_templates(profile)
    result = []
    for (section, context, command), rows in sorted(grouped.items(), key=lambda item: str(item[0])):
        if not any(row["issues"] for row in rows):
            continue
        rows = sorted(rows, key=lambda row: not bool(row["issues"]))
        target = {"section": section, "context": context, "command": command}
        choices = {}
        for row in rows:
            if not row["issues"]:
                continue
            for alternative in alternatives(row, registry, templates, limit):
                choices.setdefault(fingerprint(alternative), alternative)
        questions = ["Observed usage does not prove all supported forms or required arguments."]
        if any(row["scope"] is None and row["basis"] != "documentation" for row in rows):
            questions.append("The invocation scope is unknown; verify it before changing scope restrictions.")
        if context is None:
            questions.append("Determine the enclosing grammar and scope transition before choosing a group.")
        if any(row["form"] in ("block", "definition") for row in rows):
            questions.append("Confirm nested context, parameter types, requiredness and repetition.")
        contradictions = []
        forms = sorted({row["argument_kind"] for row in rows} - {"unknown"})
        if len(forms) > 1:
            contradictions.append("Different observed argument forms: " + ", ".join(forms))
        documented = [set(row["documented_scopes"]) for row in rows if row["documented_scopes"]]
        observed = {row["scope"] for row in rows if row["basis"] == "observed" and row["scope"]}
        if any("all" not in scopes and observed - scopes for scopes in documented):
            contradictions.append("Observed scopes exceed at least one documented scope set.")
        if len({tuple(sorted(scopes)) for scopes in documented}) > 1:
            contradictions.append("Documentation sources disagree about supported scopes.")
        signature = registry["inline_scripts"].get(command) if section == "inline_scripts" else None
        result.append({
            "id": fingerprint({"target": target, "profile": registry["profile_fingerprint"]}),
            "kind": "review", "target": target, "current_rule": rows[0]["current_rule"],
            "current_parameters": sorted(signature["parameters"]) if signature else None,
            "alternatives": list(choices.values()), "basis": sorted({row["basis"] for row in rows} | {"inference"}),
            "evidence": [row["id"] for row in rows[:limit]], "evidence_count": len(rows),
            "contradictions": contradictions, "questions": questions,
            "profile_id": profile["profile_id"], "profile_fingerprint": registry["profile_fingerprint"],
        })
    return result


def validate_recommendation_profile(result, profile):
    expected = fingerprint(profile)
    records = [result, *result["recommendations"]]
    if any(record["profile_id"] != profile["profile_id"]
           or record["profile_fingerprint"] != expected for record in records):
        raise BuildError("stale_recommendations", "The profile has changed; analyze and review again")
    return {"valid": True, "profile_fingerprint": expected}
