"""
Core functionality for repo flattener
"""

import os
import re
import sys

# Default directories to ignore
IGNORE_DIRS = ['.git', 'node_modules', '__pycache', '.idea', '.vscode',
               'venv', 'env', '.env']

# Default file extensions to ignore
IGNORE_EXTS = ['.pyc', '.class', '.o', '.so', '.dll', '.exe', '.jar',
               '.war']


def sanitize_filename(filename):
    """
    Sanitize a filename to remove invalid characters.

    Args:
        filename (str): The filename to sanitize

    Returns:
        str: Sanitized filename
    """
    # Replace invalid filename characters with underscore
    return re.sub(r'[\\/*?:"<>|]', "_", filename)


def scan_repository(repo_path, ignore_dirs=None, ignore_exts=None):
    """
    Scan a repository and return a list of files that would be processed.

    Args:
        repo_path (str): Path to the repository
        ignore_dirs (list, optional): List of directories to ignore
        ignore_exts (list, optional): List of file extensions to ignore

    Returns:
        list: List of relative file paths
    """
    if ignore_dirs is not None:
        ignore_dirs = ignore_dirs + IGNORE_DIRS
    else:
        ignore_dirs = IGNORE_DIRS

    if ignore_exts is not None:
        ignore_exts = ignore_exts + IGNORE_EXTS
    else:
        ignore_exts = IGNORE_EXTS

    repo_path = os.path.abspath(repo_path)
    files_list = []

    for root, dirs, files in os.walk(repo_path):
        # skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for filename in files:
            # check if any file should be ignored
            if any(filename.endswith(ext) for ext in ignore_exts):
                continue
            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, repo_path)
            files_list.append(relative_path)

    return sorted(files_list)


def interactive_file_selection(files_list):
    """
    Present an interactive menu for users to select/deselect files.

    Args:
        files_list (list): List of file paths to choose from

    Returns:
        list: List of selected file paths
    """
    if not files_list:
        print("No files found to process.")
        return []

    print(f"\nFound {len(files_list)} files in the repository.")
    print("\nInteractive File Selection")
    print("=" * 50)
    print("\nCommands:")
    print("  [a]ll       - Select all files")
    print("  [n]one      - Deselect all files")
    print("  [t]oggle N  - Toggle selection for file #N")
    print("  [r]ange N-M - Toggle selection for files #N through #M")
    print("  [s]how      - Show current selection")
    print("  [d]one      - Finish selection and proceed")
    print("  [q]uit      - Cancel and exit")
    print("=" * 50)

    # All files selected by default
    selected = {i: True for i in range(len(files_list))}

    def show_files(start=0, count=20):
        """Display a page of files with their selection status."""
        end = min(start + count, len(files_list))
        print(f"\nFiles {start + 1}-{end} of {len(files_list)}:")
        print("-" * 50)
        for i in range(start, end):
            status = "[X]" if selected[i] else "[ ]"
            print(f"{status} {i + 1:4d}. {files_list[i]}")
        if end < len(files_list):
            print(f"\n... and {len(files_list) - end} more files")

        selected_count = sum(1 for v in selected.values() if v)
        print(f"\nSelected: {selected_count}/{len(files_list)} files")

    current_page = 0
    show_files(current_page)

    while True:
        try:
            command = input("\n> ").strip().lower()

            if not command:
                continue

            if command in ['d', 'done']:
                selected_files = [files_list[i] for i in range(len(files_list)) if selected[i]]
                if not selected_files:
                    print("No files selected. Please select at least one file.")
                    continue
                print(f"\nProceeding with {len(selected_files)} selected files.")
                return selected_files

            elif command in ['q', 'quit']:
                print("\nCancelled by user.")
                sys.exit(0)

            elif command in ['a', 'all']:
                for i in range(len(files_list)):
                    selected[i] = True
                print(f"All {len(files_list)} files selected.")
                show_files(current_page)

            elif command in ['n', 'none']:
                for i in range(len(files_list)):
                    selected[i] = False
                print("All files deselected.")
                show_files(current_page)

            elif command in ['s', 'show']:
                show_files(current_page)

            elif command.startswith('t ') or command.startswith('toggle '):
                parts = command.split()
                if len(parts) == 2:
                    try:
                        index = int(parts[1]) - 1
                        if 0 <= index < len(files_list):
                            selected[index] = not selected[index]
                            status = "selected" if selected[index] else "deselected"
                            print(f"File #{index + 1} {status}: {files_list[index]}")
                            # Update display if it's on current page
                            if current_page <= index < current_page + 20:
                                show_files(current_page)
                        else:
                            print(f"Invalid index. Please use 1-{len(files_list)}")
                    except ValueError:
                        print("Invalid number. Usage: toggle <number>")
                else:
                    print("Usage: toggle <number>")

            elif command.startswith('r ') or command.startswith('range '):
                parts = command.split()
                if len(parts) == 2 and '-' in parts[1]:
                    try:
                        start, end = parts[1].split('-')
                        start_idx = int(start) - 1
                        end_idx = int(end) - 1
                        if 0 <= start_idx <= end_idx < len(files_list):
                            for i in range(start_idx, end_idx + 1):
                                selected[i] = not selected[i]
                            print(f"Toggled files #{start_idx + 1}-{end_idx + 1}")
                            show_files(current_page)
                        else:
                            print(f"Invalid range. Please use 1-{len(files_list)}")
                    except ValueError:
                        print("Invalid range. Usage: range <start>-<end>")
                else:
                    print("Usage: range <start>-<end> (e.g., range 1-10)")

            elif command.startswith('p ') or command.startswith('page '):
                parts = command.split()
                if len(parts) == 2:
                    try:
                        page = int(parts[1]) - 1
                        if 0 <= page * 20 < len(files_list):
                            current_page = page * 20
                            show_files(current_page)
                        else:
                            max_page = (len(files_list) - 1) // 20 + 1
                            print(f"Invalid page. Please use 1-{max_page}")
                    except ValueError:
                        print("Invalid page number. Usage: page <number>")
                else:
                    print("Usage: page <number>")

            else:
                print("Unknown command. Available commands: all, none, toggle N, range N-M, show, done, quit")

        except KeyboardInterrupt:
            print("\n\nCancelled by user.")
            sys.exit(0)
        except EOFError:
            print("\n\nCancelled by user.")
            sys.exit(0)


def process_repository(repo_path, output_dir, ignore_dirs=None,
                       ignore_exts=None, file_list=None):
    """
    Process all files in a repository and create flattened files in the output
    directory.

    Args:
        repo_path (str): Path to the repository
        output_dir (str): Directory to output the processed files.
        ignore_dirs (list, optional): List of directories to ignore
        ignore_exts (list, optional): List of file extensions to ignore
        file_list (list, optional): Specific list of files to process (relative paths)
    """
    if ignore_dirs is not None:
        ignore_dirs = ignore_dirs + IGNORE_DIRS
    else:
        ignore_dirs = IGNORE_DIRS

    if ignore_exts is not None:
        ignore_exts = ignore_exts + IGNORE_EXTS
    else:
        ignore_exts = IGNORE_EXTS

    # create output directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)

    repo_path = os.path.abspath(repo_path)
    print(f"Processing repository: {repo_path}")
    print(f"Output directory: {output_dir}")

    # store all file paths for the manifest
    all_files = []

    file_count = 0
    skipped_count = 0

    # If file_list is provided, use it; otherwise scan the repository
    if file_list is not None:
        # Process only the specified files
        all_files = file_list
        for relative_path in file_list:
            file_path = os.path.join(repo_path, relative_path)

            try:
                # create new file with path information
                output_filename = sanitize_filename(f"{relative_path.replace('/', '_')}")
                output_filepath = os.path.join(output_dir, output_filename)

                with open(file_path, 'r', encoding='utf-8', errors='replace') as input_file:
                    content = input_file.read()

                with open(output_filepath, 'w', encoding='utf-8') as output_file:
                    # write the file path at the top
                    output_file.write(f"// FILE: {relative_path}\n\n")
                    output_file.write(content)
                file_count += 1
                if file_count % 50 == 0:
                    print(f"Processed {file_count} files...")
            except Exception as e:
                print(f"Error processing file {file_path}: {str(e)}")
                skipped_count += 1
    else:
        # Normal mode: scan and process all files
        for root, dirs, files in os.walk(repo_path):
            # skip ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            for filename in files:
                # check if any file should be ignored
                if any(filename.endswith(ext) for ext in ignore_exts):
                    continue
                file_path = os.path.join(root, filename)

                # get relative path from the repository root
                relative_path = os.path.relpath(file_path, repo_path)
                all_files.append(relative_path)

                try:
                    # create new file with path information
                    output_filename = sanitize_filename(f"{relative_path.replace('/', '_')}")
                    output_filepath = os.path.join(output_dir, output_filename)

                    with open(file_path, 'r', encoding='utf-8', errors='replace') as input_file:
                        content = input_file.read()

                    with open(output_filepath, 'w', encoding='utf-8') as output_file:
                        # write the file path at the top
                        output_file.write(f"// FILE: {relative_path}\n\n")
                        output_file.write(content)
                    file_count += 1
                    if file_count % 50 == 0:
                        print(f"Processed {file_count} files...")
                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")
                    skipped_count += 1

    manifest_path = create_manifest(output_dir, all_files)

    print(f"Completed processing {file_count} files.")
    print(f"Skipped {skipped_count} files due to errors.")
    print(f"Manifest created at {manifest_path}")

    return file_count, skipped_count, manifest_path


def create_manifest(output_dir, all_files):
    """
    Create a manifest file with a structured representation of all processed files.

    Args:
        output_dir (str): Director to save the manifest
        all_files (list): List of all processed file paths

    Returns:
        str: Path to the created manifest file
    """
    manifest_path = os.path.join(output_dir, 'file_manifest.txt')
    with open(manifest_path, 'w', encoding='utf-8') as manifest:
        manifest.write("Repository structure:\n\n")

        # Create a dictionary to represent the file tree
        file_tree = {}
        for file_path in all_files:
            parts = file_path.split('/')
            current = file_tree
            for i, part in enumerate(parts):
                if i == len(parts) - 1:  # if it is a file (last part)
                    if '__files__' not in current:
                        current['__files__'] = []
                    current['__files__'].append(part)
                else:   # If it is a directory
                    if part not in current:
                        current[part] = {}
                    current = current[part]

        # Function to write the tree structure recursively
        def write_tree(tree, level=0):
            indent = ' ' * 4 * level
            # Write files at this level
            if '__files__' in tree:
                for file in sorted(tree['__files__']):
                    manifest.write(f"{indent}{file}\n")

            # Write directories and their contents
            for dir_name, contents in sorted([(k, v) for k, v in tree.items()
                                              if k != '__files__']):
                manifest.write(f"{indent}{dir_name}\n")
                write_tree(contents, level + 1)

        write_tree(file_tree)
    return manifest_path
