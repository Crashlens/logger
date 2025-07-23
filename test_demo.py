#!/usr/bin/env python3
"""
Test script to demonstrate CrashLens Logger functionality.
Run this script to see the logger in action with various scenarios.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
        print(f"Exit code: {result.returncode}")
    except Exception as e:
        print(f"Failed to run command: {e}")

def main():
    """Run test scenarios for the CrashLens Logger."""
    
    print("🚀 CrashLens Logger Test Suite")
    print("Testing various logging scenarios...")
    
    # Clean up any existing test logs
    test_files = ["test_logs.jsonl", "retry_logs.jsonl", "fallback_logs.jsonl"]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
    
    # Test 1: Basic logging
    run_command(
        'python -m crashlens_logger.logger log --model "gpt-4" --prompt "What is the meaning of life?" --response "42" --output "test_logs.jsonl" --dev-mode',
        "Basic Logging Test"
    )
    
    # Test 2: Retry simulation
    run_command(
        'python -m crashlens_logger.logger log --model "gpt-4" --prompt "Complex reasoning task" --response "Well thought out answer" --simulate-retries 3 --output "retry_logs.jsonl" --dev-mode',
        "Retry Simulation Test"
    )
    
    # Test 3: Fallback simulation
    run_command(
        'python -m crashlens_logger.logger log --model "gpt-4" --prompt "Fallback test prompt" --simulate-fallback --output "fallback_logs.jsonl" --dev-mode',
        "Fallback Simulation Test"
    )
    
    # Test 4: Initialize config
    run_command(
        'python -m crashlens_logger.logger init-config --config "test_config.yaml"',
        "Config Initialization Test"
    )
    
    # Test 5: Custom config usage
    run_command(
        'python -m crashlens_logger.logger log --model "claude-3-opus" --prompt "Test with custom config" --response "Response from Claude" --config "test_config.yaml" --dev-mode',
        "Custom Config Test"
    )
    
    # Test 6: Log analysis
    run_command(
        'python -m crashlens_logger.logger analyze test_logs.jsonl',
        "Log Analysis Test"
    )
    
    # Test 7: Filtered analysis
    run_command(
        'python -m crashlens_logger.logger analyze retry_logs.jsonl --model "gpt-4"',
        "Filtered Log Analysis Test"
    )
    
    print(f"\n{'='*60}")
    print("🎉 Test Suite Complete!")
    print("Check the generated log files:")
    for file in test_files + ["test_config.yaml"]:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  ✅ {file} ({size} bytes)")
        else:
            print(f"  ❌ {file} (not found)")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
