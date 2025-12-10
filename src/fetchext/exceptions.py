from fetchext.constants import ExitCode

class FetchextError(Exception):
    """Base class for all fetchext exceptions."""
    exit_code = ExitCode.ERROR

    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception

class NetworkError(FetchextError):
    """Network-related errors (download failed, 404, timeout)."""
    exit_code = ExitCode.NETWORK

class ConfigError(FetchextError):
    """Configuration errors (missing file, invalid key)."""
    exit_code = ExitCode.CONFIG

class ExtensionError(FetchextError):
    """Extension parsing or validation errors."""
    exit_code = ExitCode.ERROR

class SecurityError(FetchextError):
    """Security violations (signature mismatch, risk threshold)."""
    exit_code = ExitCode.SECURITY

class IntegrityError(SecurityError):
    """File integrity verification failed (hash mismatch)."""
    exit_code = ExitCode.SECURITY

class InsufficientDiskSpaceError(FetchextError):
    """Not enough disk space for the operation."""
    exit_code = ExitCode.IO

class NotFoundError(FetchextError):
    """Resource not found."""
    exit_code = ExitCode.NOT_FOUND

