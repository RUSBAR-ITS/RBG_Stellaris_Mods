"""Errors suitable for the reference tree HTTP contract."""


class BuildError(Exception):
    status = 422

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class Busy(BuildError):
    status = 409


class InvalidRequest(BuildError):
    status = 400
