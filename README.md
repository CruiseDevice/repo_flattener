# Repo Flattener

A Python package to convert a repository into flattened files for easier uploading to Large Language Models (LLMs).

## Features

- Flattens repository structure by creating single files with path information
- Creates a manifest file showing the original structure
- Configurable ignore lists for directories and file extensions
- Simple command-line interface

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

# Add custom directories to ignore
repo-flattener /path/to/repository --ignore-dirs build,dist

# Add custom file extensions to ignore
repo-flattener /path/to/repository --ignore-exts .log,.tmp
```

### Python API

```python
from repo_flattener import process_repository

# Basic usage
process_repository('/path/to/repository', 'flattened_files')

# With custom ignore lists
process_repository(
    '/path/to/repository',
    'flattened_files',
    ignore_dirs=['build', 'dist'],
    ignore_exts=['.log', '.tmp']
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