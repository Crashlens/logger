# CrashLens Logger OSS v0.1 - Complete Usage Guide

## ✅ OSS v0.1 Feature Implementation

The CrashLens Logger has been updated to match the complete OSS v0.1 feature checklist. Here's what's implemented:

### 📁 **Output Format** ✅
- Outputs logs in `.jsonl` format (one JSON object per line)
- Each log entry includes:
  - `traceId` (string)
  - `type: "generation"`
  - `startTime` in ISO 8601 UTC format
  - `input.model` and `input.prompt`
  - `usage.prompt_tokens`, `completion_tokens`, `total_tokens`
  - `cost` field with 6-digit precision (float)

### 🧠 **Cost Estimation** ✅
- Uses internal `pricing.yaml` or model_pricing dict
- Calculates cost as: `cost = (input_tokens / 1_000_000) * input_rate + (output_tokens / 1_000_000) * output_rate`
- Rounds cost to 6 decimal places
- Uses default fallback rate if model unknown

### 🛠 **CLI Interface** ✅
All required flags implemented:
- `--model` ✅
- `--prompt` ✅
- `--output` ✅
- `--trace-id` ✅
- `--simulate-retries N` ✅
- `--simulate-fallback` ✅
- `--simulate-overkill` ✅
- `--config pricing.yaml` ✅
- `--demo` ✅
- `--dev-mode` ✅

### 🔄 **Retry & Fallback Simulation** ✅
- Simulates retries with same model and prompt, incrementing retry count
- Simulates fallback by trying different models in sequence under same traceId
- Simulates failure status in early retries and success in final call
- Tracks and logs `retry_attempt`

### 🧪 **Overkill Model Simulation** ✅
- Forces small prompt (e.g., "Hi") with expensive model like gpt-4o
- Logs token count < 10 with high-cost model

### 🖥 **Dev & Demo Mode** ✅
- `--demo` triggers example log output without user input
- `--dev-mode` prints human-readable logs to terminal instead of writing to file

### 📦 **Output Handling** ✅
- Appends logs to `logs.jsonl` file unless `--dev-mode` is enabled
- Uses safe file writing with append mode
- Prints confirmation: `Logged: model=..., traceId=..., cost=...`

### 🧼 **Robustness & Defaults** ✅
- Handles missing/invalid fields gracefully
- Generates default traceId if none provided
- Detects and warns on unknown models

## 🚀 **Usage Examples**

### Basic Logging
```bash
python -m crashlens_logger.logger log --model "gpt-4" --prompt "What is AI?"
```

### Demo Mode
```bash
python -m crashlens_logger.logger log --model "gpt-4" --prompt "test" --demo
```

### Overkill Simulation
```bash
python -m crashlens_logger.logger log --model "gpt-3.5-turbo" --prompt "Hi" --simulate-overkill --dev-mode
```

### Retry Simulation
```bash
python -m crashlens_logger.logger log --model "gpt-4" --prompt "Complex task" --simulate-retries 3 --dev-mode
```

### Fallback Simulation
```bash
python -m crashlens_logger.logger log --model "gpt-4" --prompt "Fallback test" --simulate-fallback --dev-mode
```

### Development Mode
```bash
python -m crashlens_logger.logger log --model "gpt-4" --prompt "Debug test" --dev-mode
```

### Custom Configuration
```bash
python -m crashlens_logger.logger init-config --config "custom_pricing.yaml"
python -m crashlens_logger.logger log --model "custom-model" --prompt "Test" --config "custom_pricing.yaml"
```

### Log Analysis
```bash
python -m crashlens_logger.logger analyze logs.jsonl
python -m crashlens_logger.logger analyze logs.jsonl --model "gpt-4"
```

## 📊 **Log Format Example**

```json
{
  "traceId": "12345678-1234-5678-9abc-def012345678",
  "type": "generation",
  "startTime": "2025-07-23T15:30:45.123Z",
  "input": {
    "model": "gpt-4",
    "prompt": "What is machine learning?"
  },
  "output": {
    "response": "Machine learning is a subset of AI..."
  },
  "usage": {
    "prompt_tokens": 5,
    "completion_tokens": 18,
    "total_tokens": 23
  },
  "cost": 0.001320,
  "latency_ms": 1250,
  "retry_attempt": 0,
  "fallback_model": null
}
```

## 🔧 **Configuration Format**

The pricing configuration now uses per-million token pricing:

```yaml
pricing:
  gpt-4:
    input_rate_per_1m: 30.0
    output_rate_per_1m: 60.0
  gpt-4o:
    input_rate_per_1m: 5.0
    output_rate_per_1m: 15.0
  gpt-3.5-turbo:
    input_rate_per_1m: 1.0
    output_rate_per_1m: 2.0
```

## 🎯 **Key Features Demonstrated**

✅ **Accurate Cost Calculation**: Uses per-million token pricing for precise cost estimation  
✅ **Comprehensive Simulation**: Retry, fallback, and overkill scenarios  
✅ **Developer Experience**: Demo and dev modes for easy testing and debugging  
✅ **Robust Output**: Structured JSON logs with all required fields  
✅ **Flexible Configuration**: YAML-based pricing configuration  
✅ **Analysis Tools**: Built-in log analysis with filtering capabilities  

The CrashLens Logger OSS v0.1 is now fully implemented and ready for production use! 🚀
