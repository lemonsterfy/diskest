# Diskest User Guide

## Introduction

Diskest is an advanced disk benchmark tool designed for Linux systems. This guide will help you get started with Diskest and explain its features in detail.

## Installation

To install Diskest, you can use pip:

```bash
pip install diskest
```

## Basic Usage

### Running Benchmark Tests

To run benchmark tests, use the following command:

```bash
diskest run [--config CONFIG_FILE]
```

If you don't specify a config file, Diskest will use the default configuration.

### Running Diskest in a Virtual Environment

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

### Generating Reports

To generate a report of your benchmark results, use:

```bash
diskest report [--format {cli,markdown,csv,json,pdf}] [--output OUTPUT_FILE]
```

### Managing Configuration

To view or edit the configuration:

```bash
diskest config {show,edit}
```

## Advanced Usage

### Custom Configurations

You can create a custom YAML configuration file to tailor Diskest to your needs. Here's an example:

```yaml
global:
  test_directory: "/path/to/test/directory"
  verbose: true

fio:
  size: "2G"
  runtime: "120s"

sysbench:
  file_total_size: "4G"
  runtime: 300
```

### Interpreting Results

Diskest provides comprehensive results including:
- IOPS (Input/Output Operations Per Second)
- Bandwidth
- Latency (average, minimum, maximum, and 95th percentile)

Understanding these metrics will help you assess your disk performance effectively.

## Troubleshooting

If you encounter any issues, check the following:
1. Ensure you have the necessary permissions to run disk operations.
2. Verify that the test directory specified in the configuration exists and is writable.
3. Check system resources to ensure they're not constrained during testing.
4. When running in a virtual environment with sudo, make sure you're using the correct path to the diskest executable.

For more help, consult the FAQ or file an issue on our GitHub repository.

## Security Considerations

Diskest requires elevated privileges for certain operations. Always be cautious when running commands with sudo:
1. Only run Diskest from trusted sources.
2. Review the configuration and ensure it's not performing unwanted operations.
3. Consider running Diskest in a controlled environment if testing on production systems.

## Best Practices

1. Always use the latest version of Diskest for the most accurate results and latest features.
2. Run benchmarks multiple times and average the results for more reliable data.
3. Minimize system activity during benchmarking for consistent results.
4. Use custom configurations to match your specific use case or hardware setup.
5. Regularly compare benchmark results to track performance changes over time.

Remember, disk performance can vary based on many factors. Use Diskest as part of a comprehensive performance evaluation strategy.