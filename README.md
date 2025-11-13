# Repo Flattener

A Python package to convert a repository into flattened files for easier uploading to Large Language Models (LLMs).

## Features

- Flattens repository structure by creating single files with path information
- Creates a manifest file showing the original structure
- Configurable ignore lists for directories and file extensions
- **Interactive mode** for selective file processing
- Simple command-line interface
- Python API for programmatic access

## Installation

### From PyPI

```bash
pip install repo-flattener
```

### From Source

```bash
git clone https://github.com/CruiseDevice/repo-flattener.git
cd repo-flattener
pip install -e .
```

## Usage

### Command Line

```bash
# Basic usage
repo-flattener /path/to/repository

# Specify output directory
repo-flattener /path/to/repository --output flattened_files

# Interactive mode - select files interactively
repo-flattener /path/to/repository --interactive

# Add custom directories to ignore
repo-flattener /path/to/repository --ignore-dirs build,dist

# Add custom file extensions to ignore
repo-flattener /path/to/repository --ignore-exts .log,.tmp
```

### Interactive Mode

Interactive mode allows you to manually select which files to process. This is useful when you want fine-grained control over which files to include.

```bash
repo-flattener /path/to/repository --interactive
```

In interactive mode, you'll see a list of all files and can use commands to select/deselect them:

- `all` or `a` - Select all files
- `none` or `n` - Deselect all files
- `toggle N` or `t N` - Toggle selection for file #N
- `range N-M` or `r N-M` - Toggle selection for files #N through #M
- `show` or `s` - Show current selection
- `done` or `d` - Finish selection and proceed
- `quit` or `q` - Cancel and exit

Example session:
```
> none          # Deselect all files
> range 1-5     # Select files 1 through 5
> toggle 10     # Also select file 10
> show          # Review selection
> done          # Process selected files
```

### Python API

```python
from repo_flattener import process_repository, scan_repository, interactive_file_selection

# Basic usage
process_repository('/path/to/repository', 'flattened_files')

# With custom ignore lists
process_repository(
    '/path/to/repository',
    'flattened_files',
    ignore_dirs=['build', 'dist'],
    ignore_exts=['.log', '.tmp']
)

# Scan repository to get list of files
files = scan_repository('/path/to/repository')
print(f"Found {len(files)} files")

# Interactive selection (in a script)
files = scan_repository('/path/to/repository')
selected_files = interactive_file_selection(files)
process_repository('/path/to/repository', 'output', file_list=selected_files)

# Process specific files only
process_repository(
    '/path/to/repository',
    'flattened_files',
    file_list=['README.md', 'src/main.py', 'src/utils.py']
)
```

## Output

The tool creates a directory with:

1. Flattened files named according to their original path (with path separators replaced by underscores)
2. A `file_manifest.txt` showing the original repository structure

## Development

### Running Tests

```bash
pytest
```

## License

MIT License