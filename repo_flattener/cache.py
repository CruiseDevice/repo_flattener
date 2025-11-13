"""
Caching functionality for repo_flattener to optimize manifest generation
"""

import os
import json
import hashlib
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class ManifestCache:
    """Cache for manifest generation to avoid reprocessing unchanged repositories."""

    def __init__(self, cache_dir: str = ".repo_flattener_cache"):
        """
        Initialize the manifest cache.

        Args:
            cache_dir: Directory to store cache files (default: .repo_flattener_cache)
        """
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "manifest_cache.json")

    def _get_repo_signature(self, repo_path: str, file_list: List[str]) -> str:
        """
        Generate a unique signature for the repository state based on file paths
        and modification times.

        Args:
            repo_path: Path to the repository
            file_list: List of relative file paths

        Returns:
            SHA256 hash representing the repository state
        """
        # Create a signature based on file paths and their modification times
        signature_data = []

        for relative_path in sorted(file_list):
            file_path = os.path.join(repo_path, relative_path)
            if os.path.exists(file_path):
                try:
                    mtime = os.path.getmtime(file_path)
                    file_size = os.path.getsize(file_path)
                    signature_data.append(f"{relative_path}:{mtime}:{file_size}")
                except OSError:
                    # If we can't get file info, include path only
                    signature_data.append(f"{relative_path}:0:0")

        # Hash the combined signature
        signature_str = "\n".join(signature_data)
        return hashlib.sha256(signature_str.encode('utf-8')).hexdigest()

    def _load_cache(self) -> Dict:
        """
        Load cache data from disk.

        Returns:
            Dictionary containing cache data, or empty dict if cache doesn't exist
        """
        if not os.path.exists(self.cache_file):
            logger.debug("No cache file found")
            return {}

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                logger.debug(f"Loaded cache with {len(cache_data)} entries")
                return cache_data
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load cache: {e}")
            return {}

    def _save_cache(self, cache_data: Dict) -> None:
        """
        Save cache data to disk.

        Args:
            cache_data: Dictionary containing cache data
        """
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
                logger.debug(f"Saved cache with {len(cache_data)} entries")
        except OSError as e:
            logger.warning(f"Failed to save cache: {e}")

    def get_cached_manifest(
        self,
        repo_path: str,
        output_dir: str,
        file_list: List[str]
    ) -> Optional[str]:
        """
        Retrieve cached manifest if it's still valid.

        Args:
            repo_path: Path to the repository
            output_dir: Output directory for the manifest
            file_list: List of relative file paths

        Returns:
            Path to cached manifest if valid, None otherwise
        """
        # Generate signature for current repository state
        current_signature = self._get_repo_signature(repo_path, file_list)

        # Load cache
        cache_data = self._load_cache()

        # Create cache key based on repo and output paths
        cache_key = f"{os.path.abspath(repo_path)}:{os.path.abspath(output_dir)}"

        if cache_key in cache_data:
            cached_entry = cache_data[cache_key]
            cached_signature = cached_entry.get("signature", "")
            cached_manifest_path = cached_entry.get("manifest_path", "")

            # Check if signature matches and manifest file still exists
            if (current_signature == cached_signature and
                os.path.exists(cached_manifest_path)):
                logger.info("Using cached manifest (repository unchanged)")
                return cached_manifest_path
            else:
                logger.debug("Cache invalid: repository has changed or manifest missing")
        else:
            logger.debug("No cache entry found for this repository")

        return None

    def save_manifest_cache(
        self,
        repo_path: str,
        output_dir: str,
        file_list: List[str],
        manifest_path: str
    ) -> None:
        """
        Save manifest information to cache.

        Args:
            repo_path: Path to the repository
            output_dir: Output directory for the manifest
            file_list: List of relative file paths
            manifest_path: Path to the generated manifest
        """
        # Generate signature for current repository state
        current_signature = self._get_repo_signature(repo_path, file_list)

        # Load existing cache
        cache_data = self._load_cache()

        # Create cache key
        cache_key = f"{os.path.abspath(repo_path)}:{os.path.abspath(output_dir)}"

        # Update cache entry
        cache_data[cache_key] = {
            "signature": current_signature,
            "manifest_path": manifest_path,
            "file_count": len(file_list),
            "cached_at": os.path.getmtime(manifest_path) if os.path.exists(manifest_path) else 0
        }

        # Save cache
        self._save_cache(cache_data)
        logger.debug(f"Cached manifest for {cache_key}")

    def clear_cache(self) -> bool:
        """
        Clear all cached data.

        Returns:
            True if cache was cleared successfully, False otherwise
        """
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                logger.info("Cache cleared successfully")
                return True
            else:
                logger.debug("No cache file to clear")
                return True
        except OSError as e:
            logger.warning(f"Failed to clear cache: {e}")
            return False

    def get_cache_info(self) -> Dict:
        """
        Get information about the current cache state.

        Returns:
            Dictionary containing cache statistics
        """
        cache_data = self._load_cache()

        return {
            "cache_exists": os.path.exists(self.cache_file),
            "cache_entries": len(cache_data),
            "cache_file": self.cache_file,
            "cache_size_bytes": os.path.getsize(self.cache_file) if os.path.exists(self.cache_file) else 0
        }
