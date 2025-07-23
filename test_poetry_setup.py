#!/usr/bin/env python3
"""
Test script to verify Poetry setup and basic functionality.
Run this after installing with Poetry to verify everything works.
"""

def test_imports():
    """Test that all required imports work."""
    print("🔍 Testing imports...")
    
    try:
        import click
        print("✅ click imported successfully")
    except ImportError as e:
        print(f"❌ click import failed: {e}")
        return False
    
    try:
        import orjson
        print("✅ orjson imported successfully")
        
        # Test orjson functionality
        test_data = {"test": "data", "number": 42}
        json_str = orjson.dumps(test_data).decode('utf-8')
        parsed = orjson.loads(json_str)
        assert parsed == test_data
        print("✅ orjson serialization/deserialization works")
    except ImportError as e:
        print(f"❌ orjson import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ orjson functionality test failed: {e}")
        return False
    
    try:
        import yaml
        print("✅ pyyaml imported successfully")
    except ImportError as e:
        print(f"❌ pyyaml import failed: {e}")
        return False
    
    try:
        from rich.console import Console
        from rich.table import Table
        print("✅ rich imported successfully (optional dependency)")
    except ImportError:
        print("⚠️  rich not available (optional dependency)")
    
    return True


def test_cli_import():
    """Test that the CLI can be imported."""
    print("\n🔍 Testing CLI import...")
    
    try:
        from crashlens_logger.logger import cli, main
        print("✅ CLI imported successfully")
        return True
    except ImportError as e:
        print(f"❌ CLI import failed: {e}")
        return False


def test_core_classes():
    """Test that core classes can be instantiated."""
    print("\n🔍 Testing core classes...")
    
    try:
        from crashlens_logger.logger import LogEvent, TokenEstimator, CostCalculator, ConfigManager
        
        # Test LogEvent
        event = LogEvent(
            trace_id="test-123",
            model="test-model",
            prompt="test prompt",
            response="test response"
        )
        print("✅ LogEvent created successfully")
        
        # Test JSON serialization
        json_str = event.to_json()
        assert "test-123" in json_str
        print("✅ LogEvent JSON serialization works")
        
        # Test TokenEstimator
        estimator = TokenEstimator()
        tokens = estimator.estimate_tokens("hello world test")
        assert tokens > 0
        print("✅ TokenEstimator works")
        
        # Test ConfigManager
        config = ConfigManager.load_config()
        assert "gpt-4" in config
        print("✅ ConfigManager works")
        
        # Test CostCalculator
        calculator = CostCalculator(config)
        cost = calculator.calculate_cost("gpt-4", 100, 50)
        assert cost > 0
        print("✅ CostCalculator works")
        
        return True
    except Exception as e:
        print(f"❌ Core classes test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 CrashLens Logger - Poetry Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_cli_import,
        test_core_classes
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Poetry setup is working correctly.")
        print("\n💡 Try running: crashlens-logger --help")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        exit(1)


if __name__ == "__main__":
    main()
