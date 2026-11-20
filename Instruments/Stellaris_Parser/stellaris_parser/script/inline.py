"""Public inline expansion interface; template access is supplied by the caller."""

from .inlining.expansion import Expansion, expand_inline_script
from .inlining.loader import FileTemplates, MemoryTemplates

__all__ = ["Expansion", "FileTemplates", "MemoryTemplates", "expand_inline_script"]
