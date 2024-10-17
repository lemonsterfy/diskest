import sys
import os
import pytest
from unittest.mock import MagicMock

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def sample_config():
    """Provide a sample configuration for testing."""
    return {
        "global": {"test_directory": "/tmp/diskest_test", "verbose": False},
        "fio": {"size": "1G", "runtime": "60s"},
        "sysbench": {"file_total_size": "1G", "runtime": 60},
    }


@pytest.fixture
def sample_results():
    """Provide sample test results for testing."""
    return {
        "system_info": {
            "os": {"distro": "Debian GNU/Linux 12 (bookworm)"},
            "cpu": {"physical_cores": 4, "total_cores": 8},
            "memory": {"total": 16000000000},
        },
        "hardware_info": {"raid": {"detected": False}},
        "tests": {
            "fio": {
                "sequential_read_read": {
                    "iops": 1000,
                    "bw": 500,
                    "lat_avg": 5,
                    "lat_min": 1,
                    "lat_max": 10,
                    "lat_p95": 8,
                }
            }
        },
    }


@pytest.fixture
def mock_debian_system():
    """Mock system information for Debian 12.7."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("platform.system", lambda: "Linux")
        mp.setattr("platform.release", lambda: "6.1.0-18-amd64")
        mp.setattr("distro.name", lambda pretty=False: "Debian GNU/Linux 12 (bookworm)")
        mp.setattr("distro.version", lambda: "12.7")
        yield


@pytest.fixture
def mock_cpu_info():
    """Mock CPU information."""
    cpu_info = MagicMock()
    cpu_info.physical = 4
    cpu_info.total = 8
    cpu_info.max = 3.5
    cpu_info.min = 2.0
    cpu_info.current = 2.8
    return cpu_info


@pytest.fixture
def mock_memory_info():
    """Mock memory information."""
    memory_info = MagicMock()
    memory_info.total = 16000000000  # 16 GB
    memory_info.available = 8000000000
    memory_info.used = 8000000000
    memory_info.percent = 50.0
    return memory_info


@pytest.fixture
def mock_disk_info():
    """Mock disk information."""
    return {
        "/dev/sda1": {
            "mountpoint": "/",
            "fstype": "ext4",
            "total": 100000000000,  # 100 GB
            "used": 50000000000,
            "free": 50000000000,
            "percent": 50.0,
        }
    }


@pytest.fixture
def mock_hardware_detector(mock_disk_info):
    """Mock HardwareDetector."""
    detector = MagicMock()
    detector._detect_storage_devices.return_value = mock_disk_info
    detector._detect_raid.return_value = {
        "detected": False,
        "type": None,
        "details": None,
    }
    return detector


@pytest.fixture
def mock_fio_output():
    """Mock FIO test output."""
    return {
        "jobs": [
            {
                "job options": {"name": "sequential_read"},
                "read": {
                    "io_bytes": 1073741824,
                    "bw": 512000,
                    "iops": 1000,
                    "lat_ns": {
                        "min": 1000000,
                        "max": 10000000,
                        "mean": 5000000,
                        "stddev": 1000000,
                    },
                },
            }
        ]
    }


@pytest.fixture
def mock_sysbench_output():
    """Mock Sysbench test output."""
    return (
        "sysbench 1.0.20 (using system LuaJIT 2.1.0-beta3)\n"
        "Running the test with following options:\n"
        "Number of threads: 1\n"
        "Initializing random number generator from current time\n"
        "\n"
        "File operations:\n"
        "    reads/s:                      10000.00\n"
        "    writes/s:                     3333.33\n"
        "    fsyncs/s:                     1111.11\n"
        "\n"
        "Throughput:\n"
        "    read, MiB/s:                  156.25\n"
        "    written, MiB/s:               52.08\n"
        "\n"
        "General statistics:\n"
        "    total time:                          10.0001s\n"
        "    total number of events:              100000\n"
        "\n"
        "Latency (ms):\n"
        "         min:                                    0.01\n"
        "         avg:                                    0.10\n"
        "         max:                                    1.00\n"
        "         95th percentile:                        0.20\n"
        "         sum:                                10000.10\n"
    )
