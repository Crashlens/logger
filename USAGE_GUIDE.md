# CrashLens Logger - Usage Guide

## Installation & Setup

### Option 1: Using Poetry (Recommended)
```bash
# Navigate to project directory
cd "c:\Users\LawLight\OneDrive\Desktop\crashlens logger"

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Now you can use the CLI directly
crashlens-logger --help
```

### Option 2: Using pip
```bash
# Navigate to project directory
cd "c:\Users\LawLight\OneDrive\Desktop\crashlens logger"

# Install dependencies
pip install -r requirements.txt

# Run the module directly
python -m crashlens_logger.logger --help
```

## Available Commands

### 1. Basic Logging
```bash
# Basic log entry
crashlens-logger log --model "gpt-4" --prompt "What is AI?" --response "AI is artificial intelligence"

# With custom output file
crashlens-logger log --model "gpt-4" --prompt "Hello" --response "Hi there" --output "my_logs.jsonl"

# With development mode (verbose output)
crashlens-logger log --model "gpt-4" --prompt "Test prompt" --dev-mode
```

### 2. Retry Simulation
```bash
# Simulate 3 retry attempts before success
crashlens-logger log --model "gpt-4" --prompt "Complex query" --simulate-retries 3 --dev-mode

# With custom response
crashlens-logger log --model "gpt-4" --prompt "Retry test" --response "Final success" --simulate-retries 2
```

### 3. Fallback Simulation
```bash
# Simulate fallback from primary to secondary model
crashlens-logger log --model "gpt-4" --prompt "Fallback test" --simulate-fallback --dev-mode

# With custom response
crashlens-logger log --model "claude-3-opus" --prompt "Test fallback" --response "Fallback response" --simulate-fallback
```

### 4. Configuration Management
```bash
# Create sample configuration file
crashlens-logger init-config

# Create config with custom name
crashlens-logger init-config --config "my_pricing.yaml"

# Use custom config for logging
crashlens-logger log --model "custom-model" --prompt "Test" --config "my_pricing.yaml"
```

### 5. Log Analysis
```bash
# Analyze all logs in file
crashlens-logger analyze logs.jsonl

# Filter by model
crashlens-logger analyze logs.jsonl --model "gpt-4"

# Filter by trace ID
crashlens-logger analyze logs.jsonl --trace-id "123e4567-e89b-12d3-a456-426614174000"
```

### 6. Advanced Options
```bash
# Custom trace ID
crashlens-logger log --model "gpt-4" --prompt "Test" --trace-id "123e4567-e89b-12d3-a456-426614174000"

# Multiple options combined
crashlens-logger log \
  --model "claude-3-sonnet" \
  --prompt "Complex analysis task" \
  --response "Detailed analysis result" \
  --output "analysis_logs.jsonl" \
  --config "custom_pricing.yaml" \
  --dev-mode
```

## Quick Start Examples

### Example 1: Basic Usage
```bash
crashlens-logger log --model "gpt-4" --prompt "What is the weather like?" --response "I cannot access real-time weather data" --dev-mode
```

### Example 2: Cost Tracking
```bash
# Create custom pricing config
crashlens-logger init-config --config "pricing.yaml"

# Log with cost tracking
crashlens-logger log --model "gpt-4" --prompt "Expensive query with lots of tokens here" --config "pricing.yaml" --dev-mode
```

### Example 3: Reliability Testing
```bash
# Test retry patterns
crashlens-logger log --model "gpt-4" --prompt "Unreliable request" --simulate-retries 5 --dev-mode

# Test fallback patterns  
crashlens-logger log --model "gpt-4" --prompt "Primary model fails" --simulate-fallback --dev-mode
```

### Example 4: Batch Analysis
```bash
# Generate some test logs
crashlens-logger log --model "gpt-4" --prompt "Query 1" --response "Response 1"
crashlens-logger log --model "gpt-3.5-turbo" --prompt "Query 2" --response "Response 2"
crashlens-logger log --model "gpt-4" --prompt "Query 3" --response "Response 3"

# Analyze the logs
crashlens-logger analyze logs.jsonl
```

### Example 5: Python Integration
```python
from crashlens_logger import CrashLensLogger

logger = CrashLensLogger()

logger.log_event(
    traceId="trace_3921",
    type="generation",
    startTime="2024-06-01T10:00:00Z",
    endTime="2024-06-01T10:00:01Z",
    level="info",
    input={"model": "gpt-4o", "prompt": "What is 2+2?"},
    usage={"prompt_tokens": 5, "completion_tokens": 5},
    cost=0.000162,
    metadata={"fallback_attempted": False, "route": "/api/chat/completions", "team": "engineering"},
    name="simple-retry"
)
```

## Command Options Reference

### `log` command:
- `--model` (required): LLM model name
- `--prompt` (required): Input prompt text  
- `--response`: Model response text (optional)
- `--output`: Output file path (default: logs.jsonl)
- `--simulate-retries`: Number of retries to simulate
- `--simulate-fallback`: Simulate model fallback
- `--trace-id`: Custom trace ID (UUID format)
- `--dev-mode`: Enable verbose development output
- `--config`: Path to YAML pricing config file

### `init-config` command:
- `--config`: Path for config file (default: crashlens_config.yaml)

### `analyze` command:
- `log_file` (required): Path to JSONL log file
- `--trace-id`: Filter by specific trace ID
- `--model`: Filter by model name

## Log Output Format

Each log entry is a JSON object with these fields:
```json
{
  "trace_id": "uuid",
  "timestamp": "ISO8601",
  "model": "model_name",
  "prompt": "input_text",
  "response": "output_text", 
  "input_tokens": 123,
  "output_tokens": 456,
  "cost": 0.001234,
  "latency_ms": 1500,
  "retry_count": 0,
  "fallback_model": null
}
```
