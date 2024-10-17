import pytest
from unittest.mock import patch
from diskest.tests.sysbench_test import SysbenchTest


@pytest.fixture
def sysbench_test():
    return SysbenchTest()


def test_sysbench_available(sysbench_test):
    with patch("shutil.which", return_value="/usr/bin/sysbench"):
        assert sysbench_test.is_available()


@patch("subprocess.check_output")
@patch.object(SysbenchTest, "prepare_test_directory")
@patch.object(SysbenchTest, "_cleanup")
def test_run_sysbench_test(
    mock_cleanup, mock_prepare, mock_check_output, sysbench_test
):
    mock_output = """
    File operations:
       reads/s:                      631.73
       writes/s:                     421.15
       fsyncs/s:                     140.38

    Throughput:
       read, MiB/s:                  9.87
       written, MiB/s:               6.58

    Latency (ms):
         min:                                  0.03
         avg:                                  1.58
         max:                                 11.34
         95th percentile:                      4.33
    """
    mock_check_output.return_value = mock_output

    config = {
        "file_total_size": "1G",
        "runtime": 60,
        "test_directory": "/tmp/diskest_test",
    }

    result = sysbench_test.run(config)

    expected_tests = [
        "sequential_read",
        "sequential_write",
        "random_read",
        "random_write",
        "random_rw",
        "fsync",
        "latency",
    ]

    expected_metrics = [
        "read_iops",
        "write_iops",
        "read_bw",
        "write_bw",
        "latency_min",
        "latency_avg",
        "latency_max",
        "latency_95th",
    ]

    for test in expected_tests:
        for metric in expected_metrics:
            key = f"{test}_{metric}"
            assert key in result, f"{key} not found in result"
            assert isinstance(result[key], (int, float)), f"{key} is not a number"

    assert result["sequential_read_read_iops"] > 0
    assert result["sequential_read_read_bw"] > 0
    assert result["sequential_read_latency_avg"] > 0
    assert result["sequential_read_latency_95th"] > 0

    print("Test result:", result)


@patch("subprocess.check_output")
@patch.object(SysbenchTest, "prepare_test_directory")
@patch.object(SysbenchTest, "_cleanup")
def test_run_sysbench_test_error(
    mock_cleanup, mock_prepare, mock_check_output, sysbench_test
):
    mock_check_output.side_effect = Exception("Sysbench execution failed")

    config = {
        "file_total_size": "1G",
        "runtime": 60,
        "test_directory": "/tmp/diskest_test",
    }

    result = sysbench_test.run(config)

    expected_errors = [
        "sequential_read_error",
        "sequential_write_error",
        "random_read_error",
        "random_write_error",
        "random_read/write_error",
        "fsync_performance_error",
        "i/o_latency_error",
    ]

    for error in expected_errors:
        assert error in result, f"{error} not found in result"
        assert "Sysbench execution failed" in result[error]


@patch("shutil.which", return_value=None)
@patch.object(SysbenchTest, "install", return_value=False)
def test_sysbench_not_available(mock_install, mock_which, sysbench_test):
    config = {
        "file_total_size": "1G",
        "runtime": 60,
        "test_directory": "/tmp/diskest_test",
    }

    result = sysbench_test.run(config)

    assert "error" in result
    assert (
        "sysbench is not installed and automatic installation failed" in result["error"]
    )
    assert "install_instructions" in result
