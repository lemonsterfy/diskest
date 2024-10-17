import pytest
from unittest.mock import patch
from diskest.tests.fio_test import FioTest


@pytest.fixture
def fio_test():
    return FioTest()


def test_fio_available(fio_test):
    with patch("shutil.which", return_value="/usr/bin/fio"):
        assert fio_test.is_available()


@patch("subprocess.check_output")
@patch.object(FioTest, "prepare_test_directory")
def test_run_fio_test(mock_prepare, mock_check_output, fio_test):
    mock_check_output.return_value = (
        '{"jobs": [{"read": {"iops": 1000, "bw": 102400}}]}'
    )
    mock_prepare.return_value = None
    config = {"size": "1G", "runtime": "60s", "test_directory": "/tmp/diskest_test"}
    result = fio_test.run(config)

    expected_tests = [
        "sequential_read",
        "sequential_write",
        "random_read",
        "random_write",
        "mixed_rw",
        "latency",
    ]
    for test in expected_tests:
        assert (
            f"{test}_read" in result or f"{test}_write" in result
        ), f"Missing {test} test results"

    for test_result in result.values():
        assert "iops" in test_result
        assert "bw" in test_result
        assert "lat_avg" in test_result
        assert "lat_min" in test_result
        assert "lat_max" in test_result
        assert "lat_p95" in test_result

    assert any(test_result["iops"] == 1000 for test_result in result.values())

    mock_prepare.assert_called_once_with(config)
