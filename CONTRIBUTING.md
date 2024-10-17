# Contributing to Diskest

We welcome contributions to Diskest! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with a clear commit message.
4. Push your changes to your fork.
5. Submit a pull request to the main repository.

## Development Setup

1. Clone your fork of the repository.
2. Install the package in editable mode with development dependencies:
   ```
   pip install -e .[dev]
   ```

This will install all required dependencies for development, including testing tools.

## Coding Standards

- Follow PEP 8 style guide for Python code.
- Use type hints where possible.
- Write docstrings for all modules, classes, and functions.
- Ensure your code passes all existing tests and add new tests for new functionality.

## Running Tests

Before submitting a pull request, please ensure that all tests pass:

1. Run the full test suite:
   ```
   pytest
   ```

2. If you've added new functionality, please add appropriate tests in the `tests/` directory.

3. Ensure your tests cover both success and failure scenarios.

4. Use fixtures defined in `tests/conftest.py` for common test setups.

5. When adding new tests, follow the existing naming conventions:
   - Test files should be named `test_<module_name>.py`
   - Test functions should be named `test_<function_name>`

6. Use mock objects and pytest's monkeypatch where appropriate to isolate tests from external dependencies.

7. To run tests with coverage report:
   ```
   pytest --cov=diskest --cov-report=term-missing
   ```

## Code Formatting

We use Black for code formatting. Please format your code before submitting a pull request:

```
black .
```

We also use Flake8 for linting. Ensure your code passes Flake8 checks:

```
flake8 .
```

## Submitting Changes

1. Ensure your code adheres to the coding standards.
2. Run the test suite and ensure all tests pass.
3. Update the documentation if necessary.
4. Submit a pull request with a clear description of your changes.

## Reporting Issues

- Use the issue tracker to report bugs.
- Describe the bug and include steps to reproduce if possible.
- Include information about your environment (OS, Python version, etc.).

Thank you for contributing to Diskest!