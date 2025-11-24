# Testing Guide

## Quick Start

### Run All Tests with Coverage
```bash
# Easiest way - use Make
make test

# Or using docker-compose
docker-compose exec api poetry run pytest
```

### View Coverage Report
```bash
# Open HTML coverage report (macOS)
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Windows
start htmlcov/index.html
```

---

## Test Commands Reference

### Basic Test Execution

```bash
# Run all tests
make test

# Run with verbose output
docker-compose exec api poetry run pytest -v

# Run with extra verbose output (shows test names)
docker-compose exec api poetry run pytest -vv

# Run quietly (minimal output)
docker-compose exec api poetry run pytest -q
```

### Coverage Commands

```bash
# Run tests with coverage (default - already in pytest.ini)
docker-compose exec api poetry run pytest

# Coverage with missing lines highlighted
docker-compose exec api poetry run pytest --cov=app --cov-report=term-missing

# Coverage with HTML report
docker-compose exec api poetry run pytest --cov=app --cov-report=html

# Coverage with both terminal and HTML
docker-compose exec api poetry run pytest --cov=app --cov-report=term-missing --cov-report=html

# Coverage with XML report (for CI/CD)
docker-compose exec api poetry run pytest --cov=app --cov-report=xml
```

### Selective Test Execution

```bash
# Run tests in specific file
docker-compose exec api poetry run pytest app/tests/api/v1/test_auth.py

# Run specific test function
docker-compose exec api poetry run pytest app/tests/api/v1/test_auth.py::test_login_success

# Run tests in specific directory
docker-compose exec api poetry run pytest app/tests/api/

# Run tests matching pattern (by name)
docker-compose exec api poetry run pytest -k "login"
docker-compose exec api poetry run pytest -k "auth"
docker-compose exec api poetry run pytest -k "user and not admin"

# Run tests by marker (if you add markers)
docker-compose exec api poetry run pytest -m "slow"
docker-compose exec api poetry run pytest -m "integration"
```

### Test Output Control

```bash
# Stop on first failure
docker-compose exec api poetry run pytest -x

# Stop after N failures
docker-compose exec api poetry run pytest --maxfail=3

# Show local variables on failure
docker-compose exec api poetry run pytest -l

# Show print statements (disable capture)
docker-compose exec api poetry run pytest -s

# Show full diff on assertion errors
docker-compose exec api poetry run pytest -vv
```

### Debug and Troubleshooting

```bash
# Run tests with Python debugger
docker-compose exec api poetry run pytest --pdb

# Drop into debugger on first failure
docker-compose exec api poetry run pytest -x --pdb

# Show warnings
docker-compose exec api poetry run pytest -W all

# Disable warnings
docker-compose exec api poetry run pytest --disable-warnings

# Show test duration (slowest tests)
docker-compose exec api poetry run pytest --durations=10

# Show test duration for all tests
docker-compose exec api poetry run pytest --durations=0
```

---

## Coverage Analysis

### Understanding Coverage Output

```
Name                                 Stmts   Miss  Cover   Missing
------------------------------------------------------------------
app/api/deps.py                        25      3    88%   45-47
app/services/auth_service.py           45      0   100%
app/services/user_service.py           67      5    93%   23, 45-47, 89
------------------------------------------------------------------
TOTAL                                 1234     89    93%
```

**Columns explained:**
- **Stmts**: Total statements (lines of code)
- **Miss**: Statements not covered by tests
- **Cover**: Coverage percentage
- **Missing**: Line numbers not covered

### Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Overall | ≥80% | Run tests to see |
| Services | ≥90% | Run tests to see |
| API Endpoints | ≥85% | Run tests to see |
| Repositories | ≥90% | Run tests to see |

### Excluded from Coverage

The following are excluded from coverage reports (see `pyproject.toml`):
- Test files (`app/tests/*`)
- Migration files (`app/migrations/*`)
- Debug code blocks
- `if __name__ == "__main__":` blocks
- Abstract methods marked with `NotImplementedError`

---

## Test Organization

### Current Test Structure

```
app/tests/
├── conftest.py                    # Shared fixtures
├── utils.py                       # Test utilities
├── api/
│   └── v1/
│       ├── test_auth.py          # Auth endpoint tests
│       ├── test_users.py         # User endpoint tests
│       └── test_health.py        # Health check tests
├── services/
│   ├── test_auth_service.py      # Auth service tests
│   ├── test_user_service.py      # User service tests
│   └── test_password_service.py  # Password service tests
├── middleware/
│   └── test_auth_middleware.py   # Middleware tests
└── test_main.py                   # Application-level tests
```

### Test Categories

#### 1. Unit Tests
Test individual components in isolation:
- Services
- Utilities
- Models

```bash
# Run only service tests
docker-compose exec api poetry run pytest app/tests/services/
```

#### 2. Integration Tests
Test component interactions:
- API endpoints
- Database operations
- Middleware

```bash
# Run only API tests
docker-compose exec api poetry run pytest app/tests/api/
```

#### 3. End-to-End Tests
Test complete workflows:
- Authentication flow
- User management flow

```bash
# Run specific E2E test
docker-compose exec api poetry run pytest app/tests/test_main.py
```

---

## Writing Tests

### Test Naming Conventions

```python
# ✅ Good test names
def test_login_with_valid_credentials_returns_token()
def test_register_with_existing_email_raises_conflict()
def test_get_user_by_id_returns_user_object()

# ❌ Bad test names
def test_login()
def test_1()
def test_user()
```

### Using Fixtures

```python
import pytest

def test_create_user(client, mock_db):
    """Test user creation endpoint."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "Password123!",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
```

### Available Fixtures (see conftest.py)

- `client`: FastAPI TestClient with mocked database
- `db`: Real database session (SQLite)
- `mock_db`: Mocked database session
- `mock_user_repository`: Mocked user repository
- `mock_auth_service`: Mocked auth service
- `auth_service`: Real auth service instance

### Mocking Dependencies

```python
from unittest.mock import MagicMock, patch

def test_with_mock():
    mock_service = MagicMock()
    mock_service.get_user.return_value = {"id": 1, "email": "test@example.com"}
    
    # Use the mock in your test
    result = mock_service.get_user(1)
    assert result["email"] == "test@example.com"
```

---

## Continuous Integration

### Running Tests in CI

Your CI pipeline should run:

```bash
# Install dependencies
poetry install

# Run tests with coverage
poetry run pytest --cov=app --cov-report=xml --cov-report=term

# Check coverage threshold (fail if below 80%)
poetry run pytest --cov=app --cov-fail-under=80
```

### Coverage Enforcement

Add to your CI configuration:

```yaml
- name: Run tests
  run: poetry run pytest --cov=app --cov-fail-under=80 --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

---

## Performance Testing

### Load Testing with Locust

```bash
# Run load tests
locust -f locustfile.py --host=http://localhost:8001

# Run in headless mode
locust -f locustfile.py --host=http://localhost:8001 \
  --users 100 --spawn-rate 10 --run-time 60s --headless
```

---

## Troubleshooting

### Common Issues

#### 1. Tests Fail Due to Database
```bash
# Reset test database
docker-compose down -v
docker-compose up -d
docker-compose exec api poetry run alembic upgrade head
```

#### 2. Import Errors
```bash
# Reinstall dependencies
docker-compose exec api poetry install
```

#### 3. Coverage Report Not Generated
```bash
# Ensure htmlcov directory exists and is writable
docker-compose exec api mkdir -p htmlcov
docker-compose exec api chmod 755 htmlcov
```

#### 4. Tests Hang or Timeout
```bash
# Run with timeout
docker-compose exec api poetry run pytest --timeout=10
```

#### 5. Flaky Tests
```bash
# Run test multiple times to identify flakiness
docker-compose exec api poetry run pytest --count=10 app/tests/api/v1/test_auth.py
```

### Debug Failed Tests

```bash
# Get detailed error trace
docker-compose exec api poetry run pytest -vv --tb=long

# Get very detailed trace
docker-compose exec api poetry run pytest -vv --tb=short

# Show only last line of trace
docker-compose exec api poetry run pytest --tb=line

# No traceback
docker-compose exec api poetry run pytest --tb=no
```

---

## Best Practices

### ✅ Do's

1. **Write tests before fixing bugs** - Reproduce the bug in a test first
2. **Test edge cases** - Empty strings, None values, large numbers, etc.
3. **Use meaningful assertions** - Check specific values, not just truthiness
4. **Keep tests independent** - Each test should run in isolation
5. **Use fixtures** - Share setup code between tests
6. **Test both success and failure** - Happy path and error cases
7. **Keep tests fast** - Use mocks for external dependencies
8. **Update tests with code** - Tests should evolve with the codebase

### ❌ Don'ts

1. **Don't test implementation details** - Test behavior, not internals
2. **Don't write tests that depend on each other** - Order shouldn't matter
3. **Don't skip tests** - Fix or delete them
4. **Don't test external services** - Mock them instead
5. **Don't ignore flaky tests** - Investigate and fix them
6. **Don't write tests without assertions** - Every test should verify something
7. **Don't test third-party code** - Trust it works, mock it

---

## Quick Commands Cheat Sheet

```bash
# Most common commands
make test                          # Run all tests with coverage
open htmlcov/index.html           # View coverage report
make lint                         # Run linting
make format                       # Format code

# Selective testing
pytest app/tests/api/             # Test specific directory
pytest -k "auth"                  # Test by pattern
pytest -x                         # Stop on first failure
pytest -v                         # Verbose output

# Coverage
pytest --cov-report=term-missing  # Show missing lines
pytest --cov-report=html          # Generate HTML report

# Debugging
pytest -s                         # Show print statements
pytest --pdb                      # Drop into debugger
pytest --lf                       # Run last failed tests
pytest --ff                       # Run failed first

# Performance
pytest --durations=10             # Show slowest tests
pytest -n auto                    # Run in parallel (needs pytest-xdist)
```

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

## Next Steps

1. Run `make test` to see current coverage
2. Open `htmlcov/index.html` to explore coverage gaps
3. Write tests for uncovered code
4. Add test markers for different test categories
5. Set up pre-commit hooks to run tests automatically
6. Configure CI/CD pipeline for automated testing


