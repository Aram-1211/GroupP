import sys
from pathlib import Path

import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Simple placeholder test that will pass
def test_placeholder():
    """
    Placeholder test to verify CI/CD pipeline works.
    Replace with actual tests for your application.
    """
    assert True


def test_imports():
    """Test that main modules can be imported"""
    try:
        from main import app
        assert app is not None
    except Exception as e:
        pytest.fail(f"Failed to import app: {e}")
