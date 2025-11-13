"""
Custom exceptions for repo_flattener
"""


class RepoFlattenerError(Exception):
    """Base exception for all repo_flattener errors"""
    pass


class InvalidRepositoryError(RepoFlattenerError):
    """Raised when repository path is invalid or inaccessible"""
    pass


class OutputDirectoryError(RepoFlattenerError):
    """Raised when output directory cannot be created or accessed"""
    pass


class FileProcessingError(RepoFlattenerError):
    """Raised when a file cannot be processed"""
    pass


class ConfigurationError(RepoFlattenerError):
    """Raised when configuration file is invalid"""
    pass
