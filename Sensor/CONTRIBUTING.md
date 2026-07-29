# Contributing to ADR Sensor

Thank you for your interest in contributing to ADR Sensor! This guide will help you get started.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ADR.git
   cd ADR/Sensor
   ```
3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```
4. Run tests to verify:
   ```bash
   pytest tests/ -v
   ```

## Development Workflow

1. Create a branch for your change:
   ```bash
   git checkout -b feature/my-new-parser
   ```
2. Make your changes
3. Run tests and linting:
   ```bash
   pytest tests/ -v
   ruff check adr_sensor/
   ruff format adr_sensor/
   ```
4. Commit and push
5. Open a Pull Request

## Adding a New Parser

This is the most common contribution. To add support for a new AI agent:

### Step 1: Create the Parser

Create `adr_sensor/parsers/my_agent_parser.py`:

```python
from pathlib import Path
from typing import List

from ..parsers.base_parser import BaseParser
from ..schemas.agent_event_schema import AgentEvent, ChatMessage, ToolUsage

class MyAgentParser(BaseParser):
    """Parser for MyAgent logs."""

    def __init__(self):
        # Set the path where your agent stores its logs
        self.base_path = Path.home() / ".my-agent/logs"

    def parse_all(self) -> List[AgentEvent]:
        """Parse all available MyAgent logs."""
        entries = []

        if not self.base_path.exists():
            print(f"[MY_AGENT] No logs found at {self.base_path}")
            return entries

        # Your parsing logic here
        # Convert logs into AgentEvent objects

        return entries
```

### Step 2: Register in Observer

Add your parser to `adr_sensor/observer.py`:

```python
from .parsers.my_agent_parser import MyAgentParser

# In __init__:
self.my_agent_parser = MyAgentParser()

# In ingest_all:
if source_filter in ["all", "my_agent"]:
    print("Ingesting MyAgent logs...")
    try:
        entries = self.my_agent_parser.parse_all()
        filtered = [e for e in entries if e.has_meaningful_content()]
        all_entries.extend(filtered)
    except Exception as e:
        print(f"Error ingesting MyAgent logs: {e}")
```

### Step 3: Add CLI Source

Update `adr_sensor/cli.py` to add the new source choice.

### Step 4: Write Tests

Create `tests/test_my_agent_parser.py` with test cases covering:
- Parsing valid log files
- Handling missing directories
- Handling malformed data
- Edge cases

## Code Style

- Follow PEP 8
- Use type hints
- Use `ruff` for formatting and linting
- Keep parsers self-contained (each parser should handle its own errors)

## Testing Guidelines

- All new code must have tests
- Tests should not depend on real log files existing on the machine
- Use `tmp_path` fixture for file-based tests
- Use mocks for external dependencies

## Reporting Issues

When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce
- Error messages or unexpected output

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
