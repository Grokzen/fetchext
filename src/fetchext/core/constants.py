"""
Global constants for fetchext.
"""

from enum import IntEnum


class ExitCode(IntEnum):
    """
    Standard exit codes for the CLI.
    """

    SUCCESS = 0
    ERROR = 1
    USAGE = 2
    NETWORK = 3
    IO = 4
    CONFIG = 5
    NOT_FOUND = 6
    SECURITY = 7
    CANCELLED = 8
    DEPENDENCY = 9
