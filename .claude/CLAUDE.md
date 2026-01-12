# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a Senzing Governor plugin that monitors PostgreSQL transaction ID (XID) age. When XID age exceeds a high watermark, it pauses processing threads until the age drops below a low watermark (achieved via PostgreSQL VACUUM).

## Build and Development Commands

This project uses `pyproject.toml` with setuptools and requires Python >= 3.10.

```bash
# Install dependencies (using uv, pip, or similar)
uv sync --group all           # All dependency groups
uv sync --group development   # Development dependencies only
uv sync --group lint          # Linting tools only
uv sync --group test          # Test dependencies only

# Run unit tests
python -m pytest src/senzing_governor_unit_test.py
python -m unittest src/senzing_governor_unit_test.py

# Run linters (configured in pyproject.toml)
black --check src/
isort --check src/
flake8 src/
pylint src/
mypy src/
bandit -r src/

# Build package
python -m build
```

## Code Architecture

The entire implementation is in `src/senzing_governor.py`:

- **`Governor` class**: The main class implementing the governor pattern
  - `__init__()`: Configures watermarks, intervals, and database connections from environment variables or parameters
  - `govern()`: Called by worker threads; checks XID age periodically and returns wait time (uses thread locking)
  - `close()`: Closes database connections
  - Supports Python context manager protocol (`with` statement)

- **Watermark behavior**: Uses a stepped wait-time function based on ratio between current XID and watermarks. When above high watermark, returns -1.0 to signal system trouble.

- **Database URL parsing**: Custom parsing handles complex PostgreSQL URLs with special characters; extracts from `SENZING_GOVERNOR_DATABASE_URLS`, `SENZING_DATABASE_URL`, or `SENZING_ENGINE_CONFIGURATION_JSON`.

## Key Environment Variables

- `SENZING_GOVERNOR_DATABASE_URLS`: PostgreSQL connection URLs (comma-separated for multiple DBs)
- `SENZING_GOVERNOR_POSTGRESQL_HIGH_WATERMARK`: Default 1,500,000,000
- `SENZING_GOVERNOR_POSTGRESQL_LOW_WATERMARK`: Default 1,200,000,000
- `SENZING_GOVERNOR_INTERVAL`: Check interval (default 100,000 records)
- `SENZING_GOVERNOR_LIST_SEPARATOR`: URL list separator (default comma)

## Testing

- `src/senzing_governor_unit_test.py`: Unit tests for `get_wait_time()` method
- `src/senzing_governor_tester.py`: Integration test with multi-threaded example
- `src/senzing_governor_tester_context_manager.py`: Context manager usage example

## Code Style

- Line length: 120 characters (black, flake8)
- Import sorting: isort with black profile
- Type checking: mypy with several error codes disabled (see pyproject.toml)
