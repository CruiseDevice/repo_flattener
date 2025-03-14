"""
Command-line interface for repo-flattener
"""

import argparse
from repo_flattener.core import process_repository


def main():
    """
    Main entry point for the command-line interface.
    """
    parser = argparse.ArgumentParser(description='Convert a repository into'
                                     'flattened files for easier uploading'
                                     ' to LLMs.')
    parser.add_argument('repo_path', help='Path to the local repository')
    parser.add_argument('--output', '-o', help='Output directory for '
                        ' processed files', default='flattened_repo')
    parser.add_argument('--ignore-dirs', help='Comma-separated list'
                        ' of directories to ignore', default=None)
    parser.add_argument('--ignore-exts', help='Comma-separated list'
                        ' of file extensions to ignore', default=None)

    args = parser.parse_args()

    # process ignore lists
    ignore_dirs = args.ignore_dirs.split(',') if args.ignore_dirs else None
    ignore_exts = args.ignore_exts.split(',') if args.ignore_exts else None

    process_repository(
        args.repo_path,
        args.output,
        ignore_dirs,
        ignore_exts
    )


if __name__ == "__main__":
    main()