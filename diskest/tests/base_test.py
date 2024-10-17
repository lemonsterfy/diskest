"""
Base test class for Diskest benchmark tests
"""

import logging
import shutil
import subprocess
import os
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTest(ABC):
    """Base class for all benchmark tests."""

    name = ""
    required_tool = ""
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def is_available(cls) -> bool:
        """Check if the required tool for this test is available."""
        return shutil.which(cls.required_tool) is not None

    @classmethod
    def install(cls) -> bool:
        """Attempt to install the required tool for this test."""
        cls.logger.info(f"Attempting to install {cls.name}...")

        if os.geteuid() != 0:
            cls.logger.error(
                f"Root privileges required to install {cls.name}. "
                f"Please run with sudo."
            )
            return False

        package_manager = cls._get_package_manager()
        if not package_manager:
            cls.logger.error(
                "Unsupported package manager. Please install dependencies manually."
            )
            return False

        try:
            subprocess.run(f"{package_manager} update", shell=True, check=True)
            subprocess.run(
                f"{package_manager} install -y "
                f"{cls.get_package_name(package_manager)}",
                shell=True,
                check=True,
            )
            cls.logger.info(f"Successfully installed {cls.name}")
            return True
        except subprocess.CalledProcessError as e:
            cls.logger.error(f"Failed to install {cls.name}: {str(e)}")
            return False

    @staticmethod
    def _get_package_manager() -> str:
        """Detect the system's package manager."""
        if shutil.which("apt-get"):
            return "apt-get"
        elif shutil.which("yum"):
            return "yum"
        return None

    @classmethod
    def get_package_name(cls, package_manager: str) -> str:
        """Get the package name for the required tool."""
        return cls.required_tool

    @classmethod
    def get_install_instructions(cls) -> str:
        """Get installation instructions for the required tool."""
        return (
            f"sudo apt-get install {cls.get_package_name('apt-get')}  "
            f"# For Ubuntu/Debian\n"
            f"sudo yum install {cls.get_package_name('yum')}  "
            f"# For CentOS/RHEL"
        )

    @staticmethod
    def get_test_directory(config: Dict[str, Any]) -> str:
        """
        Get the test directory from the configuration.

        This method checks for both 'test_directory' and 'directory' keys
        to maintain backwards compatibility.

        Args:
            config (Dict[str, Any]): Test configuration

        Returns:
            str: Path to the test directory

        Raises:
            ValueError: If neither 'test_directory' nor 'directory'
            is found in the config
        """
        test_dir = config.get("test_directory")
        if not test_dir:
            raise ValueError("Test directory not specified in configuration")
        return test_dir

    @abstractmethod
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the benchmark test.

        Args:
            config (Dict[str, Any]): Test configuration

        Returns:
            Dict[str, Any]: Test results
        """
        raise NotImplementedError("Subclasses must implement run method")

    def _cleanup(self, config: Dict[str, Any]) -> None:
        """Clean up test files and directories."""
        test_dir = self.get_test_directory(config)
        try:
            for item in os.listdir(test_dir):
                item_path = os.path.join(test_dir, item)
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            self.logger.info(f"Cleaned up test directory: {test_dir}")
        except Exception as e:
            self.logger.error(f"Error during cleanup of {test_dir}: {str(e)}")

    def prepare_test_directory(self, config: Dict[str, Any]) -> None:
        """Prepare the test directory."""
        test_dir = self.get_test_directory(config)
        try:
            os.makedirs(test_dir, exist_ok=True)
            self.logger.info(f"Prepared test directory: {test_dir}")
        except Exception as e:
            self.logger.error(f"Error preparing test directory {test_dir}: {str(e)}")
            raise

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate the test configuration."""
        try:
            self.get_test_directory(config)
        except ValueError as e:
            raise ValueError(f"Invalid configuration: {str(e)}")

        if "runtime" not in config:
            raise ValueError("Missing required configuration key: runtime")
