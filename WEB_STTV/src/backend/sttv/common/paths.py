"""Stable paths and guarded output destinations."""

from pathlib import Path

from .errors import BuildError

PRODUCT_ROOT = Path(__file__).resolve().parents[4]
REPOSITORY_ROOT = PRODUCT_ROOT.parent
PRODUCT_DIRECTORIES = ("src", "schemas", "config", "Docs", "language")


def path_from(value, parent):
    path = Path(value)
    return (path if path.is_absolute() else parent / path).resolve()


def protected(path, roots):
    return any(path == root or path.is_relative_to(root) for root in roots)


def output_path(work, value, roots=()):
    relative = Path(value)
    if relative.is_absolute() or relative.drive:
        raise BuildError("unsafe_output", "Output filenames must be relative to WORK_DIR")
    target = (work / relative).resolve()
    protected_roots = [*(PRODUCT_ROOT / name for name in PRODUCT_DIRECTORIES), *roots]
    protected_roots.extend(path for path in PRODUCT_ROOT.iterdir() if path.is_file())
    if target == work or not target.is_relative_to(work) or protected(target, protected_roots):
        raise BuildError("unsafe_output", f"Output path is not writable: {value}")
    return target


def selected_path(selection, work):
    base = PRODUCT_ROOT if selection["base"] == "product" else work
    path = path_from(selection["path"], base)
    if path == base or not path.is_relative_to(base):
        raise BuildError("unsafe_config", "Configuration path escapes its selected base")
    return path


def distinct_paths(paths):
    for index, path in enumerate(paths):
        if any(path == other or path.is_relative_to(other) or other.is_relative_to(path)
               for other in paths[:index]):
            raise BuildError("output_collision", "Input and output file paths overlap")
