"""
Result processing module for Diskest.

This module handles the generation of reports in various formats
based on the test results obtained from disk benchmarks.
"""

import json
import csv
import logging
from typing import Dict, Any, List, Tuple

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.box import SIMPLE

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table as PDFTable, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates reports in various formats based on test results."""

    def __init__(self, results: Dict[str, Any]):
        """
        Initialize the ReportGenerator.

        Args:
            results (Dict[str, Any]): Test results to be processed.
        """
        self.results = results
        self.console = Console()
        logger.debug(
            f"Initializing ReportGenerator with results keys: " f"{results.keys()}"
        )

    def generate_cli_summary(self) -> List[Any]:
        """
        Generate a CLI summary of the test results.

        Returns:
            List[Any]: List of Rich components for CLI display.
        """
        output = []
        output.append(Text("Diskest Test Results Summary", style="bold"))
        output.append("")
        output.append(self._generate_system_info_panel())
        output.append("")

        for test_name, test_results in self.results["tests"].items():
            logger.info(f"Processing results for test: {test_name}")
            panel = self._generate_test_results_panel(test_name, test_results)
            output.append(panel)
            output.append("")

        output.append(Text("End of report.", style="italic dim"))
        return output

    def generate_markdown_report(self) -> str:
        """
        Generate a Markdown report of the test results.

        Returns:
            str: Markdown formatted report.
        """
        report = "# Diskest Test Results\n\n"
        report += self._generate_markdown_system_info()
        report += self._generate_markdown_test_results()
        return report

    def generate_csv(self, output_path: str) -> None:
        """
        Generate a CSV report of the test results.

        Args:
            output_path (str): Path to save the CSV file.
        """
        try:
            with open(output_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self._get_csv_header())
                for test_name, test_results in self.results["tests"].items():
                    writer.writerows(
                        self._process_test_results(test_name, test_results, True)
                    )
            logger.info(f"CSV report generated: {output_path}")
        except IOError as e:
            logger.error(f"Error generating CSV report: {str(e)}")
            raise

    def generate_json(self, output_path: str) -> None:
        """
        Generate a JSON report of the test results.

        Args:
            output_path (str): Path to save the JSON file.
        """
        try:
            json_results = {
                "system_info": self.results["system_info"],
                "hardware_info": self.results["hardware_info"],
                "tests": {
                    test_name: self._process_test_results_to_dict(
                        test_name, test_results
                    )
                    for test_name, test_results in self.results["tests"].items()
                },
            }
            with open(output_path, "w") as jsonfile:
                json.dump(json_results, jsonfile, indent=2)
            logger.info(f"JSON report generated: {output_path}")
        except IOError as e:
            logger.error(f"Error generating JSON report: {str(e)}")
            raise

    def generate_pdf(self, output_path: str) -> None:
        """
        Generate a PDF report of the test results.

        Args:
            output_path (str): Path to save the PDF file.
        """

        try:
            doc = SimpleDocTemplate(output_path, pagesize=landscape(letter))
            styles = getSampleStyleSheet()
            elements = [
                Paragraph("Diskest Test Results Summary", styles["Title"]),
                Paragraph("System Information", styles["Heading2"]),
                PDFTable(
                    self._get_system_info(),
                    style=[
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ],
                ),
            ]

            for test_name, test_results in self.results["tests"].items():
                elements.extend(
                    [
                        Paragraph(
                            f"{test_name.upper()} Test Results", styles["Heading2"]
                        ),
                        PDFTable(
                            [self._get_csv_header()]
                            + self._process_test_results(test_name, test_results),
                            style=[
                                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                            ],
                        ),
                    ]
                )

            doc.build(elements)
            logger.info(f"PDF report generated: {output_path}")
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise

    def _get_operations(self, test_name: str) -> List[Tuple[str, str, List[str]]]:
        """
        Get the list of operations for a given test.

        Args:
            test_name (str): Name of the test.

        Returns:
            List[Tuple[str, str, List[str]]]: List of operations for the test.
        """
        operations = {
            "fio": [
                ("sequential_read", "Sequential Read", ["read"]),
                ("sequential_write", "Sequential Write", ["write"]),
                ("random_read", "Random Read", ["read"]),
                ("random_write", "Random Write", ["write"]),
                ("mixed_rw", "Mixed R/W", ["read", "write"]),
                ("latency", "Latency", ["read"]),
            ],
            "sysbench": [
                ("sequential_read", "Sequential Read", ["read"]),
                ("sequential_write", "Sequential Write", ["write"]),
                ("random_read", "Random Read", ["read"]),
                ("random_write", "Random Write", ["write"]),
                ("random_rw", "Random R/W", ["read", "write"]),
                ("fsync", "fsync", ["read", "write"]),
                ("latency", "Latency", ["read", "write"]),
            ],
        }
        return operations.get(test_name.lower(), [])

    def _get_row_name(self, op_name: str, rw_types: List[str], rw: str) -> str:
        """
        Get the row name for a given operation.

        Args:
            op_name (str): Operation name.
            rw_types (List[str]): Read/write types.
            rw (str): Current read/write type.

        Returns:
            str: Row name.
        """
        return op_name if len(rw_types) == 1 else f"{op_name} {rw.capitalize()}"

    def _get_system_info(self) -> List[List[str]]:
        """
        Get system information as a list of key-value pairs.

        Returns:
            List[List[str]]: System information.
        """
        sys_info = self.results["system_info"]
        hw_info = self.results["hardware_info"]
        return [
            ["OS", sys_info["os"]["distro"]],
            [
                "CPU",
                f"{sys_info['cpu']['physical_cores']} physical cores, "
                f"{sys_info['cpu']['total_cores']} total cores",
            ],
            ["Memory", f"{sys_info['memory']['total'] / (1024**3):.2f} GB total"],
            ["RAID", "Detected" if hw_info["raid"]["detected"] else "Not detected"],
        ]

    def _get_csv_header(self) -> List[str]:
        """
        Get the CSV header.

        Returns:
            List[str]: CSV header.
        """
        return [
            "Test",
            "Operation",
            "IOPS",
            "Bandwidth (MB/s)",
            "Avg Latency (ms)",
            "Min Latency (ms)",
            "Max Latency (ms)",
            "95% Latency (ms)",
        ]

    def _process_test_results(
        self,
        test_name: str,
        test_results: Dict[str, Any],
        include_test_name: bool = False,
    ) -> List[List[str]]:
        """
        Process test results into a list of rows.

        Args:
            test_name (str): Name of the test.
            test_results (Dict[str, Any]): Test results.
            include_test_name (bool): Whether to include the test name in each row.

        Returns:
            List[List[str]]: Processed test results.
        """
        data = []
        for op, op_name, rw_types in self._get_operations(test_name):
            for rw in rw_types:
                key = f"{op}_{rw}"
                row_name = self._get_row_name(op_name, rw_types, rw)
                if test_name.lower() == "fio":
                    if key in test_results and test_results[key]["iops"] > 0:
                        row = self._get_fio_row(row_name, test_results[key])
                        if include_test_name:
                            row.insert(0, test_name)
                        data.append(row)
                elif test_name.lower() == "sysbench":
                    iops = test_results.get(f"{op}_{rw}_iops", 0)
                    bw = test_results.get(f"{op}_{rw}_bw", 0)
                    if iops > 0 or bw > 0:
                        row = self._get_sysbench_row(
                            row_name, test_results, op, iops, bw
                        )
                        if include_test_name:
                            row.insert(0, test_name)
                        data.append(row)
        return data

    def _process_test_results_to_dict(
        self, test_name: str, test_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process test results into a dictionary.

        Args:
            test_name (str): Name of the test.
            test_results (Dict[str, Any]): Test results.

        Returns:
            Dict[str, Any]: Processed test results as a dictionary.
        """
        return {
            row[1]: {
                "iops": float(row[2]),
                "bandwidth": float(row[3].split()[0]),
                "avg_latency": float(row[4].split()[0]),
                "min_latency": float(row[5].split()[0]),
                "max_latency": float(row[6].split()[0]),
                "95th_percentile_latency": float(row[7].split()[0]),
            }
            for row in self._process_test_results(test_name, test_results, True)
        }

    def _get_fio_row(self, row_name: str, result: Dict[str, Any]) -> List[str]:
        """
        Get a row of FIO test results.

        Args:
            row_name (str): Name of the row.
            result (Dict[str, Any]): FIO test result.

        Returns:
            List[str]: Formatted row of FIO test results.
        """
        return [
            row_name,
            f"{result['iops']:.2f}",
            f"{result['bw']:.2f} MB/s",
            f"{result['lat_avg']:.3f} ms",
            f"{result['lat_min']:.3f} ms",
            f"{result['lat_max']:.3f} ms",
            f"{result['lat_p95']:.3f} ms",
        ]

    def _get_sysbench_row(
        self, row_name: str, results: Dict[str, Any], op: str, iops: float, bw: float
    ) -> List[str]:
        """
        Get a row of Sysbench test results.

        Args:
            row_name (str): Name of the row.
            results (Dict[str, Any]): Sysbench test results.
            op (str): Operation name.
            iops (float): IOPS value.
            bw (float): Bandwidth value.

        Returns:
            List[str]: Formatted row of Sysbench test results.
        """
        return [
            row_name,
            f"{iops:.2f}",
            f"{bw:.2f} MB/s",
            f"{results.get(f'{op}_latency_avg', 0):.3f} ms",
            f"{results.get(f'{op}_latency_min', 0):.3f} ms",
            f"{results.get(f'{op}_latency_max', 0):.3f} ms",
            f"{results.get(f'{op}_latency_95th', 0):.3f} ms",
        ]

    def _generate_system_info_panel(self) -> Panel:
        """
        Generate a Rich Panel with system information.

        Returns:
            Panel: Rich Panel object containing system information.
        """
        sys_info = Table.grid(padding=(0, 2))
        sys_info.add_column(style="dim", width=12)
        sys_info.add_column()
        for row in self._get_system_info():
            sys_info.add_row(*row)

        return Panel(
            sys_info,
            title="System Information",
            title_align="left",
            border_style="dim",
            box=SIMPLE,
            padding=(1, 1),
        )

    def _generate_test_results_panel(
        self, test_name: str, test_results: Dict[str, Any]
    ) -> Panel:
        """
        Generate a Rich Panel with test results.

        Args:
            test_name (str): Name of the test.
            test_results (Dict[str, Any]): Results of the test.

        Returns:
            Panel: Rich Panel object containing test results.
        """
        table = Table(
            show_header=True, header_style="bold", box=SIMPLE, border_style="dim"
        )
        table.add_column("Operation", style="dim", width=20)
        table.add_column("IOPS", justify="right", width=12)
        table.add_column("Bandwidth", justify="right", width=12)
        table.add_column("Avg Latency", justify="right", width=12)
        table.add_column("Min Latency", justify="right", width=12)
        table.add_column("Max Latency", justify="right", width=12)
        table.add_column("95% Latency", justify="right", width=12)

        data = self._process_test_results(test_name, test_results)
        for row in data:
            table.add_row(*row)

        if not data:
            table.add_row("No results", "", "", "", "", "", "")

        return Panel(
            table,
            title=f"{test_name.upper()} Test Results",
            title_align="left",
            border_style="dim",
            box=SIMPLE,
            padding=(1, 1),
        )

    def _generate_markdown_system_info(self) -> str:
        """
        Generate Markdown formatted system information.

        Returns:
            str: Markdown formatted system information.
        """
        info = self._get_system_info()
        return (
            "## System Information\n"
            + "\n".join(f"- {k}: {v}" for k, v in info)
            + "\n\n"
        )

    def _generate_markdown_test_results(self) -> str:
        """
        Generate Markdown formatted test results.

        Returns:
            str: Markdown formatted test results.
        """
        report = ""
        for test_name, test_results in self.results["tests"].items():
            report += f"## {test_name.upper()} Test Results\n"
            report += (
                "| Operation | IOPS | Bandwidth | Avg Latency | "
                "Min Latency | Max Latency | 95% Latency |\n"
            )
            report += (
                "|-----------|------|-----------|-------------|"
                "-------------|-------------|-------------|\n"
            )
            for row in self._process_test_results(test_name, test_results):
                report += f"| {' | '.join(row)} |\n"
            report += "\n"
        return report
