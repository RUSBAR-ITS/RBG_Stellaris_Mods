"""Structured failures shared by parsing and build stages."""


class BuildError(Exception):
    def __init__(self, code, message, *, line=None, field_path=None):
        super().__init__(message)
        self.code = code
        self.line = line
        self.field_path = field_path
