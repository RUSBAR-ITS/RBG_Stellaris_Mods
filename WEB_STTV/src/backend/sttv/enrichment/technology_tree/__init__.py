"""Enrich existing technology databases with reproducible placement relations."""


def enrich_technology_tree(variables_path=None, config_path=None, combination_path=None, *, recalculate=False):
    from .operation import execute
    return execute(variables_path, config_path, combination_path, recalculate=recalculate)
