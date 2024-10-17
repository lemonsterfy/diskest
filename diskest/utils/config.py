"""
Configuration management module for Diskest
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.

    Args:
        config_path (Optional[str]): Path to the configuration file.
        If None, load default config.

    Returns:
        Dict[str, Any]: Loaded configuration

    Raises:
        FileNotFoundError: If the config file is not found
        yaml.YAMLError: If there's an error parsing the YAML file
    """
    default_config_path = Path(__file__).parent.parent / "data" / "default_config.yaml"

    try:
        with open(default_config_path, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Default config file not found: {default_config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing default config file: {e}")
        raise

    if config_path:
        try:
            with open(config_path, "r") as f:
                user_config = yaml.safe_load(f)
            config = deep_merge(config, user_config)
        except FileNotFoundError:
            logger.warning(f"User config file not found: {config_path}")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing user config file: {e}")
            raise

    # Ensure global settings are applied to each test
    global_settings = config.get("global", {})
    for key, value in config.items():
        if isinstance(value, dict) and key != "global":
            value.update({k: v for k, v in global_settings.items() if k not in value})

    return config


def deep_merge(dest: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform a deep merge of two dictionaries.

    Args:
        dest (Dict[str, Any]): Destination dictionary
        src (Dict[str, Any]): Source dictionary

    Returns:
        Dict[str, Any]: Merged dictionary
    """
    for k, v in src.items():
        if isinstance(v, dict):
            dest[k] = deep_merge(dest.get(k, {}), v)
        else:
            dest[k] = v
    return dest


def get_config_path() -> Path:
    """
    Get the path to the user's configuration file.

    Returns:
        Path: Path to the user's configuration file
    """
    return Path.home() / ".diskest" / "config.yaml"


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to a YAML file.

    Args:
        config (Dict[str, Any]): Configuration to save
        config_path (str): Path to save the configuration file

    Raises:
        PermissionError: If there's no write permission for the config file
    """
    try:
        with open(config_path, "w") as f:
            yaml.dump(config, f)
        logger.info(f"Configuration saved to {config_path}")
    except PermissionError:
        logger.error(f"No write permission for config file: {config_path}")
        raise
