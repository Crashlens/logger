# CrashLens Logger 🧠💸  
Structured Token & Cost Logs for OpenAI / Anthropic Usage

[![PyPI version](https://badge.fury.io/py/crashlens_logger.svg)](https://badge.fury.io/py/crashlens_logger)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> ⚠️ Are you burning money on GPT calls without knowing where or why?  
> CrashLens Logger captures cost, tokens, and prompts in JSON logs — for FinOps, audits, or debugging.

---

## Purpose

**CrashLens Logger** is a Python package for generating structured, machine-readable logs of LLM (Large Language Model) API usage.  
It helps you:
- Track prompt, model, and token usage for every AI call
- Automatically calculate cost using standard model pricing
- Output logs in newline-delimited JSON (NDJSON) for easy analysis, monitoring, and cost tracking

---

## Real Use Cases

- 🔍 Debug fallback loops by logging all model calls with prompt/token trace
- 💰 Auto-generate cost reports across agents & users
- 🧠 Analyze which prompts are burning tokens (and why)
- 🛡️ Audit LLM usage for compliance or security

---

## Installation

```bash
pip install --upgrade crashlens_logger
```
_This will install or upgrade to the latest version._

---

## Quick Start

```python
from crashlens_logger import CrashLensLogger
import uuid
from datetime import datetime
import openai

logger = CrashLensLogger()

def call_and_log():
    trace_id = str(uuid.uuid4())
    start_time = datetime.utcnow().isoformat() + "Z"
    prompt = "What are the main tourist attractions in Rome?"
    model = "gpt-3.5-turbo"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    end_time = datetime.utcnow().isoformat() + "Z"
    usage = response["usage"]
    logger.log_event(
        traceId=trace_id,
        startTime=start_time,
        endTime=end_time,
        input={"model": model, "prompt": prompt},
        usage=usage
    )
```

---

## Where Do Logs Go?

By default, logs are printed to `stdout` in newline-delimited JSON (NDJSON) format.  
You can redirect output to a file:

```bash
python your_script.py > logs.jsonl
```

---

## Example Output

```json
{
  "traceId": "trace_norm_01",
  "startTime": "2025-07-22T10:30:05Z",
  "input": {"model": "gpt-3.5-turbo", "prompt": "What are the main tourist attractions in Rome?"},
  "usage": {"prompt_tokens": 10, "completion_tokens": 155, "total_tokens": 165},
  "cost": 0.0002375
}
```

---

## What Gets Calculated Automatically?

- **total_tokens**: If you provide `prompt_tokens` and `completion_tokens` in `usage`, the logger adds `total_tokens`.
- **cost**: If you provide `model`, `prompt_tokens`, and `completion_tokens`, the logger calculates cost using standard pricing.

---

## Troubleshooting

- **Cannot resolve host:** Check your internet connection or DNS.
- **pip cache issues:** Try `pip install --no-cache-dir crashlens_logger`
- **Permission errors:** Use a virtual environment or add `--user` to your pip command.
- **Module not found:** Ensure you’re using the correct Python environment.

---

## Roadmap

- [ ] Token pricing overrides
- [ ] File/DB exporters
- [ ] SDK instrumentation helpers
- [ ] Pydantic validation for log structure

---

## Testing

Run tests with:

```bash
pytest
```

*100% coverage on core logging logic.*

---

## License

MIT License

