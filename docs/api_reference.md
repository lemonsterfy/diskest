# Diskest API Reference

## Core Components

### TestRunner

```python
class TestRunner:
    def __init__(self, config: Dict[str, Any], progress_callback: Callable[[float], None] = None):
        ...

    def run_tests(self) -> Dict[str, Any]:
        ...
```

The `TestRunner` class is responsible for executing benchmark tests based on the provided configuration.

### ReportGenerator

```python
class ReportGenerator:
    def __init__(self, results: Dict[str, Any]):
        ...

    def generate_cli_summary(self) -> List[Any]:
        ...

    def generate_markdown_report(self) -> str:
        ...

    def generate_csv(self, output_path: str) -> None:
        ...

    def generate_json(self, output_path: str) -> None:
        ...

    def generate_pdf(self, output_path: str) -> None:
        ...
```

The `ReportGenerator` class processes test results and generates reports in various formats.

## Utility Functions

### Configuration

```python
def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    ...

def get_config_path() -> Path:
    ...
```

These functions handle loading and managing Diskest configurations.

### Logging

```python
def setup_logging(verbose: bool = False, log_file: str = None) -> None:
    ...

def get_log_file_path() -> Path:
    ...
```

These functions set up and configure logging for Diskest.

### Database

```python
class ResultDatabase:
    def __init__(self, db_path: str = "/var/lib/diskest/results.db"):
        ...

    def save_result(self, result: Dict) -> Optional[int]:
        ...

    def get_latest_result(self) -> Optional[Dict]:
        ...

    def get_all_results(self) -> List[Tuple[str, Dict]]:
        ...
```

The `ResultDatabase` class provides methods for storing and retrieving benchmark results.

## Test Classes

### BaseTest

```python
class BaseTest(ABC):
    @abstractmethod
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        ...
```

`BaseTest` is an abstract base class for all benchmark tests.

### FioTest

```python
class FioTest(BaseTest):
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        ...
```

`FioTest` implements the Flexible I/O Tester benchmark.

### SysbenchTest

```python
class SysbenchTest(BaseTest):
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        ...
```

`SysbenchTest` implements the Sysbench benchmark test.

For more detailed information on each component, please refer to the inline documentation in the source code.