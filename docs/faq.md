# Diskest FAQ

## General Questions

### Q: What is Diskest?
A: Diskest is an advanced disk benchmark tool designed for Linux systems. It provides comprehensive disk performance assessment using multiple benchmark tests.

### Q: Which operating systems are supported?
A: Diskest is primarily designed for Linux systems. It may work on other UNIX-like systems, but this is not officially supported.

## Installation and Setup

### Q: How do I install Diskest?
A: You can install Diskest using pip:
```
pip install diskest
```
Alternatively, you can clone the repository and install it manually.

### Q: What are the system requirements?
A: Diskest requires Python 3.7 or later. Some benchmark tests (like FIO and Sysbench) need to be installed separately.

### Q: Can I install Diskest in a virtual environment?
A: Yes, it's recommended to install Diskest in a virtual environment. Use the following commands:
```
python -m venv diskest_env
source diskest_env/bin/activate
pip install diskest
```

## Usage

### Q: How do I run a benchmark test?
A: You can run a benchmark test using the command:
```
diskest run
```
You can specify a custom configuration file using the `--config` option.

### Q: How do I run Diskest in a virtual environment?
A: If you're using Diskest in a virtual environment and need to run it with elevated privileges, use the following command:
```
sudo /path/to/your/venv/bin/diskest run
```
Replace `/path/to/your/venv` with the actual path to your virtual environment.

### Q: Why do I need to run Diskest with sudo?
A: Diskest requires root privileges to perform certain disk operations and collect detailed system information. Always be cautious when running commands with elevated privileges.

### Q: Can I customize the benchmark parameters?
A: Yes, you can create a custom YAML configuration file to adjust various parameters like test duration, file size, etc.

### Q: How do I interpret the results?
A: Diskest provides metrics such as IOPS, bandwidth, and latency. Higher IOPS and bandwidth generally indicate better performance, while lower latency is desirable.

## Troubleshooting

### Q: The benchmark fails to run. What should I do?
A: Ensure you have the necessary permissions to write to the test directory. Also, check if FIO and Sysbench are properly installed on your system.

### Q: How can I get more detailed logs for debugging?
A: You can enable verbose logging by using the `-v` or `--verbose` option when running Diskest.

### Q: I'm getting unusually low performance results. What could be the cause?
A: Various factors can affect disk performance, including other running processes, disk fragmentation, or hardware issues. Try running the benchmark when the system is idle and ensure your disks are in good health.

### Q: Diskest can't find the command when I use sudo. What should I do?
A: When using sudo with a virtual environment, you need to specify the full path to the Diskest executable. Use:
```
sudo /path/to/your/venv/bin/diskest run
```
Replace `/path/to/your/venv` with the actual path to your virtual environment.

## Security

### Q: Is it safe to run Diskest with sudo?
A: While Diskest is designed to be safe, running any program with elevated privileges carries risks. Only run Diskest from trusted sources and review the configuration before running.

### Q: Can Diskest damage my disks?
A: Diskest is designed to be non-destructive. However, intensive I/O operations can potentially impact the lifespan of SSDs if run excessively. Use Diskest responsibly and avoid unnecessary repeated runs.

## Contributing

### Q: How can I contribute to Diskest?
A: We welcome contributions! Please refer to our [Contributing Guide](../CONTRIBUTING.md) for details on how to submit patches, report bugs, or suggest new features.

If you have any other questions not covered here, please file an issue on our GitHub repository.