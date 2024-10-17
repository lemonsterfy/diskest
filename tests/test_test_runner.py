import pytest
from unittest.mock import patch, MagicMock
from diskest.core.test_runner import TestRunner
import warnings

# Ignore the specific warning
warnings.filterwarnings("ignore", message="cannot collect test class 'TestRunner'")


@pytest.fixture
def sample_config():
    return {
        "global": {"test_directory": "/tmp/diskest_test"},
        "fio": {"size": "1G", "runtime": "60s"},
        "sysbench": {"file_total_size": "1G", "runtime": 60},
    }


@pytest.fixture
def test_runner(sample_config):
    with patch("diskest.core.test_runner.SystemInfo") as mock_system_info, patch(
        "diskest.core.test_runner.HardwareDetector"
    ) as mock_hardware_detector:
        mock_system_info.return_value.collect.return_value = {
            "os": {"distro": "Debian GNU/Linux 12 (bookworm)"}
        }
        mock_hardware_detector.return_value.detect.return_value = {"mock": "data"}
        yield TestRunner(sample_config)


@patch("diskest.core.test_runner.FioTest")
@patch("diskest.core.test_runner.SysbenchTest")
def test_run_tests(mock_sysbench, mock_fio, test_runner):
    # Set up mock FioTest
    mock_fio_instance = MagicMock()
    mock_fio_instance.name = "fio"
    mock_fio_instance.run.return_value = {"fio_result": "data"}
    mock_fio.return_value = mock_fio_instance

    # Set up mock SysbenchTest
    mock_sysbench_instance = MagicMock()
    mock_sysbench_instance.name = "sysbench"
    mock_sysbench_instance.run.return_value = {"sysbench_result": "data"}
    mock_sysbench.return_value = mock_sysbench_instance

    results = test_runner.run_tests()

    assert "system_info" in results
    assert results["system_info"]["os"]["distro"] == "Debian GNU/Linux 12 (bookworm)"
    assert "hardware_info" in results
    assert "tests" in results
    assert "fio" in results["tests"]
    assert "sysbench" in results["tests"]
    assert results["tests"]["fio"] == {"fio_result": "data"}
    assert results["tests"]["sysbench"] == {"sysbench_result": "data"}

    # Verify that the mocks were called
    mock_fio_instance.run.assert_called_once()
    mock_sysbench_instance.run.assert_called_once()
    test_runner.system_info.collect.assert_called_once()
    test_runner.hardware_detector.detect.assert_called_once()
