"""Enrich existing technology databases with reproducible placement relations."""


def enrich_technology_tree(variables_path=None, config_path=None, combination_path=None, *, recalculate=False,
                          dlc_enabled=False, cancelled=None, expected_revision=None, variants=None, commit_guard=None):
    from .operation import execute
    return execute(variables_path, config_path, combination_path, recalculate=recalculate, dlc_enabled=dlc_enabled,
                   cancelled=cancelled, expected_revision=expected_revision, variants=variants, commit_guard=commit_guard)
