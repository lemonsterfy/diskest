"""
CLI commands for Diskest
"""

import click
from rich.console import Console
from .handlers import run_handler, report_handler, config_handler
from diskest import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="Diskest")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose):
    """Diskest - Advanced Disk Benchmark Tool"""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.option(
    "--config", type=click.Path(exists=True), help="Path to configuration file"
)
@click.pass_context
def run(ctx, config):
    """Run disk performance tests."""
    try:
        run_handler(config, ctx.obj["verbose"])
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        ctx.exit(1)


@cli.command()
@click.option(
    "--format",
    type=click.Choice(["cli", "markdown", "csv", "json", "pdf"]),
    default="cli",
    help="Output format",
)
@click.option("--output", type=click.Path(), help="Output file path")
@click.pass_context
def report(ctx, format, output):
    """Generate a report of test results."""
    try:
        report_handler(format, output)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        ctx.exit(1)


@cli.command()
@click.argument("action", type=click.Choice(["show", "edit"]))
@click.pass_context
def config(ctx, action):
    """Manage Diskest configuration."""
    try:
        config_handler(action)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        ctx.exit(1)
