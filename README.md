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
  "trace_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-07-23T10:30:00.000Z",
  "model": "gpt-4",
  "prompt": "Hello, world!",
  "response": "Hi there!",
  "input_tokens": 3,
  "output_tokens": 3,
  "cost": 0.00018,
  "latency_ms": 1250,
  "retry_count": 0,
  "fallback_model": null
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
