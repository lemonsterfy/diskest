import pytest
from click.testing import CliRunner
from diskest.cli.commands import cli


@pytest.fixture
def runner():
    """Provide a CliRunner instance."""
    return CliRunner()


@pytest.fixture
def mock_test_runner(mocker):
    """Mock TestRunner to avoid actual disk operations."""
    mock = mocker.patch("diskest.cli.handlers.TestRunner")
    mock.return_value.run_tests.return_value = {"test": "result"}
    return mock


@pytest.fixture
def mock_result_database(mocker):
    """Mock ResultDatabase to avoid database operations."""
    mock = mocker.patch("diskest.cli.handlers.ResultDatabase")
    mock.return_value.save_result.return_value = 1
    mock.return_value.get_latest_result.return_value = {"test": "result"}
    return mock


def test_run_command(runner, mock_test_runner, mock_result_database):
    """Test the 'run' command of the CLI."""
    result = runner.invoke(cli, ["run"])
    assert result.exit_code == 0
    assert "Diskest Disk Benchmark" in result.output
    assert "Tests completed" in result.output
    mock_test_runner.assert_called_once()
    mock_result_database.return_value.save_result.assert_called_once()


def test_report_command(runner, mock_result_database):
    """Test the 'report' command of the CLI."""
    result = runner.invoke(cli, ["report"])
    assert result.exit_code == 0
    assert "Generating report" in result.output
    mock_result_database.return_value.get_latest_result.assert_called_once()


def test_config_command(runner, mocker):
    """Test the 'config' command of the CLI."""
    mock_load_config = mocker.patch("diskest.cli.handlers.load_config")
    mock_load_config.return_value = {"test": "config"}

    result = runner.invoke(cli, ["config", "show"])
    assert result.exit_code == 0
    assert "Current Configuration" in result.output
    mock_load_config.assert_called_once()
