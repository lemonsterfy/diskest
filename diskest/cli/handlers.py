"""
Command handlers for Diskest CLI
"""

import json
import time
from typing import Optional

from rich.console import Console
from rich.theme import Theme

from diskest.core.test_runner import TestRunner
from diskest.utils.logging import setup_logging
from diskest.utils.config import load_config, get_config_path
from diskest.utils.database import ResultDatabase
from diskest.core.result_processor import ReportGenerator

# Elegant and professional color theme
elegant_theme = Theme(
    {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red",
    }
)

console = Console(theme=elegant_theme)


def run_handler(config_path: str, verbose: bool):
    """Handle the 'run' command with elegant and minimalist output."""
    try:
        setup_logging(verbose)
        config = load_config(config_path)

        console.print("[bold info]Diskest[/bold info] Disk Benchmark", style="info")
        console.print("Initializing...", style="info")

        runner = TestRunner(config)
        start_time = time.time()
        results = runner.run_tests()
        end_time = time.time()

        elapsed_time = end_time - start_time
        console.print(
            f"Tests completed in {elapsed_time:.2f} seconds.", style="success"
        )

        db = ResultDatabase()
        saved_id = db.save_result(results)

        if saved_id:
            console.print(
                f"Results saved to database. Result ID: {saved_id}", style="success"
            )
        else:
            console.print(
                "Tests completed, but results could not be saved.", style="warning"
            )

    except Exception as e:
        console.print(f"An error occurred: {str(e)}", style="error")


def report_handler(format: str, output: Optional[str]):
    """Handle the 'report' command with minimalist output."""
    try:
        db = ResultDatabase()
        latest_result = db.get_latest_result()

        if not latest_result:
            raise ValueError("No test results found. Run 'diskest run' first.")

        generator = ReportGenerator(latest_result)

        console.print("Generating report...", style="info")
        if format == "cli":
            summary = generator.generate_cli_summary()
            for item in summary:
                console.print(item)
        elif format == "markdown":
            content = generator.generate_markdown_report()
            if output:
                with open(output, "w") as f:
                    f.write(content)
                console.print(f"Markdown report saved to: {output}", style="success")
            else:
                console.print(content)
        elif format in ["csv", "json", "pdf"]:
            if not output:
                raise ValueError(f"Output file path is required for {format} format.")
            getattr(generator, f"generate_{format}")(output)
            console.print(
                f"{format.upper()} report saved to: {output}", style="success"
            )

    except Exception as e:
        console.print(f"An error occurred: {str(e)}", style="error")


def config_handler(action: str):
    """Handle the 'config' command with minimalist output."""
    try:
        config_path = get_config_path()
        if action == "show":
            config = load_config(config_path)
            console.print("Current Configuration:", style="info")
            console.print_json(json.dumps(config, indent=2))
        elif action == "edit":
            console.print(
                "Configuration editing is not yet implemented.", style="warning"
            )
            console.print(
                "This feature will be available in a future update.", style="info"
            )
    except Exception as e:
        console.print(f"An error occurred: {str(e)}", style="error")
