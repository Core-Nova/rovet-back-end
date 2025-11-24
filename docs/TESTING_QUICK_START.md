# Testing Quick Start

## 🚀 Run Tests Right Now

```bash
# All tests with coverage
docker-compose exec api pytest --cov=app --cov-report=html -v

# View coverage
open htmlcov/index.html
```

---

## 📊 Run Specific Test Types

```bash
# Unit tests only (FAST - <1 second)
docker-compose exec api pytest -m unit -v

# Integration tests only (MEDIUM - ~3 seconds)
docker-compose exec api pytest -m integration -v

# E2E tests only (SLOWER - ~10 seconds)
docker-compose exec api pytest -m e2e -v

# Database tests only
docker-compose exec api pytest -m db -v

# All except slow tests (good for development)
docker-compose exec api pytest -m "not slow" -v
```

---

## 📁 Run Specific Test Files

```bash
# Run one file
docker-compose exec api pytest tests/unit/test_user_service_unit.py -v

# Run one test
docker-compose exec api pytest tests/e2e/test_auth_flow_e2e.py::TestUserRegistrationFlow::test_complete_registration_flow -v

# Run all E2E tests
docker-compose exec api pytest tests/e2e/ -v

# Run all unit tests
docker-compose exec api pytest tests/unit/ -v
```

---

## 🎯 Development Workflow

### During Development (Fast Feedback)
```bash
# Run unit tests (< 1 second)
docker-compose exec api pytest -m unit -v
```

### Before Commit (More Comprehensive)
```bash
# Run unit + integration tests
docker-compose exec api pytest -m "unit or integration" --cov=app -v
```

### Before Pull Request (Everything)
```bash
# Run full suite with coverage
docker-compose exec api pytest --cov=app --cov-report=html --cov-report=term-missing -v

# Check coverage is ≥80%
open htmlcov/index.html
```

---

## ⚡ Pro Tips

### Watch Mode
```bash
# Re-run tests on file changes
docker-compose exec api ptw tests/ -- -v
```

### Parallel Execution
```bash
# Run tests in parallel (faster)
docker-compose exec api pytest -n auto -v
```

### Stop on First Failure
```bash
# Stop immediately when test fails
docker-compose exec api pytest -x -v
```

### Show Print Statements
```bash
# See print() output
docker-compose exec api pytest -s -v
```

### Show Slowest Tests
```bash
# See which tests are slow
docker-compose exec api pytest --durations=10 -v
```

---

## 📊 Test Coverage Goals

| Layer | Current | Target | Command |
|-------|---------|--------|---------|
| Overall | Run tests to see | ≥80% | `pytest --cov=app` |
| Services | Run tests to see | ≥90% | `pytest --cov=app/services` |
| Endpoints | Run tests to see | ≥85% | `pytest --cov=app/api` |
| Repositories | Run tests to see | ≥90% | `pytest --cov=app/repositories` |

---

## 🐛 Debugging Failed Tests

### Get More Info
```bash
# Verbose output
docker-compose exec api pytest -vv

# Show full traceback
docker-compose exec api pytest --tb=long

# Drop into debugger on failure
docker-compose exec api pytest --pdb
```

### Re-run Failed Tests
```bash
# Run only tests that failed last time
docker-compose exec api pytest --lf -v

# Run failed tests first, then others
docker-compose exec api pytest --ff -v
```

---

## ✅ What Tests Exist

### Unit Tests (`tests/unit/`)
- `test_user_service_unit.py` - UserService business logic

### Integration Tests (`tests/integration/`)
- `test_user_service_integration.py` - Service + Repository + DB
- `test_user_repository.py` - Database operations

### E2E Tests (`tests/e2e/`)
- `test_auth_flow_e2e.py` - Complete user workflows

### Supporting Files
- `conftest.py` - All fixtures
- `factories.py` - Test data generation

---

## 🎓 Test Examples

### Unit Test Example
```python
@pytest.mark.unit
def test_create_user_unit(mock_user_repository, mock_password_service):
    service = UserService(mock_user_repository, mock_password_service)
    user = service.create_user(user_data)
    assert user.email == user_data.email
```

### Integration Test Example
```python
@pytest.mark.integration
def test_create_user_integration(user_service, db):
    user = user_service.create_user(user_data)
    # Verify in database
    db_user = db.query(User).filter_by(email=user.email).first()
    assert db_user is not None
```

### E2E Test Example
```python
@pytest.mark.e2e
def test_user_journey_e2e(client_e2e):
    # Register
    register_response = client_e2e.post("/api/v1/auth/register", json={...})
    assert register_response.status_code == 201
    
    # Login
    login_response = client_e2e.post("/api/v1/auth/login", json={...})
    token = login_response.json()["access_token"]
    
    # Use token
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = client_e2e.get("/api/v1/auth/me", headers=headers)
    assert profile_response.status_code == 200
```

---

## 📝 Quick Reference Card

| Want to... | Command |
|------------|---------|
| Run all tests | `pytest -v` |
| Run with coverage | `pytest --cov=app -v` |
| View coverage report | `open htmlcov/index.html` |
| Run unit tests | `pytest -m unit -v` |
| Run E2E tests | `pytest -m e2e -v` |
| Run one file | `pytest tests/unit/test_user_service_unit.py -v` |
| Run one test | `pytest tests/e2e/test_auth_flow_e2e.py::test_name -v` |
| Stop on first fail | `pytest -x -v` |
| Show print output | `pytest -s -v` |
| Debug failed test | `pytest --pdb` |
| Re-run failed | `pytest --lf -v` |
| Run fast tests | `pytest -m "not slow" -v` |
| Parallel execution | `pytest -n auto -v` |

---

## 🎯 Recommended Workflow

```bash
# 1. Start services
docker-compose up -d

# 2. Run fast tests during development
docker-compose exec api pytest -m unit -v

# 3. Make code changes...

# 4. Run relevant tests
docker-compose exec api pytest tests/unit/test_user_service_unit.py -v

# 5. Before commit - run unit + integration
docker-compose exec api pytest -m "unit or integration" --cov=app -v

# 6. Before PR - run everything
docker-compose exec api pytest --cov=app --cov-report=html --cov-report=term-missing -v

# 7. Check coverage
open htmlcov/index.html

# 8. Fix any gaps, commit!
git add .
git commit -m "feat: add new feature with tests"
```

---

## 🆘 Common Issues

### Import Errors
```bash
# Reinstall dependencies
docker-compose exec api poetry install
```

### Database Errors
```bash
# Recreate test database
docker-compose down -v
docker-compose up -d
```

### Tests Hanging
```bash
# Add timeout
docker-compose exec api pytest --timeout=10
```

### Can't See Print Output
```bash
# Use -s flag
docker-compose exec api pytest -s -v
```

---

**Quick Start:** `docker-compose exec api pytest --cov=app -v && open htmlcov/index.html`

**Documentation:** See `docs/TESTING_WITH_DI.md` for comprehensive guide

