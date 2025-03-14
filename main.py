import os
import re
import argparse


IGNORE_DIRS = ['.git', 'node_modules', '__pycache', '.idea', '.vscode',
               'venv', 'env', '.env']

IGNORE_EXTS = ['.pyc', '.class', '.o', '.so', '.dll', '.exe', '.jar',
               '.war']


def sanitize_filename(filename):
    """
    Sanitize a filename to remove invalid characters.
    """
    # Replace invalid filename characters with underscore
    return re.sub(r'[\\/*?:"<>|]', "_", filename)


def process_repository(repo_path, output_dir, ignore_dirs=None,
                       ignore_exts=None):
    """
    Process all files in a repository and create flattened files in the output
    directory.

    Args:
        repo_path (str): Path to the repository
        output_dir (str): Directory to output the processed files.
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

            file_count = 0
            skipped_count = 0
            try:
                # create new file with path information
                output_filename = sanitize_filename(f"{relative_path.replace('/', '_')}")
                output_filepath = os.path.join(output_dir, output_filename)

                with open(file_path, 'r', encoding='utf', errors='replace') as input_file:
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

    # create a manifest file with all paths
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


def main():
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