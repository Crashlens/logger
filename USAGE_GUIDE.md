# CrashLens Logger - Usage Guide

## 1. Install or Upgrade the Package from PyPI

```bash
pip install --upgrade crashlens_logger
```

*This command will install the package if not present, or upgrade it to the latest version if already installed.*

---

## 2. Import and Initialize the Logger

At the top of your Python file:

```python
from crashlens_logger import CrashLensLogger
logger = CrashLensLogger()
```

---

## 3. Collect Required Parameters in Your Code

When you make an AI API call (e.g., to OpenAI, Anthropic, etc.), collect the following:

| Parameter   | How to Get It in Your Codebase (AI Agent)                                   | Example Code / Notes                                 |
|-------------|-----------------------------------------------------------------------------|------------------------------------------------------|
| **traceId** | Generate a unique ID for each request (UUID or from your framework)         | `import uuid; trace_id = str(uuid.uuid4())`<br>Or use a request/session ID if your framework provides one. |
| **startTime** | Record the time before processing the request                             | `from datetime import datetime; start_time = datetime.utcnow().isoformat() + "Z"` |
| **endTime** | Record the time after processing the request                                | `end_time = datetime.utcnow().isoformat() + "Z"`     |
| **input**   | Dictionary with model, prompt, etc.                                         | `input_data = {"model": model_name, "prompt": prompt}` |
| **usage**   | Dictionary with token counts, etc. (from LLM API response or estimate)      | `usage = response["usage"]`<br>Or extract from your LLM API response. |

*You do NOT need to provide `total_tokens` or `cost`—the logger will calculate these automatically!*

---

## 4. Log the Structured Event

After your AI agent processes the request, call:

```python
logger.log_event(
    traceId=trace_id,
    startTime=start_time,
    endTime=end_time,
    input={"model": model, "prompt": prompt},
    usage=usage
    # Optionally add: type, level, metadata, name, etc.
)
```

---

## 5. Full Example: Logging an OpenAI API Call

```python
from crashlens_logger import CrashLensLogger
import uuid
from datetime import datetime
import openai  # or your LLM provider

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
    usage = response["usage"]  # {'prompt_tokens': ..., 'completion_tokens': ...}
    logger.log_event(
        traceId=trace_id,
        startTime=start_time,
        endTime=end_time,
        input={"model": model, "prompt": prompt},
        usage=usage
    )
```

---

## 6. What Gets Calculated Automatically?

- **total_tokens**: If you provide `prompt_tokens` and `completion_tokens` in `usage`, the logger will add `total_tokens` automatically.
- **cost**: If you provide `model`, `prompt_tokens`, and `completion_tokens`, the logger will calculate the cost using standard pricing.

---

## 7. Output Example

The logger will print a JSON log like:

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

## 8. Tips
- You can add extra fields (like `type`, `level`, `metadata`, `name`) if you want more detail.
- For custom pricing, see the README for configuration options.
- For troubleshooting, see the README setup section.
