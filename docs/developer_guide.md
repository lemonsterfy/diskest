# Diskest Developer Documentation

## Project Structure

Diskest follows a modular structure:

```
diskest/
├── cli/
│   ├── commands.py
│   ├── handlers.py
│   └── __init__.py
├── core/
│   ├── hardware_detection.py
│   ├── result_processor.py
│   ├── system_info.py
│   └── test_runner.py
├── tests/
│   ├── base_test.py
│   ├── fio_test.py
│   └── sysbench_test.py
└── utils/
    ├── config.py
    ├── database.py
    └── logging.py
```

## Key Components

1. **CLI**: Handles command-line interface interactions.
2. **Core**: Contains the main logic for hardware detection, running tests, and processing results.
3. **Tests**: Implements specific benchmark tests (FIO and Sysbench).
4. **Utils**: Provides utility functions for configuration, logging, and database operations.

## Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/lemonsterfy/diskest.git
   ```
2. Install development dependencies:
   ```
   cd diskest
   pip install -e .[dev]
   ```

## Adding New Tests

To add a new benchmark test:

1. Create a new file in the `tests/` directory (e.g., `new_test.py`).
2. Implement a new class that inherits from `BaseTest`.
3. Override the `run()` method to implement the test logic.
4. Add the new test to `test_runner.py`.

## Running Tests

We use pytest for testing. Run tests with:

```
pytest
```

To run tests with coverage report:

```
pytest --cov=diskest --cov-report=term-missing
```

## Code Style

We follow PEP 8 for code style. Use `black` for code formatting:

```
black .
```

Use `flake8` for linting:

```
flake8 .
```

## Documentation

Use Google-style docstrings for all modules, classes, and functions.

## Submitting Changes

1. Create a new branch for your feature or bug fix.
2. Make your changes and commit them.
3. Push your branch and submit a pull request.
4. Ensure all tests pass and the code adheres to the style guide.

For more information, see the [Contributing Guide](../CONTRIBUTING.md).