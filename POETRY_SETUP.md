# Poetry Setup Guide for CrashLens Logger

This guide will help you set up the CrashLens Logger project using Poetry for dependency management.

## Prerequisites

Make sure you have Python 3.9+ and Poetry installed:

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -
# Or on Windows:
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

## Installation

1. **Clone/Navigate to the project directory:**
   ```bash
   cd "c:\Users\LawLight\OneDrive\Desktop\crashlens logger"
   ```

2. **Install dependencies with Poetry:**
   ```bash
   poetry install
   ```

3. **Install with development dependencies (recommended):**
   ```bash
   poetry install --extras dev
   ```

## Usage

### Option 1: Using Poetry shell (Recommended)

```bash
# Activate the virtual environment
poetry shell

# Now you can use the CLI directly
crashlens-logger --help
crashlens-logger log --model "gpt-4" --prompt "Hello!" --dev-mode
```

### Option 2: Using Poetry run

```bash
# Run commands without activating the shell
poetry run crashlens-logger --help
poetry run crashlens-logger log --model "gpt-4" --prompt "Hello!" --dev-mode
```

### Option 3: Direct Python execution

```bash
# Run the module directly
poetry run python -m crashlens_logger.logger --help
```

## Development Commands

```bash
# Run tests
poetry run pytest

# Format code
poetry run black crashlens_logger/
poetry run isort crashlens_logger/

# Type checking
poetry run mypy crashlens_logger/

# Lint code
poetry run flake8 crashlens_logger/

# Test the setup
poetry run python test_poetry_setup.py
```

## Building and Publishing

```bash
# Build the package
poetry build

# Publish to PyPI (when ready)
poetry publish
```

## Example Usage

```bash
# After installation, try these examples:

# Basic logging
poetry run crashlens-logger log \
  --model "gpt-4" \
  --prompt "What is machine learning?" \
  --response "ML is a subset of AI..." \
  --dev-mode

# Simulate retries
poetry run crashlens-logger log \
  --model "gpt-4" \
  --prompt "Complex query" \
  --simulate-retries 3 \
  --dev-mode

# Initialize config
poetry run crashlens-logger init-config

# Analyze logs
poetry run crashlens-logger analyze logs.jsonl
```

## Project Structure

```
crashlens-logger/
├── pyproject.toml           # Poetry configuration
├── crashlens_logger/        # Main package
│   ├── __init__.py
│   └── logger.py           # Core CLI implementation
├── test_poetry_setup.py    # Setup verification
├── README.md               # Documentation
└── sample_config.yaml      # Example configuration
```

## Troubleshooting

1. **Import errors**: Make sure you're running commands with `poetry run` or inside `poetry shell`
2. **Missing dependencies**: Run `poetry install` again
3. **Rich not available**: This is optional - install with `poetry install --extras dev`
4. **CLI not found**: Make sure the installation completed successfully

## Dependencies

- **Core**: `click`, `orjson`, `pyyaml`
- **Optional**: `rich` (for pretty output)
- **Dev**: `pytest`, `black`, `isort`, `flake8`, `mypy`
