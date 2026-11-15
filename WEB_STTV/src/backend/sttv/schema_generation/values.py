"""Reference markers for script values; shared library rules remain centralized."""

from .helpers import TEXT, obj


def configuration():
    return obj(dict(format_version={'const': 1}, reference_prefix=TEXT,
                    scope_separator=TEXT, argument_separator=TEXT))
