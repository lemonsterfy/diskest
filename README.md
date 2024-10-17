# Diskest: Advanced Disk Benchmark Tool

Diskest is an advanced disk benchmark tool designed to provide comprehensive disk performance assessment for Linux systems.

## Features

- Supports multiple benchmark tests including FIO and Sysbench
- Detailed hardware detection and system information collection
- Flexible configuration options
- Multiple report formats (CLI, Markdown, CSV, JSON, PDF)
- Results database for storing and comparing benchmark results

## Installation

To install Diskest, you can use pip:

```bash
pip install diskest
```

For development installation with additional tools:

```bash
pip install diskest[dev]
```

Or clone the repository and install:

```bash
git clone https://github.com/lemonsterfy/diskest.git
cd diskest
pip install -e .[dev]
```

This will install Diskest along with all development dependencies.

## Usage

Diskest provides a command-line interface with the following main commands:

1. Run benchmark tests:
   ```
   diskest run [--config CONFIG_FILE]
   ```

2. Generate reports:
   ```
   diskest report [--format {cli,markdown,csv,json,pdf}] [--output OUTPUT_FILE]
   ```

3. Manage configuration:
   ```
   diskest config {show,edit}
   ```

For more detailed usage instructions, use the `--help` option with any command.

## Running Diskest in a Virtual Environment

If you're using Diskest in a virtual environment and need to run it with elevated privileges, use the following command:

```bash
sudo /path/to/your/venv/bin/diskest run [--config CONFIG_FILE]
```

For example, if your virtual environment is named `diskest_env` and is located in your home directory:

```bash
sudo /home/yourusername/diskest_env/bin/diskest run [--config CONFIG_FILE]
```

Replace `/home/yourusername` with your actual home directory path.

**Note:** Running Diskest with sudo privileges is necessary for certain disk operations. Always exercise caution when running commands with elevated privileges.

## Running Tests

To run the tests for Diskest, follow these steps:

1. Ensure you have installed the development dependencies:
   ```
   pip install -e .[dev]
   ```

2. Run the tests using pytest:
   ```
   pytest
   ```

This will run all the tests in the `tests/` directory. For more detailed output, you can use the `-v` flag:
   ```
   pytest -v
   ```

Our test suite covers the following areas:
- Configuration management
- Hardware detection
- System information collection
- Result processing
- Test runners (FIO and Sysbench)
- CLI functionality
- Database operations
- Logging

To run tests for a specific module, use:
   ```
   pytest tests/test_<module_name>.py
   ```

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## License

Diskest is released under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Support

If you encounter any issues or have questions, please file an issue on the [GitHub issue tracker](https://github.com/lemonsterfy/diskest/issues).