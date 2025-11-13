"""
Repo Flattener - A tool to convert a repository into flattened files
for easier LLM upload.
"""

__version__ = "0.2.1"

from repo_flattener.core import (
    process_repository,
    scan_repository,
    interactive_file_selection,
    sanitize_filename,
    create_manifest,
    export,
    IGNORE_DIRS,
    IGNORE_EXTS
)

from repo_flattener.exceptions import (
    RepoFlattenerError,
    InvalidRepositoryError,
    OutputDirectoryError,
    FileProcessingError,
    ConfigurationError
)

__all__ = [
    'process_repository',
    'scan_repository',
    'interactive_file_selection',
    'sanitize_filename',
    'create_manifest',
    'export',
    'IGNORE_DIRS',
    'IGNORE_EXTS',
    'RepoFlattenerError',
    'InvalidRepositoryError',
    'OutputDirectoryError',
    'FileProcessingError',
    'ConfigurationError'
]
