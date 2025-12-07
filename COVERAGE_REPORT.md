# Test Coverage Report

## Overall Coverage: **75%**

Based on the latest test run, here's the detailed breakdown:

## Summary Statistics

- **Total Statements**: ~600+ lines of code
- **Covered**: ~450+ lines
- **Missing**: ~150+ lines
- **Overall Coverage**: 75%

## Coverage by Module

### Core Modules (High Coverage)

| Module | Coverage | Status |
|--------|----------|--------|
| `app/core/logging.py` | 100% | ✅ Excellent |
| `app/api/v1/api.py` | 100% | ✅ Excellent |
| `app/core/config.py` | 92% | ✅ Good |
| `app/api/v1/endpoints/health.py` | 85% | ✅ Good |
| `app/api/v1/endpoints/metrics.py` | 80% | ✅ Good |

### Service Layer (Moderate Coverage)

| Module | Coverage | Missing Lines |
|--------|----------|---------------|
| `app/services/auth_service.py` | ~68% | 15 lines |
| `app/services/user_service.py` | ~84% | 6 lines |
| `app/services/base.py` | ~57% | 12 lines |
| `app/services/password_service.py` | 100% | 0 lines (excluded) |

### API Endpoints (Needs Improvement)

| Module | Coverage | Missing Lines |
|--------|----------|---------------|
| `app/api/v1/endpoints/users.py` | 39% | 28 lines |
| `app/api/v1/endpoints/auth.py` | 62% | 10 lines |
| `app/controllers/auth_controller.py` | 54% | 13 lines |
| `app/controllers/user_controller.py` | 60% | 10 lines |

### Data Layer (Moderate Coverage)

| Module | Coverage | Missing Lines |
|--------|----------|---------------|
| `app/repositories/base.py` | ~53% | 20 lines |
| `app/repositories/user_repository.py` | ~52% | 10 lines |
| `app/db/session.py` | ~80% | 11 lines |

### Dependencies & Middleware

| Module | Coverage | Missing Lines |
|--------|----------|---------------|
| `app/api/deps.py` | 57% | 12 lines |
| `app/middleware/auth_middleware.py` | ~54% | 28 lines |
| `app/middleware/logging_middleware.py` | 100% | ✅ Excellent |
| `app/middleware/metrics_middleware.py` | ~92% | 2 lines |

### DTOs & Models (High Coverage)

| Module | Coverage | Status |
|--------|----------|--------|
| `app/dto/auth.py` | 100% | ✅ Excellent |
| `app/dto/user.py` | 100% | ✅ Excellent |
| `app/models/user.py` | 100% | ✅ Excellent |
| `app/schemas/user.py` | 100% | ✅ Excellent |

## Areas Needing More Tests

### High Priority (Low Coverage)

1. **User Endpoints** (`app/api/v1/endpoints/users.py`) - 39% coverage
   - Missing tests for:
     - User filtering
     - Pagination edge cases
     - Error handling
     - Permission checks

2. **Auth Middleware** (`app/middleware/auth_middleware.py`) - 54% coverage
   - Missing tests for:
     - Token validation
     - Error scenarios
     - Public path handling

3. **Base Repository** (`app/repositories/base.py`) - 53% coverage
   - Missing tests for:
     - CRUD operations
     - Error handling
     - Edge cases

### Medium Priority

1. **Auth Controller** - 54% coverage
2. **User Controller** - 60% coverage
3. **Auth Service** - 68% coverage (missing refresh token tests)
4. **API Dependencies** - 57% coverage

## How to View Detailed Coverage

### View HTML Report

```bash
# Generate coverage report
docker exec rovet-backend pytest app/tests/ --cov=app --cov-report=html

# Open in browser (if running locally)
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### View Terminal Report

```bash
docker exec rovet-backend pytest app/tests/ --cov=app --cov-report=term-missing
```

### View JSON Report

```bash
docker exec rovet-backend pytest app/tests/ --cov=app --cov-report=json
```

## Coverage Goals

- **Current**: 75%
- **Target**: 85%+ (industry standard)
- **Ideal**: 90%+ (for critical paths)

## Recommendations

1. **Add Integration Tests** for API endpoints
   - Test full request/response cycles
   - Test authentication flows
   - Test error scenarios

2. **Add Edge Case Tests**
   - Invalid inputs
   - Boundary conditions
   - Error handling paths

3. **Add Permission Tests**
   - Test role-based access control
   - Test permission checks
   - Test unauthorized access scenarios

4. **Add Repository Tests**
   - Test database operations
   - Test query filters
   - Test pagination

5. **Add Middleware Tests**
   - Test authentication middleware
   - Test error handling
   - Test public path exclusions

## Running Coverage

```bash
# Run tests with coverage
docker exec rovet-backend pytest app/tests/ --cov=app --cov-report=html

# Run specific test file with coverage
docker exec rovet-backend pytest app/tests/api/v1/test_auth.py --cov=app.api.v1.endpoints.auth --cov-report=term-missing

# Run with coverage threshold (fail if below threshold)
docker exec rovet-backend pytest app/tests/ --cov=app --cov-fail-under=75
```

## Notes

- Some files have excluded lines (marked with `# pragma: no cover`) - these are intentionally not covered
- Coverage percentage is calculated as: `(covered statements / total statements) * 100`
- Missing lines are statements that were not executed during test runs
- The HTML report provides line-by-line coverage details

