"""
Utility functions for repo_flattener
"""

import os
from typing import List, Dict, Tuple
from collections import defaultdict


def format_size(bytes_size: int) -> str:
    """
    Format a byte size into a human-readable string.

    Args:
        bytes_size: Size in bytes

    Returns:
        Formatted size string (e.g., "1.2 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            if unit == 'B':
                return f"{bytes_size:.0f} {unit}"
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def estimate_tokens(file_size: int) -> int:
    """
    Estimate the number of tokens based on file size.
    Rough estimate: ~4 characters per token, ~1 byte per character for text.

    Args:
        file_size: Size in bytes

    Returns:
        Estimated token count
    """
    # Rough heuristic: 1 token ≈ 4 characters ≈ 4 bytes for text files
    return file_size // 4


def format_token_count(token_count: int) -> str:
    """
    Format a token count into a human-readable string.

    Args:
        token_count: Number of tokens

    Returns:
        Formatted token count (e.g., "450K")
    """
    if token_count < 1000:
        return str(token_count)
    elif token_count < 1_000_000:
        return f"{token_count / 1000:.1f}K"
    else:
        return f"{token_count / 1_000_000:.1f}M"


def calculate_file_statistics(
    repo_path: str,
    file_list: List[str]
) -> Dict[str, int]:
    """
    Calculate statistics about files in the repository.

    Args:
        repo_path: Path to the repository
        file_list: List of relative file paths

    Returns:
        Dictionary containing statistics:
        - total_files: Total number of files
        - total_size: Total size in bytes
        - by_extension: Dict mapping extensions to counts
    """
    stats = {
        'total_files': len(file_list),
        'total_size': 0,
        'by_extension': defaultdict(int),
        'by_extension_size': defaultdict(int)
    }

    for relative_path in file_list:
        file_path = os.path.join(repo_path, relative_path)
        if os.path.exists(file_path):
            try:
                size = os.path.getsize(file_path)
                stats['total_size'] += size

                # Get extension
                _, ext = os.path.splitext(relative_path)
                if not ext:
                    ext = '(no extension)'
                stats['by_extension'][ext] += 1
                stats['by_extension_size'][ext] += size
            except OSError:
                pass

    return stats


def format_file_type_summary(stats: Dict, top_n: int = 10) -> str:
    """
    Format file type statistics into a readable summary.

    Args:
        stats: Statistics dictionary from calculate_file_statistics
        top_n: Number of top file types to show

    Returns:
        Formatted summary string
    """
    total_files = stats['total_files']
    by_ext = stats['by_extension']

    if not by_ext:
        return "No files to summarize"

    # Sort by count, descending
    sorted_exts = sorted(by_ext.items(), key=lambda x: x[1], reverse=True)

    lines = []
    lines.append("\nFile Type Breakdown:")
    lines.append("-" * 50)

    shown = 0
    for ext, count in sorted_exts:
        if shown >= top_n:
            break

        percentage = (count / total_files * 100) if total_files > 0 else 0
        ext_display = ext if ext != '(no extension)' else 'No extension'

        # Create a simple bar
        bar_length = int(percentage / 2)  # Max 50 chars for 100%
        bar = "█" * bar_length

        lines.append(f"  {ext_display:<20} {count:>4} files ({percentage:>5.1f}%) {bar}")
        shown += 1

    # Show "other" if there are more types
    if len(sorted_exts) > top_n:
        other_count = sum(count for ext, count in sorted_exts[top_n:])
        other_percentage = (other_count / total_files * 100) if total_files > 0 else 0
        lines.append(f"  {'Other':<20} {other_count:>4} files ({other_percentage:>5.1f}%)")

    return "\n".join(lines)


def print_summary(
    file_count: int,
    skipped_count: int,
    manifest_path: str,
    stats: Dict,
    elapsed_time: float
) -> None:
    """
    Print a formatted summary of the processing results.

    Args:
        file_count: Number of files successfully processed
        skipped_count: Number of files skipped
        manifest_path: Path to the manifest file
        stats: Statistics dictionary
        elapsed_time: Time elapsed in seconds
    """
    total_size = stats.get('total_size', 0)
    estimated_tokens = estimate_tokens(total_size)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    # Success/skip counts
    if skipped_count == 0:
        print(f"  ✓ {file_count} files processed successfully")
    else:
        print(f"  ✓ {file_count} files processed successfully")
        print(f"  ⚠ {skipped_count} files skipped")

    # File info
    print(f"  📁 Manifest: {manifest_path}")
    print(f"  📊 Total size: {format_size(total_size)}")
    print(f"  🔢 Estimated tokens: ~{format_token_count(estimated_tokens)}")

    # Timing
    print(f"\n  ⏱  Done in {elapsed_time:.1f} seconds!")
    print("=" * 60)


def print_dry_run_summary(
    file_list: List[str],
    stats: Dict,
    output_dir: str
) -> None:
    """
    Print a summary for dry-run mode.

    Args:
        file_list: List of files that would be processed
        stats: Statistics dictionary
        output_dir: Output directory path
    """
    total_size = stats.get('total_size', 0)
    estimated_tokens = estimate_tokens(total_size)

    print("\n" + "=" * 60)
    print("DRY RUN - No files will be modified")
    print("=" * 60)

    print(f"\n  📂 Repository files: {len(file_list)}")
    print(f"  📁 Output directory: {output_dir}")
    print(f"  📊 Total size: {format_size(total_size)}")
    print(f"  🔢 Estimated tokens: ~{format_token_count(estimated_tokens)}")

    # Show file type breakdown
    print(format_file_type_summary(stats, top_n=10))

    print("\n" + "=" * 60)
    print("To proceed with processing, run without --dry-run flag")
    print("=" * 60)
