class FetchextError(Exception):
    """Base class for all fetchext exceptions."""
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception

class NetworkError(FetchextError):
    """Network-related errors (download failed, 404, timeout)."""
    pass

class ConfigError(FetchextError):
    """Configuration errors (missing file, invalid key)."""
    pass

class ExtensionError(FetchextError):
    """Extension parsing or validation errors."""
    pass

class SecurityError(FetchextError):
    """Security violations (signature mismatch, risk threshold)."""
    pass

class IntegrityError(SecurityError):
    """File integrity verification failed (hash mismatch)."""
    pass
