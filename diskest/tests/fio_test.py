"""
FIO (Flexible I/O Tester) benchmark test for Diskest
"""

import json
import subprocess
from typing import Dict, Any
from .base_test import BaseTest


class FioTest(BaseTest):
    """FIO benchmark test implementation."""

    name = "fio"
    required_tool = "fio"
    default_ramp_time = "10s" 

    def __init__(self):
        super().__init__()

    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run the FIO benchmark test suite."""
        if not self.is_available():
            if not self.install():
                return {
                    "error": (
                        f"{self.name} is not installed "
                        f"and automatic installation failed"
                    ),
                    "install_instructions": self.get_install_instructions(),
                }

        self.logger.info("Starting FIO test suite")
        self.validate_config(config)
        self.prepare_test_directory(config)

        results = {}
        scenarios = [
            (self._sequential_read_test, "Sequential Read"),
            (self._sequential_write_test, "Sequential Write"),
            (self._random_read_test, "Random Read"),
            (self._random_write_test, "Random Write"),
            (self._mixed_rw_test, "Mixed Read/Write"),
            (self._latency_test, "Latency"),
        ]

        for scenario, description in scenarios:
            self.logger.info(f"Starting {description} test")
            scenario_results = scenario(config)
            if scenario_results:
                results.update(scenario_results)
            else:
                self.logger.warning(f"No results generated for {description} test")
            self.logger.info(f"Completed {description} test")
            self._cleanup(config)

        self.logger.info("FIO test suite completed")
        return results

    def _run_fio_test(self, job_file: str) -> Dict[str, Any]:
        """Run a single FIO test."""
        cmd = ["fio", "--output-format=json+", job_file]
        try:
            self.logger.debug(f"Executing command: {' '.join(cmd)}")
            output = subprocess.check_output(
                cmd, stderr=subprocess.PIPE, universal_newlines=True
            )
            return self._parse_fio_output(output)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"FIO test failed: {e.output}")
            self.logger.error(f"FIO stderr: {e.stderr}")
            return {"error": str(e)}

    def _parse_fio_output(self, output: str) -> Dict[str, Any]:
        """Parse FIO JSON output."""
        try:
            json_start = output.find("{")
            json_end = output.rfind("}") + 1
            if json_start != -1 and json_end != -1:
                return json.loads(output[json_start:json_end])
            raise ValueError("No valid JSON found in FIO output")
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse FIO test results: {str(e)}")
            self.logger.debug(f"Raw FIO output: {output}")
            return {"error": "Failed to parse FIO output"}

    def _process_results(
        self, raw_results: Dict[str, Any], test_name: str
    ) -> Dict[str, Any]:
        """Process raw FIO results into a standardized format."""
        if not raw_results or "error" in raw_results:
            return {f"{test_name}_error": raw_results.get("error", "Unknown error")}

        processed = {}
        for job in raw_results["jobs"]:
            for op in ["read", "write"]:
                if op in job:
                    key = f"{test_name}_{op}"
                    processed[key] = {}

                    processed[key]["iops"] = job[op].get("iops", 0)
                    processed[key]["bw"] = (
                        job[op].get("bw", 0) / 1024
                    )  # Convert to MB/s

                    lat_ns = job[op].get("lat_ns", {})
                    processed[key]["lat_avg"] = (
                        lat_ns.get("mean", 0) / 1000000
                    )  # Convert to ms
                    processed[key]["lat_min"] = lat_ns.get("min", 0) / 1000000
                    processed[key]["lat_max"] = lat_ns.get("max", 0) / 1000000

                    clat_ns = job[op].get("clat_ns", {})
                    percentiles = clat_ns.get("percentile", {})
                    for p in [
                        "50.000000",
                        "95.000000",
                        "99.000000",
                        "99.900000",
                        "99.990000",
                    ]:
                        processed[key][f"lat_p{p.split('.')[0]}"] = (
                            percentiles.get(p, 0) / 1000000
                        )

        return processed

    def _create_job_file(
        self, name: str, job_params: Dict[str, Any], config: Dict[str, Any]
    ) -> str:
        """Create an FIO job file."""
        job_file = f"/tmp/fio_{name}_job.fio"
        with open(job_file, "w") as f:
            f.write("[global]\n")
            f.write(f"directory={self.get_test_directory(config)}\n")
            f.write(f"runtime={job_params.get('runtime', config['runtime'])}\n")
            f.write(f"ramp_time={config.get('ramp_time', self.default_ramp_time)}\n")
            f.write("ioengine=libaio\n")
            f.write("direct=1\n")
            f.write("group_reporting\n")
            f.write("time_based\n")
            f.write(f"write_bw_log={self.get_test_directory(config)}/bw_log\n")
            f.write(f"write_lat_log={self.get_test_directory(config)}/lat_log\n")
            f.write(f"write_iops_log={self.get_test_directory(config)}/iops_log\n")
            f.write("log_avg_msec=1000\n")
            f.write(f"\n[{name}]\n")
            for key, value in job_params.items():
                f.write(f"{key}={value}\n")
        return job_file

    def _sequential_read_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run sequential read test."""
        job_file = self._create_job_file(
            "sequential_read",
            {
                "rw": "read",
                "bs": "1m",
                "iodepth": 32,
                "numjobs": 4,
                "size": config["size"],
            },
            config,
        )
        results = self._run_fio_test(job_file)
        return self._process_results(results, "sequential_read")

    def _sequential_write_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run sequential write test."""
        job_file = self._create_job_file(
            "sequential_write",
            {
                "rw": "write",
                "bs": "1m",
                "iodepth": 32,
                "numjobs": 4,
                "size": config["size"],
            },
            config,
        )
        results = self._run_fio_test(job_file)
        return self._process_results(results, "sequential_write")

    def _random_read_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run random read test."""
        job_file = self._create_job_file(
            "random_read",
            {
                "rw": "randread",
                "bs": "4k",
                "iodepth": 64,
                "numjobs": 4,
                "size": config["size"],
            },
            config,
        )
        results = self._run_fio_test(job_file)
        return self._process_results(results, "random_read")

    def _random_write_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run random write test."""
        job_file = self._create_job_file(
            "random_write",
            {
                "rw": "randwrite",
                "bs": "4k",
                "iodepth": 64,
                "numjobs": 4,
                "size": config["size"],
            },
            config,
        )
        results = self._run_fio_test(job_file)
        return self._process_results(results, "random_write")

    def _mixed_rw_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run mixed read/write test."""
        job_file = self._create_job_file(
            "mixed_rw",
            {
                "rw": "randrw",
                "rwmixread": 70,
                "bs": "4k",
                "iodepth": 64,
                "numjobs": 4,
                "size": config["size"],
            },
            config,
        )
        results = self._run_fio_test(job_file)
        return self._process_results(results, "mixed_rw")

    def _latency_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run latency test."""
        job_file = self._create_job_file(
            "latency",
            {
                "rw": "randread",
                "bs": "4k",
                "iodepth": 1,
                "numjobs": 1,
                "size": "1G",
                "runtime": "30s",
            },
            config,
        )
        results = self._run_fio_test(job_file)
        return self._process_results(results, "latency")
