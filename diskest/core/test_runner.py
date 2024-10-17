"""
Test runner module for Diskest
"""

import logging
from typing import Dict, Any, Callable
from .system_info import SystemInfo
from .hardware_detection import HardwareDetector
from diskest.tests.fio_test import FioTest
from diskest.tests.sysbench_test import SysbenchTest

logger = logging.getLogger(__name__)


class TestRunner:
    """Runs disk benchmark tests and collects results."""

    def __init__(
        self,
        config: Dict[str, Any],
        progress_callback: Callable[[float], None] = None,
    ):
        self.config = config
        self.system_info = SystemInfo()
        self.hardware_detector = HardwareDetector()
        self.progress_callback = progress_callback

    def run_tests(self) -> Dict[str, Any]:
        """
        Run all configured tests.

        Returns:
            Dict[str, Any]: Dictionary containing all results and information.
        """
        logger.info("Starting test suite")
        results = {
            "system_info": self.system_info.collect(),
            "hardware_info": self.hardware_detector.detect(),
            "tests": {},
        }

        tests = [FioTest(), SysbenchTest()]
        total_tests = len(tests)

        for i, test in enumerate(tests, 1):
            logger.info(f"Running {test.name} test")
            try:
                # Start with global config
                test_config = self.config.get("global", {}).copy()
                # Overwriting global settings by test-specific config if necessary
                test_config.update(self.config.get(test.name, {}))
                results["tests"][test.name] = test.run(test_config)
                logger.info(f"{test.name} test completed successfully")
            except Exception as e:
                logger.error(f"Error running {test.name} test: {str(e)}")
                results["tests"][test.name] = {"error": str(e)}

            if self.progress_callback:
                self.progress_callback(i / total_tests * 100)

        logger.info("Test suite completed")
        return results
