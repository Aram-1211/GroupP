# CI/CD Configuration Guide

## Overview
This project is configured with GitHub Actions for automated testing and code quality checks.

## Workflow Features

### 1. Automated Testing (test.yml)
- **Trigger Conditions**: Pushes to main or Yiming-side branches, or Pull Requests
- **Environment**: Ubuntu Latest + Python 3.11
- **Steps**:
  - ✅ Checkout code
  - ✅ Install Python dependencies
  - ✅ Run pytest unit tests
  - ✅ Generate coverage reports
  - ✅ Code style checks (flake8)
  - ✅ Import order verification (isort)

## Local Testing

Before submitting, you can run the same tests locally:

```bash
# Install test dependencies
pip install pytest pytest-cov flake8 isort

# Run tests
pytest backend/tests/ -v

# Check code style
flake8 backend --max-line-length=100

# Check imports
isort backend --check-only
```

## Adding More Tests

Create test files in the `backend/tests/` directory:
- Test files must start with `test_`, for example `test_models.py`
- Name test functions with `def test_` prefix

## CI/CD Status
GitHub will display CI/CD status in Pull Requests. Green ✅ means passed, Red ❌ means failed.

## Troubleshooting
- **Dependency Errors**: Ensure `backend/requirements.txt` is up to date
- **Test Failures**: Check if `pytest` can run locally
- **Import Errors**: Run `isort backend` to auto-fix import order
