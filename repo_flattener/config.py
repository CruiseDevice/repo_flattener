"""
Configuration file handling for repo_flattener
"""

import os
import yaml
from typing import Dict, Any, Optional
import logging

from repo_flattener.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to configuration file. If None, looks for .repo-flattener.yml
                    in current directory

    Returns:
        Dictionary containing configuration options

    Raises:
        ConfigurationError: If configuration file is invalid
    """
    if config_path is None:
        # Look for default config file in current directory
        config_path = '.repo-flattener.yml'
        if not os.path.exists(config_path):
            logger.debug("No configuration file found, using defaults")
            return {}

    if not os.path.exists(config_path):
        raise ConfigurationError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}

        logger.debug(f"Loaded configuration from {config_path}")
        return config
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in configuration file: {e}")
    except Exception as e:
        raise ConfigurationError(f"Error reading configuration file: {e}")


def merge_config_with_args(config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Merge configuration file options with command-line arguments.
    Command-line arguments take precedence.

    Args:
        config: Configuration dictionary from file
        **kwargs: Command-line arguments

    Returns:
        Merged configuration dictionary
    """
    merged = config.copy()

    # Override with command-line arguments if provided
    for key, value in kwargs.items():
        if value is not None:
            merged[key] = value

    return merged
