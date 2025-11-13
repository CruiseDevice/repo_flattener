# Repo Flattener

A Python package to convert a repository into flattened files for easier uploading to Large Language Models (LLMs).

## Features

- Flattens repository structure by creating single files with path information
- Creates a manifest file showing the original structure
- Configurable ignore lists for directories and file extensions
- **Interactive mode** for selective file processing
- **Type-safe** with full type hints
- **Robust error handling** with custom exceptions
- **Configurable logging** with verbose and quiet modes
- **Configuration file support** (.repo-flattener.yml)
- Simple command-line interface
- Clean Python API for programmatic access

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

# Verbose output (DEBUG level)
repo-flattener /path/to/repository --verbose

# Quiet mode (errors only)
repo-flattener /path/to/repository --quiet
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
from repo_flattener import export, process_repository, scan_repository

# Simplest usage with export function
count, skipped, manifest = export('/path/to/repository', 'output')
print(f"Processed {count} files, skipped {skipped}")

# Export with options
count, skipped, manifest = export(
    '/path/to/repository',
    output_dir='flattened_files',
    ignore_dirs=['build', 'dist'],
    ignore_exts=['.log', '.tmp']
)

# Export with interactive mode
count, skipped, manifest = export(
    '/path/to/repository',
    'output',
    interactive=True  # Opens interactive file selector
)

# Using process_repository (lower-level API)
process_repository('/path/to/repository', 'flattened_files')

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

# Error handling
from repo_flattener import InvalidRepositoryError, OutputDirectoryError

try:
    export('/path/to/repository', 'output')
except InvalidRepositoryError as e:
    print(f"Invalid repository: {e}")
except OutputDirectoryError as e:
    print(f"Cannot create output: {e}")
```

## Output

The tool creates a directory with:

1. Flattened files named according to their original path (with path separators replaced by underscores)
2. A `file_manifest.txt` showing the original repository structure

## Configuration File

You can create a `.repo-flattener.yml` configuration file in your repository for default settings:

```yaml
# .repo-flattener.yml
ignore_dirs:
  - build
  - dist
  - coverage
ignore_exts:
  - .log
  - .tmp
  - .cache
output_dir: flattened_output
```

The CLI will automatically load this file if present. Command-line arguments override configuration file settings.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=repo_flattener --cov-report=html

# Run in verbose mode
pytest -v
```

### Installing Development Dependencies

```bash
pip install -e ".[dev]"
```

## License

MIT License