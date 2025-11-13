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
- **Progress bar** for visual feedback during processing
- **Parallel processing** for faster performance on large repositories
- **Memory optimization** with configurable file size limits
- **Intelligent caching** for instant manifest generation on unchanged repositories
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

# Disable progress bar
repo-flattener /path/to/repository --no-progress

# Parallel processing with 4 workers
repo-flattener /path/to/repository --workers 4

# Auto-detect optimal number of workers
repo-flattener /path/to/repository --workers 0

# Set maximum file size (10MB = 10485760 bytes)
repo-flattener /path/to/repository --max-file-size 10485760
```

### Progress Bar

By default, repo-flattener shows a progress bar when processing files:

```
Processing files: 100%|██████████| 1523/1523 [00:02<00:00, 615.24file/s]
```

The progress bar is automatically disabled in:
- Quiet mode (`--quiet`)
- When explicitly disabled (`--no-progress`)
- Non-interactive environments (e.g., CI/CD pipelines)

```bash
# With progress bar (default)
repo-flattener /path/to/repository

# Without progress bar
repo-flattener /path/to/repository --no-progress
```

### Parallel Processing

For large repositories, parallel processing can significantly speed up file processing:

```bash
# Use 4 parallel workers
repo-flattener /path/to/repository --workers 4

# Auto-detect optimal number of workers
repo-flattener /path/to/repository --workers 0

# Combine with other options
repo-flattener /path/to/repository --workers 4 --verbose
```

**Performance Tips:**
- Use 2-8 workers for best performance on most systems
- `--workers 0` auto-detects: `min(32, CPU_count + 4)`
- More workers = faster for I/O-bound operations (reading/writing files)
- Single worker (default) has lowest memory overhead

### Memory Optimization

For repositories with very large files, you can set a maximum file size to prevent loading huge files into memory:

```bash
# Skip files larger than 10MB
repo-flattener /path/to/repository --max-file-size 10485760

# Skip files larger than 50MB
repo-flattener /path/to/repository --max-file-size 52428800

# Combine with parallel processing
repo-flattener /path/to/repository --workers 4 --max-file-size 10485760
```

**Usage Tips:**
- `--max-file-size` accepts size in bytes (e.g., 10485760 for 10MB)
- Default is 0 (no limit) - all files will be processed
- Files exceeding the limit are skipped and logged as warnings
- Skipped files still appear in the manifest but are not flattened

### Manifest Caching

Repo-flattener automatically caches manifest generation to speed up repeated runs on unchanged repositories. The cache uses file modification times and sizes to detect changes.

```bash
# Default behavior - caching enabled
repo-flattener /path/to/repository

# Disable caching
repo-flattener /path/to/repository --no-cache

# Use custom cache directory
repo-flattener /path/to/repository --cache-dir /path/to/custom/cache
```

**How Caching Works:**
- On first run, the manifest is generated and cached with a signature based on file paths, modification times, and sizes
- On subsequent runs, if the repository hasn't changed (same files with same modification times), the cached manifest is used instantly
- If any file is modified, added, or removed, the cache is invalidated and the manifest is regenerated
- Cache is stored in `.repo_flattener_cache/` by default (ignored by git)
- Each repository/output directory combination has its own cache entry

**Performance Benefits:**
- **Instant manifest generation** for unchanged repositories (no file scanning needed)
- Particularly useful when running repo-flattener multiple times during development
- Cache automatically invalidates when files change, ensuring accuracy

**Cache Management:**
- Cache files are small (typically a few KB)
- No manual cache clearing needed - cache auto-invalidates on changes
- Use `--no-cache` to bypass cache for debugging or one-time runs
- Add `.repo_flattener_cache/` to your `.gitignore` (recommended)

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

# Export without progress bar
count, skipped, manifest = export(
    '/path/to/repository',
    'output',
    show_progress=False
)

# Parallel processing with 4 workers
count, skipped, manifest = export(
    '/path/to/repository',
    'output',
    max_workers=4
)

# Auto-detect optimal number of workers
count, skipped, manifest = export(
    '/path/to/repository',
    'output',
    max_workers=0  # Auto-detect
)

# Skip files larger than 10MB
count, skipped, manifest = export(
    '/path/to/repository',
    'output',
    max_file_size=10_000_000  # 10MB in bytes
)

# Combine parallel processing with file size limit
count, skipped, manifest = export(
    '/path/to/repository',
    'output',
    max_workers=4,
    max_file_size=10_000_000
)

# Disable caching
count, skipped, manifest = export(
    '/path/to/repository',
    'output',
    use_cache=False
)

# Custom cache directory
count, skipped, manifest = export(
    '/path/to/repository',
    'output',
    cache_dir='/path/to/custom/cache'
)

# Using process_repository (lower-level API)
process_repository('/path/to/repository', 'flattened_files', max_workers=4)

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