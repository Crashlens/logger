# CrashLens Logger

A CLI tool for generating structured logs of LLM API usage. These logs are designed to be consumed by FinOps tools like CrashLens to detect token waste, fallback storms, retry loops, and enforce budget policies.

## Features

🔹 **CLI Interface** - Easy-to-use command-line interface with Click  
🔹 **Structured Logging** - JSON Lines format for easy processing  
🔹 **Token Estimation** - Estimates token usage from text input  
🔹 **Cost Calculation** - Calculates costs based on configurable model pricing  
🔹 **Retry Simulation** - Simulate retry patterns for testing  
🔹 **Fallback Simulation** - Simulate model fallback scenarios  
🔹 **YAML Configuration** - Flexible pricing configuration  
🔹 **Dev Mode** - Verbose output and debugging features  

## Installation

```bash
pip install -r requirements.txt
```

For development installation:
```bash
pip install -e .
```

## Usage

### Basic Logging

```bash
python -m crashlens_logger.logger log --model "gpt-4" --prompt "Hello, world!" --response "Hi there!"
```

### Advanced Usage

```bash
# Simulate retries
python -m crashlens_logger.logger log \
  --model "gpt-4" \
  --prompt "Complex query" \
  --response "Detailed response" \
  --simulate-retries 3 \
  --dev-mode

# Simulate fallback
python -m crashlens_logger.logger log \
  --model "gpt-4" \
  --prompt "Another query" \
  --simulate-fallback \
  --output "fallback_logs.jsonl"

# Custom configuration
python -m crashlens_logger.logger log \
  --model "custom-model" \
  --prompt "Test prompt" \
  --config "custom_pricing.yaml"
```

### Python Integration Example

You can use CrashLensLogger directly in your Python code to log structured events:

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

#### Required Fields for Structured Logging

| Field      | Description                                  | Example Value                        |
|------------|----------------------------------------------|--------------------------------------|
| traceId    | Unique request ID (UUID)                     | "trace_3921"                         |
| type       | Log type                                     | "generation"                         |
| startTime  | Start timestamp (ISO8601)                    | "2024-06-01T10:00:00Z"               |
| endTime    | End timestamp (ISO8601)                      | "2024-06-01T10:00:01Z"               |
| level      | Log level                                    | "info"                               |
| input      | Dict: model, prompt, etc.                    | {"model": "gpt-4o", "prompt": "..."} |
| usage      | Dict: token counts, etc.                     | {"prompt_tokens": 5, ...}            |
| cost       | Operation cost                               | 0.000162                             |
| metadata   | Dict: extra info (route, team, etc.)         | {"route": "...", "team": "..."}      |
| name       | Operation name                               | "simple-retry"                       |

#### Step-by-Step: Logging in Your AI Agent

1. Install: `pip install crashlens_logger`
2. Import: `from crashlens_logger import CrashLensLogger`
3. Initialize: `logger = CrashLensLogger()`
4. Collect required fields (see table above)
5. Log: `logger.log_event(traceId=..., type=..., ...)`

### Configuration Management

Initialize a sample configuration file:
```bash
python -m crashlens_logger.logger init-config --config "my_config.yaml"
```

### Log Analysis

Analyze existing log files:
```bash
python -m crashlens_logger.logger analyze logs.jsonl
python -m crashlens_logger.logger analyze logs.jsonl --model "gpt-4"
python -m crashlens_logger.logger analyze logs.jsonl --trace-id "123e4567-e89b-12d3-a456-426614174000"
```

## Log Schema

Each log entry follows this JSON schema:

```json
{
  "traceId": "trace_3921",
  "type": "generation",
  "startTime": "2024-06-01T10:00:00Z",
  "endTime": "2024-06-01T10:00:01Z",
  "level": "info",
  "input": {"model": "gpt-4o", "prompt": "What is 2+2?"},
  "usage": {"prompt_tokens": 5, "completion_tokens": 5},
  "cost": 0.000162,
  "metadata": {"fallback_attempted": false, "route": "/api/chat/completions", "team": "engineering"},
  "name": "simple-retry"
}
```

## Configuration

Create a YAML configuration file for custom model pricing:

```yaml
pricing:
  gpt-4:
    input_price_per_1k: 0.03
    output_price_per_1k: 0.06
  gpt-3.5-turbo:
    input_price_per_1k: 0.001
    output_price_per_1k: 0.002
  claude-3-opus:
    input_price_per_1k: 0.015
    output_price_per_1k: 0.075
```

## Development

The project is structured as follows:

```
crashlens_logger/
├── __init__.py          # Package initialization
└── logger.py            # Main CLI and logging logic
```

### Key Components

- **LogEvent**: Data class representing a single log entry
- **TokenEstimator**: Estimates token counts from text (placeholder for future tiktoken integration)
- **CostCalculator**: Calculates costs based on token usage and pricing
- **ConfigManager**: Handles YAML configuration loading
- **CrashLensLogger**: Main orchestrator class

## Future Enhancements

- [ ] Integration with tiktoken for accurate OpenAI token counting
- [ ] Integration with Claude tokenizer for Anthropic models
- [ ] Real API integration mode
- [ ] Dashboard for log visualization
- [ ] Advanced anomaly detection

## License

MIT License
