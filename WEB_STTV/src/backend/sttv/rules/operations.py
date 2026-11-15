"""Guarded profile and registry persistence, independent of any user interface."""

from sttv.common.errors import BuildError
from sttv.common.paths import output_path, distinct_paths
from sttv.common.persistence import save_json
from sttv.common.schema import validate_schema
from .compiler import generate_registry, load_profile, validate_profile
from .validation import validate_registry, validate_registry_syntax


def save_profile(settings, profile, relative):
    path = output_path(settings.work, relative, settings.protected)
    base = (settings.work / "profiles").resolve()
    if not path.is_relative_to(base) or path == base:
        raise BuildError("unsafe_profile", "User profiles must be inside WORK_DIR/profiles")
    distinct_paths([path, settings.registry, settings.database, settings.report,
                    settings.generation_report, *settings.config_files])
    return save_json(path, profile, validator=validate_profile)


def save_registry(settings, registry):
    return save_json(settings.registry, registry, validator=validate_registry)


def generate(settings):
    profile = load_profile(settings.profile)
    registry = generate_registry(profile)
    validate_registry_syntax(registry, settings.syntax)
    save_registry(settings, registry)
    result = {
        "format_version": 1, "profile_id": profile["profile_id"],
        "profile_fingerprint": registry["profile_fingerprint"],
        "registry_path": str(settings.registry), "registry_written": True,
    }
    validate_schema(result, "generation_report.schema.json")
    try:
        save_json(settings.generation_report, result, "generation_report.schema.json")
    except Exception as exc:
        error = BuildError("generation_report_write", str(exc))
        error.result = result
        raise error from exc
    return registry, result
