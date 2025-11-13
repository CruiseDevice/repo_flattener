"""
Command-line interface for repo-flattener
"""

import argparse
from repo_flattener.core import (
    process_repository,
    scan_repository,
    interactive_file_selection
)


def main():
    """
    Main entry point for the command-line interface.
    """
    parser = argparse.ArgumentParser(
        description='Convert a repository into flattened files for easier uploading to LLMs.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  repo-flattener /path/to/repository

  # Interactive file selection
  repo-flattener /path/to/repository --interactive

  # With custom ignore lists
  repo-flattener /path/to/repository --ignore-dirs build,dist --ignore-exts .log,.tmp
        """
    )
    parser.add_argument('repo_path', help='Path to the local repository')
    parser.add_argument('--output', '-o', help='Output directory for processed files',
                        default='flattened_repo')
    parser.add_argument('--ignore-dirs', help='Comma-separated list of directories to ignore',
                        default=None)
    parser.add_argument('--ignore-exts', help='Comma-separated list of file extensions to ignore',
                        default=None)
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Interactively select files to process')

    args = parser.parse_args()

    # process ignore lists
    ignore_dirs = args.ignore_dirs.split(',') if args.ignore_dirs else None
    ignore_exts = args.ignore_exts.split(',') if args.ignore_exts else None

    # Handle interactive mode
    if args.interactive:
        # First, scan the repository to get all files
        files_list = scan_repository(
            args.repo_path,
            ignore_dirs,
            ignore_exts
        )

        # Let user select files interactively
        selected_files = interactive_file_selection(files_list)

        # Process only the selected files
        process_repository(
            args.repo_path,
            args.output,
            ignore_dirs,
            ignore_exts,
            file_list=selected_files
        )
    else:
        # Normal mode: process all files
        process_repository(
            args.repo_path,
            args.output,
            ignore_dirs,
            ignore_exts
        )


if __name__ == "__main__":
    main()