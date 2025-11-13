"""
Command-line interface for repo-flattener
"""

import argparse
import logging
import sys
from repo_flattener.core import (
    process_repository,
    scan_repository,
    interactive_file_selection
)
from repo_flattener.exceptions import RepoFlattenerError


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """
    Configure logging based on verbosity flags.

    Args:
        verbose: Enable verbose (DEBUG) logging
        quiet: Suppress all non-error logging
    """
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
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
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output (DEBUG level)')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Suppress all non-error output')
    parser.add_argument('--no-progress', action='store_true',
                        help='Disable progress bar')
    parser.add_argument('--workers', '-w', type=int, default=1, metavar='N',
                        help='Number of parallel workers (default: 1, 0 for auto)')
    parser.add_argument('--max-file-size', type=int, default=0, metavar='BYTES',
                        help='Maximum file size in bytes (default: 0 = no limit, e.g., 10485760 for 10MB)')
    parser.add_argument('--no-cache', action='store_true',
                        help='Disable manifest caching (default: caching enabled)')
    parser.add_argument('--cache-dir', type=str, default='.repo_flattener_cache', metavar='DIR',
                        help='Directory to store cache files (default: .repo_flattener_cache)')

    args = parser.parse_args()

    # Setup logging
    setup_logging(verbose=args.verbose, quiet=args.quiet)

    # Determine if progress bar should be shown
    # Disable progress bar if quiet mode is enabled or explicitly disabled
    show_progress = not (args.quiet or args.no_progress)

    # process ignore lists
    ignore_dirs = args.ignore_dirs.split(',') if args.ignore_dirs else None
    ignore_exts = args.ignore_exts.split(',') if args.ignore_exts else None

    try:
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
                file_list=selected_files,
                show_progress=show_progress,
                max_workers=args.workers,
                max_file_size=args.max_file_size,
                use_cache=not args.no_cache,
                cache_dir=args.cache_dir
            )
        else:
            # Normal mode: process all files
            process_repository(
                args.repo_path,
                args.output,
                ignore_dirs,
                ignore_exts,
                show_progress=show_progress,
                max_workers=args.workers,
                max_file_size=args.max_file_size,
                use_cache=not args.no_cache,
                cache_dir=args.cache_dir
            )
    except RepoFlattenerError as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logging.info("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        if args.verbose:
            logging.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()