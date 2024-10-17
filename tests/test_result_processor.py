import pytest
from diskest.core.result_processor import ReportGenerator
from rich.panel import Panel


@pytest.fixture
def report_generator(sample_results):
    return ReportGenerator(sample_results)


def test_generate_cli_summary(report_generator):
    summary = report_generator.generate_cli_summary()
    assert isinstance(summary, list)

    print("\nGenerated CLI Summary:")
    for item in summary:
        print(str(item))
        if isinstance(item, Panel):
            print(f"Panel title: {item.title}")
            print(f"Panel content: {item.renderable}")

    print("\nReport Generator Results:")
    print(f"Keys in results: {report_generator.results.keys()}")
    if "system_info" in report_generator.results:
        print(f"Keys in system_info: {report_generator.results['system_info'].keys()}")
    if "tests" in report_generator.results:
        print(f"Keys in tests: {report_generator.results['tests'].keys()}")

    assert len(summary) > 0, "CLI summary is empty"

    system_info_found = any(
        isinstance(item, Panel) and item.title and "System" in item.title
        for item in summary
    )
    test_results_found = any(
        isinstance(item, Panel) and item.title and "Test" in item.title
        for item in summary
    )

    assert system_info_found, "System Information panel not found in summary"
    assert test_results_found, "Test Results panel not found in summary"


def test_generate_markdown_report(report_generator):
    report = report_generator.generate_markdown_report()
    assert isinstance(report, str)
    assert "## System Information" in report
    assert "## FIO Test Results" in report or "## Test Results" in report


def test_process_test_results(report_generator, sample_results):
    processed = report_generator._process_test_results(
        "fio", sample_results["tests"]["fio"]
    )
    assert len(processed) == 1
    assert processed[0][0] == "Sequential Read"
    assert processed[0][1] == "1000.00"
    assert processed[0][2] == "500.00 MB/s"


def test_sample_results_content(sample_results):
    assert "system_info" in sample_results, "sample_results missing system_info"
    assert "tests" in sample_results, "sample_results missing tests"
    assert "fio" in sample_results["tests"], "sample_results missing FIO test results"

    print("\nSample Results Content:")
    print(f"Keys in sample_results: {sample_results.keys()}")
    print(f"Keys in system_info: {sample_results['system_info'].keys()}")
    print(f"Keys in tests: {sample_results['tests'].keys()}")
