"""
Tests for repo_flattener package
"""

import os
import tempfile
import shutil
import pytest
from repo_flattener.core import (
    sanitize_filename,
    process_repository,
    create_manifest,
    IGNORE_DIRS,
    IGNORE_EXTS
)


class TestSanitizeFilename:
    """Tests for the sanitize_filename function"""

    def test_sanitize_filename_with_invalid_chars(self):
        """Test that invalid characters are replaced with underscores"""
        assert sanitize_filename('file/with\\slashes.txt') == 'file_with_slashes.txt'
        assert sanitize_filename('file:with*special?.txt') == 'file_with_special_.txt'
        assert sanitize_filename('file<with>pipes|.txt') == 'file_with_pipes_.txt'
        assert sanitize_filename('file"with"quotes.txt') == 'file_with_quotes.txt'

    def test_sanitize_filename_with_valid_chars(self):
        """Test that valid filenames remain unchanged"""
        assert sanitize_filename('normal_file.txt') == 'normal_file.txt'
        assert sanitize_filename('file-with-dashes.txt') == 'file-with-dashes.txt'


class TestProcessRepository:
    """Tests for the process_repository function"""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository for testing"""
        temp_dir = tempfile.mkdtemp()

        # Create test directory structure
        os.makedirs(os.path.join(temp_dir, 'src'))
        os.makedirs(os.path.join(temp_dir, 'tests'))
        os.makedirs(os.path.join(temp_dir, '.git'))
        os.makedirs(os.path.join(temp_dir, 'node_modules'))

        # Create test files
        with open(os.path.join(temp_dir, 'README.md'), 'w') as f:
            f.write('# Test Repository\n')

        with open(os.path.join(temp_dir, 'src', 'main.py'), 'w') as f:
            f.write('print("Hello World")\n')

        with open(os.path.join(temp_dir, 'src', 'utils.py'), 'w') as f:
            f.write('def helper():\n    pass\n')

        with open(os.path.join(temp_dir, 'tests', 'test_main.py'), 'w') as f:
            f.write('def test_something():\n    assert True\n')

        # Create files that should be ignored
        with open(os.path.join(temp_dir, '.git', 'config'), 'w') as f:
            f.write('[core]\n')

        with open(os.path.join(temp_dir, 'node_modules', 'package.json'), 'w') as f:
            f.write('{}\n')

        with open(os.path.join(temp_dir, 'compiled.pyc'), 'w') as f:
            f.write('compiled\n')

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def temp_output(self):
        """Create a temporary output directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_process_repository_basic(self, temp_repo, temp_output):
        """Test basic repository processing"""
        file_count, skipped_count, manifest_path = process_repository(
            temp_repo, temp_output
        )

        # Should process 4 files: README.md, src/main.py, src/utils.py, tests/test_main.py
        assert file_count == 4
        assert skipped_count == 0

        # Check that output files exist
        assert os.path.exists(os.path.join(temp_output, 'README.md'))
        assert os.path.exists(os.path.join(temp_output, 'src_main.py'))
        assert os.path.exists(os.path.join(temp_output, 'src_utils.py'))
        assert os.path.exists(os.path.join(temp_output, 'tests_test_main.py'))

        # Check that manifest was created
        assert os.path.exists(manifest_path)
        assert manifest_path == os.path.join(temp_output, 'file_manifest.txt')

    def test_process_repository_ignores_default_dirs(self, temp_repo, temp_output):
        """Test that default ignored directories are skipped"""
        process_repository(temp_repo, temp_output)

        # Files from .git and node_modules should not be in output
        assert not os.path.exists(os.path.join(temp_output, '.git_config'))
        assert not os.path.exists(os.path.join(temp_output, 'node_modules_package.json'))

    def test_process_repository_ignores_default_extensions(self, temp_repo, temp_output):
        """Test that default ignored extensions are skipped"""
        process_repository(temp_repo, temp_output)

        # .pyc files should not be in output
        assert not os.path.exists(os.path.join(temp_output, 'compiled.pyc'))

    def test_process_repository_custom_ignore_dirs(self, temp_repo, temp_output):
        """Test custom ignore directories"""
        file_count, _, _ = process_repository(
            temp_repo, temp_output, ignore_dirs=['tests']
        )

        # Should skip tests directory, so only 3 files
        assert file_count == 3
        assert not os.path.exists(os.path.join(temp_output, 'tests_test_main.py'))

    def test_process_repository_custom_ignore_exts(self, temp_repo, temp_output):
        """Test custom ignore extensions"""
        file_count, _, _ = process_repository(
            temp_repo, temp_output, ignore_exts=['.md']
        )

        # Should skip .md files
        assert file_count == 3
        assert not os.path.exists(os.path.join(temp_output, 'README.md'))

    def test_process_repository_file_content(self, temp_repo, temp_output):
        """Test that file content is correctly written with path header"""
        process_repository(temp_repo, temp_output)

        output_file = os.path.join(temp_output, 'src_main.py')
        with open(output_file, 'r') as f:
            content = f.read()

        # Check that file has the path header
        assert content.startswith('// FILE: src/main.py\n\n')
        assert 'print("Hello World")' in content

    def test_process_repository_creates_output_dir(self, temp_repo):
        """Test that output directory is created if it doesn't exist"""
        temp_output = os.path.join(tempfile.gettempdir(), 'test_output_created')

        # Ensure it doesn't exist
        if os.path.exists(temp_output):
            shutil.rmtree(temp_output)

        try:
            process_repository(temp_repo, temp_output)
            assert os.path.exists(temp_output)
        finally:
            if os.path.exists(temp_output):
                shutil.rmtree(temp_output)



class TestCreateManifest:
    """Tests for the create_manifest function"""

    @pytest.fixture
    def temp_output(self):
        """Create a temporary output directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_create_manifest_simple(self, temp_output):
        """Test manifest creation with simple file list"""
        files = ['README.md', 'src/main.py', 'src/utils.py']
        manifest_path = create_manifest(temp_output, files)

        assert os.path.exists(manifest_path)

        with open(manifest_path, 'r') as f:
            content = f.read()

        assert 'Repository structure:' in content
        assert 'README.md' in content
        assert 'src' in content
        assert 'main.py' in content
        assert 'utils.py' in content

    def test_create_manifest_nested_structure(self, temp_output):
        """Test manifest with nested directory structure"""
        files = [
            'README.md',
            'src/main.py',
            'src/lib/helper.py',
            'tests/unit/test_main.py'
        ]
        manifest_path = create_manifest(temp_output, files)

        with open(manifest_path, 'r') as f:
            content = f.read()

        # Check structure is represented
        assert 'src' in content
        assert 'lib' in content
        assert 'tests' in content
        assert 'unit' in content

    def test_create_manifest_empty_list(self, temp_output):
        """Test manifest with empty file list"""
        files = []
        manifest_path = create_manifest(temp_output, files)

        assert os.path.exists(manifest_path)

        with open(manifest_path, 'r') as f:
            content = f.read()

        assert 'Repository structure:' in content


class TestConstants:
    """Tests for module constants"""

    def test_ignore_dirs_contains_common_dirs(self):
        """Test that IGNORE_DIRS contains common directories"""
        assert '.git' in IGNORE_DIRS
        assert 'node_modules' in IGNORE_DIRS
        assert '__pycache' in IGNORE_DIRS
        assert 'venv' in IGNORE_DIRS

    def test_ignore_exts_contains_common_exts(self):
        """Test that IGNORE_EXTS contains common extensions"""
        assert '.pyc' in IGNORE_EXTS
        assert '.class' in IGNORE_EXTS
        assert '.exe' in IGNORE_EXTS
