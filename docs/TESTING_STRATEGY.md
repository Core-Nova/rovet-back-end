# Comprehensive Testing Strategy

## 🎯 Testing Philosophy

With **Dependency Injection**, we can easily switch between:
- **Real implementations** → End-to-end tests (minimal mocking)
- **Mock implementations** → Unit tests (maximum isolation)
- **Mixed approach** → Integration tests (test interactions)

---

## 📊 Test Pyramid

```
         /\
        /  \    E2E Tests (5%)
       /────\   - Full workflows
      /      \  - Real DB, Real services
     /────────\ - Minimal mocking
    /          \
   /Integration \ (25%)
  /    Tests     \
 /────────────────\
/                  \
/   Unit Tests     \ (70%)
/  (Fast, Isolated) \
/────────────────────\
```

### 1. Unit Tests (70%) - Isolated, Fast
- **What:** Test single component in isolation
- **Mock:** Everything except the component under test
- **Speed:** Very fast (<1ms per test)
- **Example:** Test UserService.create_user with mocked repository

### 2. Integration Tests (25%) - Component Interactions
- **What:** Test how components work together
- **Mock:** External services only (DB is real test DB)
- **Speed:** Fast (10-100ms per test)
- **Example:** Test UserService + UserRepository + real DB

### 3. End-to-End Tests (5%) - Full Workflows
- **What:** Test complete user workflows
- **Mock:** Minimal (maybe external APIs)
- **Speed:** Slower (100-1000ms per test)
- **Example:** Register → Login → Get profile → Update → Delete

---

## 🎭 How DI Helps Testing

### Unit Test (Maximum Mocking)
```python
def test_create_user_unit(client):
    # Mock the entire service
    mock_service = MagicMock()
    mock_service.create_user.return_value = UserResponse(...)
    
    # Override dependency with mock
    app.dependency_overrides[get_user_service] = lambda: mock_service
    
    # Test endpoint logic only
    response = client.post("/api/v1/auth/register", json={...})
    
    assert response.status_code == 201
    mock_service.create_user.assert_called_once()
```

### E2E Test (Minimal Mocking)
```python
def test_user_registration_flow_e2e(client_e2e, clean_db):
    # NO MOCKING - use real services, real DB
    # Just override DB with test DB
    
    # 1. Register
    response = client_e2e.post("/api/v1/auth/register", json={
        "email": "john@example.com",
        "password": "SecurePass123!",
        "full_name": "John Doe"
    })
    assert response.status_code == 201
    
    # 2. Login
    response = client_e2e.post("/api/v1/auth/login", json={
        "email": "john@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 3. Get profile
    response = client_e2e.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "john@example.com"
```

---

## 📁 Test Organization

```
app/tests/
├── conftest.py                    # Shared fixtures
├── factories.py                   # Test data factories
│
├── unit/                          # Unit tests (70%)
│   ├── test_password_service.py   # Pure logic, no dependencies
│   ├── test_user_service_unit.py  # Service with mocked repo
│   └── test_auth_service_unit.py  # Service with mocked user service
│
├── integration/                   # Integration tests (25%)
│   ├── test_user_service_integration.py  # Service + repo + real DB
│   ├── test_auth_service_integration.py  # Auth + user service + real DB
│   └── test_repositories.py               # Repo + real DB
│
├── e2e/                           # End-to-end tests (5%)
│   ├── test_auth_flow.py          # Register → Login → Profile
│   ├── test_user_management.py    # Full CRUD workflow
│   └── test_admin_operations.py   # Admin workflows
│
└── api/                           # API endpoint tests (can be unit or e2e)
    └── v1/
        ├── test_auth_endpoints.py
        └── test_user_endpoints.py
```

---

## 🔧 Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_password_hashing():
    ...

@pytest.mark.integration
def test_user_service_with_db():
    ...

@pytest.mark.e2e
def test_complete_user_journey():
    ...

@pytest.mark.slow
def test_bulk_operations():
    ...
```

**Run specific test types:**
```bash
# Fast unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# E2E tests
pytest -m e2e

# Everything except slow tests
pytest -m "not slow"

# Unit + integration (skip E2E)
pytest -m "unit or integration"
```

---

## ✅ What Each Test Type Should Cover

### Unit Tests
- [ ] Password validation logic
- [ ] JWT token creation/verification
- [ ] DTO validation rules
- [ ] Service business logic (with mocked dependencies)
- [ ] Utility functions
- [ ] Error handling in services

### Integration Tests
- [ ] User creation flow (service + repository + DB)
- [ ] Authentication flow (auth service + user service + DB)
- [ ] User updates (service + repository + DB)
- [ ] Filtering and pagination (repository + DB)
- [ ] Transaction handling
- [ ] Constraint violations (email uniqueness)

### E2E Tests
- [ ] Complete registration → login → profile workflow
- [ ] Password change workflow
- [ ] Admin user management workflow
- [ ] Error scenarios (invalid credentials, unauthorized access)
- [ ] Token expiration handling

### Database Tests
- [ ] Repository CRUD operations
- [ ] Query filtering
- [ ] Pagination
- [ ] Database constraints
- [ ] Transaction rollback

---

## 🎨 Test Data Management

### Factories (Better than fixtures)
```python
# tests/factories.py
class UserFactory:
    @staticmethod
    def create(db, **kwargs):
        defaults = {
            "email": f"user{uuid.uuid4()}@example.com",
            "full_name": "Test User",
            "password": "TestPass123!",
            "role": UserRole.USER,
            "is_active": True
        }
        defaults.update(kwargs)
        return user_service.create_user(UserCreate(**defaults))
    
    @staticmethod
    def build(**kwargs):
        # Build without saving to DB (for unit tests)
        ...
```

**Usage:**
```python
# Integration test - real DB
def test_with_real_user(db):
    user = UserFactory.create(db, email="specific@example.com")
    ...

# Unit test - mock object
def test_with_mock_user():
    user = UserFactory.build(email="mock@example.com")
    ...
```

---

## 🔄 Test Lifecycle

### Setup → Execute → Verify → Teardown

```python
def test_user_creation():
    # ARRANGE (Setup)
    db = get_test_db()
    service = UserService(UserRepository(db), PasswordService())
    user_data = UserCreate(...)
    
    # ACT (Execute)
    result = service.create_user(user_data)
    
    # ASSERT (Verify)
    assert result.email == user_data.email
    assert result.id is not None
    
    # TEARDOWN (automatic with fixtures)
    # db fixture auto-closes and rolls back
```

---

## 📈 Coverage Goals

| Layer | Target Coverage | Priority |
|-------|----------------|----------|
| Services | 90%+ | HIGH |
| Repositories | 85%+ | HIGH |
| API Endpoints | 85%+ | HIGH |
| DTOs/Validation | 90%+ | MEDIUM |
| Middleware | 75%+ | MEDIUM |
| Utilities | 80%+ | LOW |
| **Overall** | **80%+** | **REQUIRED** |

---

## 🚀 Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Fast tests only (unit)
pytest -m unit

# All but E2E
pytest -m "not e2e"

# Specific file
pytest tests/unit/test_user_service_unit.py

# Specific test
pytest tests/unit/test_user_service_unit.py::test_create_user

# Parallel execution
pytest -n auto

# Verbose with timing
pytest -v --durations=10

# Stop on first failure
pytest -x

# Re-run failed tests
pytest --lf
```

---

## 🎯 Best Practices

### ✅ DO:
1. **Keep unit tests fast** - Mock all I/O
2. **Use factories** - Don't duplicate test data creation
3. **Test one thing** - One assertion per test (when possible)
4. **Use descriptive names** - `test_create_user_with_duplicate_email_raises_conflict`
5. **Clean up after tests** - Use fixtures with teardown
6. **Use markers** - Categorize tests for selective running
7. **Test error cases** - Don't just test happy paths
8. **Keep E2E tests minimal** - They're slow and brittle

### ❌ DON'T:
1. **Don't share state** - Each test should be independent
2. **Don't use sleep()** - Use proper async/await or mocking
3. **Don't test framework code** - Trust FastAPI, SQLAlchemy work
4. **Don't mock what you're testing** - Only mock dependencies
5. **Don't write flaky tests** - Fix or remove them
6. **Don't skip tests** - Fix or delete them
7. **Don't test implementation** - Test behavior
8. **Don't mix test types** - Keep unit/integration/e2e separate

---

## 🔒 Security Testing

Include security tests:
```python
def test_sql_injection_attempt():
    # Test that malicious input is properly escaped
    ...

def test_xss_attempt():
    # Test that HTML/JS is properly escaped
    ...

def test_password_exposed_in_logs():
    # Verify passwords never appear in logs
    ...

def test_rate_limiting():
    # Test rate limiting works
    ...
```

---

**Next:** See actual test implementations in the refactored test files!

