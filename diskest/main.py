#!/usr/bin/env python3
"""
Main entry point for the Diskest application.
"""
import sys
import logging
from .cli.commands import cli
from .utils.logging import setup_logging


def main():
    try:
        setup_logging()
        cli()
    except Exception as e:
        logging.critical(f"An unhandled exception occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
