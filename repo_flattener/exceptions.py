"""
Custom exceptions for repo_flattener
"""


class RepoFlattenerError(Exception):
    """Base exception for all repo_flattener errors"""

    def __init__(self, message: str, tip: str = None):
        """
        Initialize the exception with a message and optional tip.

        Args:
            message: Error message
            tip: Optional helpful tip for the user
        """
        self.message = message
        self.tip = tip
        super().__init__(self.format_message())

    def format_message(self) -> str:
        """Format the error message with optional tip."""
        if self.tip:
            return f"{self.message}\nTip: {self.tip}"
        return self.message


class InvalidRepositoryError(RepoFlattenerError):
    """Raised when repository path is invalid or inaccessible"""

    def __init__(self, message: str, tip: str = None):
        if tip is None:
            # Provide helpful default tips based on common issues
            if "does not exist" in message:
                tip = "Make sure the path exists and is spelled correctly"
            elif "not a directory" in message:
                tip = "The path should point to a directory, not a file"
            elif "not readable" in message:
                tip = "Make sure you have read permissions for this directory"
            else:
                tip = "Verify the repository path and your access permissions"
        super().__init__(message, tip)


class OutputDirectoryError(RepoFlattenerError):
    """Raised when output directory cannot be created or accessed"""

    def __init__(self, message: str, tip: str = None):
        if tip is None:
            tip = "Ensure you have write permissions for the parent directory"
        super().__init__(message, tip)


class FileProcessingError(RepoFlattenerError):
    """Raised when a file cannot be processed"""

    def __init__(self, message: str, tip: str = None):
        if tip is None:
            tip = "Check file permissions and encoding"
        super().__init__(message, tip)


class ConfigurationError(RepoFlattenerError):
    """Raised when configuration file is invalid"""

    def __init__(self, message: str, tip: str = None):
        if tip is None:
            tip = "Check your .repo-flattener.yml file syntax"
        super().__init__(message, tip)


class SecurityError(RepoFlattenerError):
    """Raised when a security issue is detected"""

    def __init__(self, message: str, tip: str = None):
        if tip is None:
            if "path traversal" in message.lower():
                tip = "File paths must remain within the output directory"
            elif "symlink" in message.lower():
                tip = "Use --follow-symlinks to process symbolic links"
            else:
                tip = "This operation was blocked for security reasons"
        super().__init__(message, tip)


class ResourceLimitError(RepoFlattenerError):
    """Raised when resource limits are exceeded"""

    def __init__(self, message: str, tip: str = None):
        if tip is None:
            if "files" in message.lower():
                tip = "Use --max-files to increase the limit or filter files with --ignore-dirs"
            else:
                tip = "Reduce the scope of files to process"
        super().__init__(message, tip)
