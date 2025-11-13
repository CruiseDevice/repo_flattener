"""
Repo Flattener - A tool to convert a repository into flattened files
for easier LLM upload.
"""

__version__ = "0.1.1"

from repo_flattener.core import (
    process_repository,
    scan_repository,
    interactive_file_selection,
    sanitize_filename,
    create_manifest,
    IGNORE_DIRS,
    IGNORE_EXTS
)

__all__ = [
    'process_repository',
    'scan_repository',
    'interactive_file_selection',
    'sanitize_filename',
    'create_manifest',
    'IGNORE_DIRS',
    'IGNORE_EXTS'
]
