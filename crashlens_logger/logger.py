#!/usr/bin/env python3
"""
CrashLens Logger - CLI tool for generating structured logs of LLM API usage.
Used by FinOps tools to detect token waste, fallback storms, retry loops, and enforce budget policies.
"""

import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

import click
import orjson
import yaml

try:
    from rich.console import Console
    from rich.table import Table
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback console for when rich is not available
    class Console:
        def print(self, *args, **kwargs):
            # Remove rich markup for fallback
            if args:
                clean_args = []
                for arg in args:
                    if isinstance(arg, str):
                        # Simple removal of rich markup like [color]text[/color]
                        import re
                        clean_arg = re.sub(r'\[/?[^\]]*\]', '', str(arg))
                        clean_args.append(clean_arg)
                    else:
                        clean_args.append(arg)
                print(*clean_args, **kwargs)
            else:
                print(*args, **kwargs)
    
    # Simple fallback table for when rich is not available
    class Table:
        def __init__(self, title=""):
            self.title = title
            self.columns = []
            self.rows = []
        
        def add_column(self, name, **kwargs):
            # Ignore rich-specific parameters like style, no_wrap, etc.
            self.columns.append(name)
        
        def add_row(self, *values):
            self.rows.append(values)
        
        def __str__(self):
            if not self.rows:
                return f"{self.title}\nNo data"
            
            result = f"{self.title}\n"
            result += " | ".join(self.columns) + "\n"
            result += "-" * (len(" | ".join(self.columns))) + "\n"
            for row in self.rows:
                result += " | ".join(str(cell) for cell in row) + "\n"
            return result
    
    def rprint(*args, **kwargs):
        print(*args)

# Initialize console after the try/except block
console = Console()


class LogEvent:
    """Represents a single log event with all required fields and supports arbitrary extra fields."""
    
    def __init__(
        self,
        trace_id: str = None,
        type: str = None,
        start_time: str = None,
        end_time: str = None,
        level: str = None,
        input: dict = None,
        usage: dict = None,
        cost: float = None,
        metadata: dict = None,
        name: str = None,
        # legacy fields for backward compatibility
        model: str = None,
        prompt: str = None,
        response: str = None,
        input_tokens: int = None,
        output_tokens: int = None,
        latency_ms: int = None,
        retry_count: int = None,
        fallback_model: str = None,
        **extra_fields
    ):
        # Standard fields
        self.traceId = trace_id or extra_fields.pop("traceId", None)
        self.type = type or extra_fields.pop("type", None)
        self.startTime = start_time or extra_fields.pop("startTime", None)
        self.endTime = end_time or extra_fields.pop("endTime", None)
        self.level = level or extra_fields.pop("level", None)
        self.input = input or extra_fields.pop("input", None)
        self.usage = usage or extra_fields.pop("usage", None)
        self.cost = cost if cost is not None else extra_fields.pop("cost", None)
        self.metadata = metadata or extra_fields.pop("metadata", None)
        self.name = name or extra_fields.pop("name", None)
        # Legacy/compat fields
        self.model = model
        self.prompt = prompt
        self.response = response
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.latency_ms = latency_ms
        self.retry_count = retry_count
        self.fallback_model = fallback_model
        # Store any extra fields
        self.extra_fields = extra_fields

    def _auto_usage(self):
        # Calculate total_tokens if possible
        usage = self.usage.copy() if self.usage else {}
        pt = usage.get("prompt_tokens")
        ct = usage.get("completion_tokens")
        if pt is not None and ct is not None:
            usage["total_tokens"] = pt + ct
        return usage

    def _auto_cost(self, model, usage, cost):
        # If cost is provided, use it. Otherwise, calculate if possible.
        if cost is not None:
            return cost
        # Try to calculate cost if model and usage are available
        if model and usage:
            pt = usage.get("prompt_tokens")
            ct = usage.get("completion_tokens")
            if pt is not None and ct is not None:
                # Use default pricing if available
                from .logger import ConfigManager, CostCalculator
                pricing = ConfigManager.DEFAULT_PRICING
                calc = CostCalculator(pricing)
                return calc.calculate_cost(model, pt, ct)
        return None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        # Add standard fields if present
        if self.traceId is not None:
            d["traceId"] = self.traceId
        if self.type is not None:
            d["type"] = self.type
        if self.startTime is not None:
            d["startTime"] = self.startTime
        if self.endTime is not None:
            d["endTime"] = self.endTime
        if self.level is not None:
            d["level"] = self.level
        if self.input is not None:
            d["input"] = self.input
        # Usage: auto-calculate total_tokens if possible
        usage = self._auto_usage()
        if usage:
            d["usage"] = usage
        # Cost: auto-calculate if not provided
        model = self.input.get("model") if self.input and isinstance(self.input, dict) else self.model
        d["cost"] = self._auto_cost(model, usage, self.cost)
        if self.metadata is not None:
            d["metadata"] = self.metadata
        if self.name is not None:
            d["name"] = self.name
        # Add legacy fields if present and not already included
        if self.model and (not self.input or "model" not in self.input):
            d.setdefault("input", {})["model"] = self.model
        if self.prompt and (not self.input or "prompt" not in self.input):
            d.setdefault("input", {})["prompt"] = self.prompt
        if self.response:
            d.setdefault("output", {})["response"] = self.response
        if self.input_tokens is not None or self.output_tokens is not None:
            d.setdefault("usage", {})
            if self.input_tokens is not None:
                d["usage"]["prompt_tokens"] = self.input_tokens
            if self.output_tokens is not None:
                d["usage"]["completion_tokens"] = self.output_tokens
            if self.input_tokens is not None and self.output_tokens is not None:
                d["usage"]["total_tokens"] = self.input_tokens + self.output_tokens
        if self.latency_ms is not None:
            d["latency_ms"] = self.latency_ms
        if self.retry_count is not None:
            d["retry_count"] = self.retry_count
        if self.fallback_model is not None:
            d["fallback_model"] = self.fallback_model
        # Merge in any extra fields
        d.update(self.extra_fields)
        return d

    def to_json(self) -> str:
        return orjson.dumps(self.to_dict()).decode('utf-8')


class TokenEstimator:
    """Handles token estimation logic."""
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate tokens from text using word count approximation.
        TODO: Replace with tiktoken or Claude tokenizer for accurate counts.
        """
        if not text:
            return 0
        
        # Rough approximation: 1 token ≈ 0.75 words
        word_count = len(text.split())
        return int(word_count / 0.75)


class CostCalculator:
    """Handles cost calculation based on model pricing."""
    
    def __init__(self, pricing_config: Dict[str, Dict[str, float]]):
        self.pricing = pricing_config
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage and model pricing using per-million pricing."""
        if model not in self.pricing:
            console.print(f"[yellow]Warning: No pricing data for model '{model}', using default[/yellow]")
            # Default pricing fallback (per million tokens)
            input_rate = 1.0  # $1.00 per 1M tokens
            output_rate = 2.0  # $2.00 per 1M tokens
        else:
            input_rate = self.pricing[model].get("input_rate_per_1m", 1.0)
            output_rate = self.pricing[model].get("output_rate_per_1m", 2.0)
        
        input_cost = (input_tokens / 1_000_000) * input_rate
        output_cost = (output_tokens / 1_000_000) * output_rate
        
        return round(input_cost + output_cost, 6)


class ConfigManager:
    """Handles YAML configuration loading and parsing."""
    
    DEFAULT_PRICING = {
        "gpt-4": {
            "input_rate_per_1m": 30.0,
            "output_rate_per_1m": 60.0
        },
        "gpt-4o": {
            "input_rate_per_1m": 5.0,
            "output_rate_per_1m": 15.0
        },
        "gpt-3.5-turbo": {
            "input_rate_per_1m": 1.0,
            "output_rate_per_1m": 2.0
        },
        "claude-3-opus": {
            "input_rate_per_1m": 15.0,
            "output_rate_per_1m": 75.0
        },
        "claude-3-sonnet": {
            "input_rate_per_1m": 3.0,
            "output_rate_per_1m": 15.0
        }
    }
    
    @classmethod
    def load_config(cls, config_path: Optional[str] = None) -> Dict[str, Dict[str, float]]:
        """Load pricing configuration from YAML file or use defaults."""
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                console.print(f"[green]Loaded config from {config_path}[/green]")
                return config.get("pricing", cls.DEFAULT_PRICING)
            except Exception as e:
                console.print(f"[red]Error loading config: {e}[/red]")
                console.print("[yellow]Falling back to default pricing[/yellow]")
        
        return cls.DEFAULT_PRICING


class CrashLensLogger:
    """Main logger class that orchestrates all components."""
    
    def __init__(self, config_path: Optional[str] = None, dev_mode: bool = False):
        self.pricing_config = ConfigManager.load_config(config_path)
        self.cost_calculator = CostCalculator(self.pricing_config)
        self.token_estimator = TokenEstimator()
        self.dev_mode = dev_mode
        
        if dev_mode:
            console.print("[cyan]🚀 Dev Mode Enabled[/cyan]")
    
    def generate_log_event(
        self,
        model: str,
        prompt: str,
        response: str = "",
        trace_id: Optional[str] = None,
        retry_count: int = 0,
        fallback_model: Optional[str] = None,
        simulate_latency: bool = True
    ) -> LogEvent:
        """Generate a single log event with calculated metrics."""
        
        if trace_id is None:
            trace_id = str(uuid.uuid4())
        
        # Estimate tokens
        input_tokens = self.token_estimator.estimate_tokens(prompt)
        output_tokens = self.token_estimator.estimate_tokens(response)
        
        # Calculate cost
        cost = self.cost_calculator.calculate_cost(model, input_tokens, output_tokens)
        
        # Simulate latency (for demo purposes)
        latency_ms = 0
        if simulate_latency:
            import random
            latency_ms = random.randint(100, 2000)  # 100ms to 2s
        
        return LogEvent(
            trace_id=trace_id,
            model=model,
            prompt=prompt,
            response=response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            latency_ms=latency_ms,
            retry_count=retry_count,
            fallback_model=fallback_model
        )
    
    def write_logs(self, events: List[LogEvent], output_path: str) -> None:
        """Write log events to JSONL file."""
        try:
            with open(output_path, 'a') as f:
                for event in events:
                    f.write(event.to_json() + '\n')
            
            console.print(f"[green]✅ Logged {len(events)} events to {output_path}[/green]")
            
            # Print confirmation with details
            for event in events:
                console.print(f"Logged: model={event.model}, traceId={event.trace_id[:8]}..., cost=${event.cost:.6f}")
            
            if self.dev_mode:
                self._print_events_table(events)
                
        except Exception as e:
            console.print(f"[red]❌ Error writing logs: {e}[/red]")
            raise
    
    def _print_events_table(self, events: List[LogEvent]) -> None:
        """Print events in a nice table format for dev mode."""
        table = Table(title="Generated Log Events")
        
        table.add_column("Trace ID", style="cyan" if RICH_AVAILABLE else "", no_wrap=True)
        table.add_column("Model", style="magenta" if RICH_AVAILABLE else "")
        table.add_column("Tokens (P/C/T)", style="green" if RICH_AVAILABLE else "")
        table.add_column("Cost", style="yellow" if RICH_AVAILABLE else "")
        table.add_column("Latency", style="blue" if RICH_AVAILABLE else "")
        table.add_column("Retry", style="red" if RICH_AVAILABLE else "")
        
        for event in events:
            table.add_row(
                event.trace_id[:8] + "...",
                event.model,
                f"{event.input_tokens}/{event.output_tokens}/{event.total_tokens}",
                f"${event.cost:.6f}",
                f"{event.latency_ms}ms",
                str(event.retry_count) if event.retry_count > 0 else "-"
            )
        
        if RICH_AVAILABLE:
            console.print(table)
        else:
            print(table)

    def log_event(self, output_file=None, **fields):
        """
        Log a structured event with arbitrary fields.
        If output_file is provided, append the log as a new line in that file (create if it doesn't exist).
        Otherwise, print to stdout.
        """
        event = LogEvent(**fields)
        log_line = event.to_json()
        if output_file:
            with open(output_file, 'a') as f:
                f.write(log_line + '\n')
        else:
            print(log_line)
        return event


# CLI Commands
@click.group()
@click.version_option(version="1.0.0", prog_name="crashlens-logger")
def cli():
    """CrashLens Logger - Generate structured logs for LLM API usage tracking."""
    pass


@cli.command()
@click.option("--model", required=True, help="LLM model name (e.g., gpt-4, claude-3-opus)")
@click.option("--prompt", required=True, help="Input prompt text")
@click.option("--output", default="logs.jsonl", help="Output file path")
@click.option("--trace-id", help="Custom trace ID (UUID format)")
@click.option("--simulate-retries", type=int, help="Number of retry attempts to simulate")
@click.option("--simulate-fallback", is_flag=True, help="Simulate fallback to different model")
@click.option("--simulate-overkill", is_flag=True, help="Simulate overkill scenario (small prompt with expensive model)")
@click.option("--config", help="Path to YAML config file for model pricing")
@click.option("--demo", is_flag=True, help="Trigger example log output without user input")
@click.option("--dev-mode", is_flag=True, help="Print human-readable logs to terminal instead of writing to file")
def log(
    model: str,
    prompt: str,
    output: str,
    trace_id: Optional[str],
    simulate_retries: Optional[int],
    simulate_fallback: bool,
    simulate_overkill: bool,
    config: Optional[str],
    demo: bool,
    dev_mode: bool
):
    """Generate structured log entries for LLM API usage."""
    
    # Handle demo mode
    if demo:
        console.print("[cyan]🎬 Demo Mode: Generating example log entries[/cyan]")
        model = "gpt-4"
        prompt = "What is the meaning of life?"
        trace_id = "12345678-1234-5678-9abc-def012345678"  # Valid UUID format
    
    # Handle overkill simulation
    if simulate_overkill:
        console.print("[yellow]🔥 Simulating overkill scenario[/yellow]")
        prompt = "Hi"
        if model not in ["gpt-4", "gpt-4o", "claude-3-opus"]:
            model = "gpt-4o"  # Force expensive model
    
    # Initialize logger
    logger = CrashLensLogger(config_path=config, dev_mode=dev_mode)
    
    # Validate trace_id if provided
    if trace_id:
        try:
            uuid.UUID(trace_id)
        except ValueError:
            console.print(f"[red]❌ Invalid trace-id format. Expected UUID, got: {trace_id}[/red]")
            raise click.Abort()
    
    events = []
    
    # Generate response based on mode
    response = ""
    if demo:
        response = "42 - The answer to the ultimate question of life, the universe, and everything."
    elif simulate_overkill:
        response = "Hello!"
    else:
        # Generate a realistic response based on the prompt
        response = f"This is a simulated response for: '{prompt[:30]}...'"
    
    # Generate base trace ID
    base_trace_id = trace_id or str(uuid.uuid4())
    
    # Handle retry simulation
    if simulate_retries:
        console.print(f"[yellow]🔄 Simulating {simulate_retries} retries[/yellow]")
        
        # Generate failed retry attempts
        for retry_num in range(1, simulate_retries + 1):
            retry_event = logger.generate_log_event(
                model=model,
                prompt=prompt,
                response="",  # Failed attempts have no response
                trace_id=base_trace_id,
                retry_count=retry_num
            )
            events.append(retry_event)
        
        # Final successful attempt
        success_event = logger.generate_log_event(
            model=model,
            prompt=prompt,
            response=response,
            trace_id=base_trace_id,
            retry_count=simulate_retries + 1
        )
        events.append(success_event)
    
    # Handle fallback simulation
    elif simulate_fallback:
        console.print("[yellow]🔀 Simulating model fallback[/yellow]")
        
        # Failed attempt with primary model
        failed_event = logger.generate_log_event(
            model=model,
            prompt=prompt,
            response="",  # Failed attempt
            trace_id=base_trace_id,
            retry_count=1
        )
        events.append(failed_event)
        
        # Successful attempt with fallback model
        fallback_models = ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"]
        fallback_model = next((m for m in fallback_models if m != model), "gpt-3.5-turbo")
        
        success_event = logger.generate_log_event(
            model=fallback_model,
            prompt=prompt,
            response=response,
            trace_id=base_trace_id,
            retry_count=2,
            fallback_model=fallback_model
        )
        events.append(success_event)
    
    # Normal single log event
    else:
        event = logger.generate_log_event(
            model=model,
            prompt=prompt,
            response=response,
            trace_id=base_trace_id
        )
        events.append(event)
    
    # Handle output mode
    if dev_mode:
        console.print("[cyan]💻 Dev Mode: Printing human-readable logs to terminal[/cyan]")
        logger._print_events_table(events)
        for event in events:
            console.print(f"\n[green]Log Entry:[/green]")
            console.print(f"  TraceId: {event.trace_id}")
            console.print(f"  Model: {event.model}")
            console.print(f"  Prompt: {event.prompt}")
            console.print(f"  Response: {event.response}")
            console.print(f"  Tokens: {event.input_tokens}/{event.output_tokens}/{event.total_tokens}")
            console.print(f"  Cost: ${event.cost:.6f}")
            console.print(f"  Retry: {event.retry_count}")
    else:
        # Write logs to file
        logger.write_logs(events, output)


@cli.command()
@click.option("--config", help="Path to config file to create")
def init_config(config: Optional[str]):
    """Initialize a sample configuration file."""
    config_path = config or "crashlens_config.yaml"
    
    sample_config = {
        "pricing": {
            "gpt-4": {
                "input_rate_per_1m": 30.0,
                "output_rate_per_1m": 60.0
            },
            "gpt-4o": {
                "input_rate_per_1m": 5.0,
                "output_rate_per_1m": 15.0
            },
            "gpt-3.5-turbo": {
                "input_rate_per_1m": 1.0,
                "output_rate_per_1m": 2.0
            },
            "claude-3-opus": {
                "input_rate_per_1m": 15.0,
                "output_rate_per_1m": 75.0
            },
            "claude-3-sonnet": {
                "input_rate_per_1m": 3.0,
                "output_rate_per_1m": 15.0
            }
        }
    }
    
    try:
        with open(config_path, 'w') as f:
            yaml.dump(sample_config, f, default_flow_style=False, indent=2)
        
        console.print(f"[green]✅ Created sample config at {config_path}[/green]")
        console.print(f"[cyan]Edit this file to customize model pricing[/cyan]")
        
    except Exception as e:
        console.print(f"[red]❌ Error creating config: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.argument("log_file", type=click.Path(exists=True))
@click.option("--trace-id", help="Filter by specific trace ID")
@click.option("--model", help="Filter by model name")
def analyze(log_file: str, trace_id: Optional[str], model: Optional[str]):
    """Analyze existing log files and show statistics."""
    try:
        events = []
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    event_data = orjson.loads(line)
                    events.append(event_data)
        
        # Apply filters
        if trace_id:
            events = [e for e in events if e.get("traceId") == trace_id]
        
        if model:
            events = [e for e in events if e.get("input", {}).get("model") == model]
        
        if not events:
            console.print("[yellow]No events found matching criteria[/yellow]")
            return
        
        # Calculate statistics
        total_cost = sum(e.get("cost", 0) for e in events)
        total_input_tokens = sum(e.get("usage", {}).get("prompt_tokens", 0) for e in events)
        total_output_tokens = sum(e.get("usage", {}).get("completion_tokens", 0) for e in events)
        total_tokens = sum(e.get("usage", {}).get("total_tokens", 0) for e in events)
        avg_latency = sum(e.get("latency_ms", 0) for e in events) / len(events)
        
        # Print analysis
        table = Table(title=f"Log Analysis: {log_file}")
        table.add_column("Metric", style="cyan" if RICH_AVAILABLE else "")
        table.add_column("Value", style="green" if RICH_AVAILABLE else "")
        
        table.add_row("Total Events", str(len(events)))
        table.add_row("Total Cost", f"${total_cost:.6f}")
        table.add_row("Total Input Tokens", f"{total_input_tokens:,}")
        table.add_row("Total Output Tokens", f"{total_output_tokens:,}")
        table.add_row("Total Tokens", f"{total_tokens:,}")
        table.add_row("Average Latency", f"{avg_latency:.1f}ms")
        
        if RICH_AVAILABLE:
            console.print(table)
        else:
            print(table)
        
    except Exception as e:
        console.print(f"[red]❌ Error analyzing log file: {e}[/red]")
        raise click.Abort()


def main():
    """Main entry point for the CLI application."""
    cli()


if __name__ == "__main__":
    main()
