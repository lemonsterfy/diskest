"""
Sysbench benchmark test for Diskest
"""

import re
import os
import subprocess
from typing import Dict, Any, List
from .base_test import BaseTest


class SysbenchTest(BaseTest):
    """Sysbench benchmark test implementation."""

    name = "sysbench"
    required_tool = "sysbench"

    def __init__(self):
        super().__init__()

    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run the Sysbench benchmark test suite."""
        if not self.is_available():
            if not self.install():
                return {
                    "error": (
                        f"{self.name} is not installed "
                        f"and automatic installation failed"
                    ),
                    "install_instructions": self.get_install_instructions(),
                }

        self.logger.info("Starting Sysbench test suite")
        self.validate_config(config)
        self.prepare_test_directory(config)

        results = {}
        scenarios = [
            (self._sequential_read_test, "Sequential Read"),
            (self._sequential_write_test, "Sequential Write"),
            (self._random_read_test, "Random Read"),
            (self._random_write_test, "Random Write"),
            (self._random_rw_test, "Random Read/Write"),
            (self._fsync_test, "fsync Performance"),
            (self._latency_test, "I/O Latency"),
        ]

        for scenario, description in scenarios:
            self.logger.info(f"Starting {description} test")
            try:
                scenario_results = scenario(config)
                if scenario_results:
                    results.update(scenario_results)
                else:
                    self.logger.warning(f"No results generated for {description} test")
            except Exception as e:
                self.logger.error(f"Error during {description} test: {str(e)}")
                results[f"{description.lower().replace(' ', '_')}_error"] = str(e)
            finally:
                self.logger.info(f"Completed {description} test")
                self._cleanup(config)

        self.logger.info("Sysbench test suite completed")
        return results

    def _run_sysbench_test(self, params: List[str]) -> str:
        """Run a single Sysbench test."""
        stages = ["prepare", "run", "cleanup"]
        output = None

        for stage in stages:
            stage_params = params + [stage]
            try:
                self.logger.debug(f"Executing {stage}: {' '.join(stage_params)}")
                stage_output = subprocess.check_output(
                    stage_params,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                )
                self.logger.debug(f"{stage.capitalize()} stage output: {stage_output}")
                if stage == "run":
                    output = stage_output
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Sysbench {stage} failed: {e.output}")
                if stage == "run":
                    return None

        return output

    def _process_results(self, output: str, test_name: str) -> Dict[str, Any]:
        """Process Sysbench test results."""
        if not output:
            return {f"{test_name}_error": "Test execution failed"}

        patterns = {
            "read_iops": r"reads/s:\s+(\d+\.\d+)",
            "write_iops": r"writes/s:\s+(\d+\.\d+)",
            "read_bw": r"read, MiB/s:\s+(\d+\.\d+)",
            "write_bw": r"written, MiB/s:\s+(\d+\.\d+)",
            "latency_min": r"min:\s+(\d+\.\d+)",
            "latency_avg": r"avg:\s+(\d+\.\d+)",
            "latency_max": r"max:\s+(\d+\.\d+)",
            "latency_95th": r"95th percentile:\s+(\d+\.\d+)",
        }

        results = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, output)
            if match:
                results[f"{test_name}_{key}"] = float(match.group(1))
            else:
                results[f"{test_name}_{key}"] = 0
                self.logger.warning(
                    f"Could not find {key} in sysbench output for {test_name}"
                )

        return results

    def _get_base_params(self, config: Dict[str, Any]) -> List[str]:
        """Get base parameters for Sysbench tests."""
        return [
            "sysbench",
            "fileio",
            f"--file-total-size={config['file_total_size']}",
            "--file-test-mode=",
            f"--time={config['runtime']}",
            "--file-io-mode=async",
            "--file-extra-flags=direct",
            f"--file-num={config.get('num_files', min(os.cpu_count(), 4))}",
        ]

    def _sequential_read_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run sequential read test."""
        params = self._get_base_params(config)
        params[3] += "seqrd"
        params.extend([f"--file-block-size={config.get('seq_block_size', '1M')}"])
        output = self._run_sysbench_test(params)
        return self._process_results(output, "sequential_read")

    def _sequential_write_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run sequential write test."""
        params = self._get_base_params(config)
        params[3] += "seqwr"
        params.extend([f"--file-block-size={config.get('seq_block_size', '1M')}"])
        output = self._run_sysbench_test(params)
        return self._process_results(output, "sequential_write")

    def _random_read_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run random read test."""
        params = self._get_base_params(config)
        params[3] += "rndrd"
        params.extend([f"--file-block-size={config.get('rnd_block_size', '4K')}"])
        output = self._run_sysbench_test(params)
        return self._process_results(output, "random_read")

    def _random_write_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run random write test."""
        params = self._get_base_params(config)
        params[3] += "rndwr"
        params.extend([f"--file-block-size={config.get('rnd_block_size', '4K')}"])
        output = self._run_sysbench_test(params)
        return self._process_results(output, "random_write")

    def _random_rw_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run random read/write test."""
        params = self._get_base_params(config)
        params[3] += "rndrw"
        params.extend(
            [
                f"--file-block-size={config.get('rnd_block_size', '4K')}",
                f"--file-rw-ratio={config.get('rw_ratio', 2)}",
            ]
        )
        output = self._run_sysbench_test(params)
        return self._process_results(output, "random_rw")

    def _fsync_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run fsync performance test."""
        params = self._get_base_params(config)
        params[3] += "rndrw"
        params.extend(
            [
                f"--file-block-size={config.get('fsync_block_size', '4K')}",
                "--file-fsync-freq=1",
                "--file-fsync-all",
                f"--file-rw-ratio={config.get('fsync_rw_ratio', 2)}",
            ]
        )
        output = self._run_sysbench_test(params)
        return self._process_results(output, "fsync")

    def _latency_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run I/O latency test."""
        params = self._get_base_params(config)
        params[3] += "rndrw"
        params[2] = f"--file-total-size={config.get('latency_file_size', '1G')}"
        params[4] = f"--time={config.get('latency_time', 30)}"
        params.extend(
            [
                f"--file-block-size={config.get('latency_block_size', '4K')}",
                f"--file-rw-ratio={config.get('latency_rw_ratio', 2)}",
                "--file-num=1",
                "--file-io-mode=sync",
            ]
        )
        output = self._run_sysbench_test(params)
        return self._process_results(output, "latency")
