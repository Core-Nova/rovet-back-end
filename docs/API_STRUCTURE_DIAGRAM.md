# API Structure Visualization

## 🔴 Current State (Problematic)

### File Structure
```
app/
├── controllers/                    ← 🔴 DUPLICATE LOCATION #1
│   ├── auth_controller.py         ← Defines /login, /register, /me
│   └── user_controller.py         ← Defines /users CRUD
│
├── api/
│   ├── deps.py                    ← ⚠️  Only has get_db, get_current_user
│   └── v1/
│       ├── endpoints/             ← 🔴 DUPLICATE LOCATION #2
│       │   ├── auth.py           ← ALSO defines /login, /register, /me
│       │   ├── users.py          ← ALSO defines /users CRUD
│       │   ├── health.py         ← Defines /health
│       │   └── metrics.py
│       └── api.py                ← ⚠️  Imports from BOTH controllers & endpoints
│
└── main.py                        ← 🔴 DUPLICATE LOCATION #3
    └── Lines 74-86               ← Defines / and /health (duplicate names!)
```

### Data Flow (Broken)
```
HTTP Request
    ↓
Which endpoint handles it? 🤷
    ├── controllers/auth_controller.py?
    ├── api/v1/endpoints/auth.py?
    └── main.py?
    ↓
❌ Controllers/Endpoints create services manually
    │
    └── UserService(db)  ← Hard-coded dependency
        └── Creates UserRepository(db) internally
        └── Creates PasswordService() internally
    ↓
❌ Some endpoints skip services entirely
    │
    └── Direct: db.query(User).filter(...).first()
    └── Direct: UserRepository(db)
```

### Problems Visualized

```
┌─────────────────────────────────────────────────┐
│  HTTP: GET /api/v1/auth/login                   │
└────────────────┬────────────────────────────────┘
                 │
         Which one runs? 🤷
                 │
    ┌────────────┼────────────┐
    │                         │
    ▼                         ▼
┌─────────────────┐   ┌─────────────────┐
│ controllers/    │   │ api/endpoints/  │
│ auth_controller │   │ auth.py         │
│                 │   │                 │
│ @router.post    │   │ @router.post    │
│ ("/login")      │   │ ("/login")      │
│                 │   │                 │
│ Creates:        │   │ Creates:        │
│ AuthService(db) │   │ AuthService(db) │
│                 │   │                 │
│ + Direct SQL!   │   │ + Direct SQL!   │
└─────────────────┘   └─────────────────┘

Result: Confusion, duplication, inconsistency
```

---

## 🟢 Target State (Clean)

### File Structure
```
app/
├── api/
│   ├── deps.py                    ← ✅ ALL dependency providers HERE
│   │   ├── get_db()
│   │   ├── get_password_service()
│   │   ├── get_user_repository()
│   │   ├── get_user_service()    ← ✅ NEW
│   │   ├── get_auth_service()    ← ✅ NEW
│   │   └── get_current_user()
│   │
│   └── v1/
│       ├── endpoints/             ← ✅ SINGLE LOCATION FOR ENDPOINTS
│       │   ├── auth.py           ← /login, /register, /me (uses DI)
│       │   ├── users.py          ← /users CRUD (uses DI)
│       │   ├── health.py         ← /health, /readyz
│       │   └── metrics.py
│       └── api.py                ← ✅ Imports ONLY from endpoints
│
├── services/                      ← ✅ Business logic layer
│   ├── auth_service.py           ← Accepts injected dependencies
│   ├── user_service.py           ← Accepts injected dependencies
│   └── password_service.py
│
├── repositories/                  ← ✅ Data access layer
│   └── user_repository.py
│
└── main.py                        ← ✅ Minimal (just / root)
```

### Data Flow (Clean)
```
HTTP Request
    ↓
✅ Single source of truth
    ↓
api/v1/endpoints/auth.py
    ↓
@router.post("/login")
def login(
    auth_service: AuthService = Depends(get_auth_service)  ← ✅ INJECTED
):
    return auth_service.authenticate(...)
    ↓
    │
    ▼
deps.get_auth_service()  ← ✅ Dependency provider
    │
    ├── Creates AuthService with:
    │   ├── db (from get_db)
    │   └── UserService (from get_user_service)
    │       ├── UserRepository (from get_user_repository)
    │       └── PasswordService (from get_password_service)
    │
    └── Returns fully configured AuthService
    ↓
AuthService.authenticate()  ← ✅ Business logic
    ↓
UserRepository.get_by_email()  ← ✅ Data access
    ↓
Database
```

### Clean Architecture Visualized

```
┌──────────────────────────────────────────────────┐
│  HTTP: GET /api/v1/auth/login                    │
└────────────────┬─────────────────────────────────┘
                 │
         One clear path ✅
                 │
                 ▼
┌────────────────────────────────────────────────┐
│  api/v1/endpoints/auth.py                      │
│                                                 │
│  @router.post("/login")                        │
│  def login(                                     │
│      auth_service: AuthService = Depends(...)  │ ← Dependency Injection
│  ):                                             │
│      return auth_service.authenticate(...)     │
└────────────────┬───────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────┐
│  api/deps.py                                    │
│                                                 │
│  def get_auth_service(...) -> AuthService:     │
│      user_service = Depends(get_user_service)  │
│      return AuthService(db, user_service)      │
└────────────────┬───────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────┐
│  services/auth_service.py                      │
│                                                 │
│  class AuthService:                            │
│      def __init__(self, db, user_service):     │ ← Accepts dependencies
│          self.db = db                          │
│          self.user_service = user_service      │
│                                                 │
│      def authenticate(self, email, password):  │ ← Business logic
│          user = self.user_service.get_by...    │
└────────────────┬───────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────┐
│  repositories/user_repository.py               │
│                                                 │
│  class UserRepository:                         │
│      def get_by_email(self, email):           │ ← Data access only
│          return self.db.query(...).first()    │
└────────────────┬───────────────────────────────┘
                 │
                 ▼
            Database

Result: Clear, testable, maintainable
```

---

## 📊 Side-by-Side Comparison

### Endpoint Definition

#### ❌ Before (Duplicate + Manual Instantiation)
```python
# File: controllers/auth_controller.py
@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)  # ❌ Manual creation
    return auth_service.authenticate_user(...)

# File: api/v1/endpoints/auth.py
@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(deps.get_db)):
    auth_service = AuthService(db)  # ❌ Duplicate + Manual creation
    return auth_service.authenticate_user(...)
```

#### ✅ After (Single + Dependency Injection)
```python
# File: api/v1/endpoints/auth.py (ONLY location)
@router.post("/login")
def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)  # ✅ Injected
):
    return auth_service.authenticate_user(...)
```

### Service Constructor

#### ❌ Before (Creates Own Dependencies)
```python
# File: services/user_service.py
class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)      # ❌ Creates repository
        self.password_service = PasswordService() # ❌ Creates password service
```

#### ✅ After (Dependencies Injected)
```python
# File: services/user_service.py
class UserService:
    def __init__(
        self,
        repository: UserRepository,          # ✅ Injected
        password_service: PasswordService    # ✅ Injected
    ):
        self.repository = repository
        self.password_service = password_service
```

### Testing

#### ❌ Before (Hard to Test)
```python
def test_login(client):
    # Can't mock AuthService because it's created inside endpoint
    response = client.post("/api/v1/auth/login", json={...})
    # Must use real AuthService, UserService, UserRepository, Database
```

#### ✅ After (Easy to Test)
```python
def test_login(client, mock_auth_service):
    # Override dependency with mock
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    
    response = client.post("/api/v1/auth/login", json={...})
    
    # Verify mock was called correctly
    mock_auth_service.authenticate_user.assert_called_once()
```

---

## 🎯 Migration Path

### Phase 1: Add Dependency Providers
```
deps.py (before)        deps.py (after)
───────────────         ─────────────────────────────────
get_db() ────────→      get_db()
get_current_user()      get_current_user()
                        get_password_service()        ← NEW
                        get_user_repository()         ← NEW
                        get_user_service()            ← NEW
                        get_auth_service()            ← NEW
```

### Phase 2: Refactor Services
```
UserService (before)    UserService (after)
────────────────────    ────────────────────────────────
__init__(db):           __init__(repository, password_service):
  repo = UserRepo(db)     self.repository = repository
  pwd = PwdService()      self.password_service = password_service
```

### Phase 3: Consolidate Endpoints
```
Before:                 After:
───────────────────     ─────────────────────────────
controllers/            [DELETED]
  auth_controller.py    
  user_controller.py    

api/v1/endpoints/       api/v1/endpoints/
  auth.py (partial)  →    auth.py (unified, uses DI)
  users.py (partial) →    users.py (unified, uses DI)
  health.py          →    health.py (fixed duplicates)
```

### Phase 4: Update Tests
```
Before:                 After:
───────────────────     ─────────────────────────────
Tests use real          Tests use dependency overrides
services & DB           with mocks

def test_x(client):     def test_x(client, mock_service):
  response = ...          app.dependency_overrides[...] = ...
                          response = ...
                          mock_service.method.assert_called()
```

---

## 🔄 Request Flow Comparison

### ❌ Current (Confusing)
```
User Request
    ↓
FastAPI Router
    ↓
    ├──→ controllers/auth_controller.py?
    ├──→ api/v1/endpoints/auth.py?
    └──→ main.py?
         ↓ (which one wins?)
         Endpoint
         ↓
         Creates: AuthService(db)
         ↓
         AuthService.__init__(db):
           Creates: UserService(db)
           ↓
           UserService.__init__(db):
             Creates: UserRepository(db)
             Creates: PasswordService()
```

### ✅ Target (Clear)
```
User Request
    ↓
FastAPI Router
    ↓
api/v1/endpoints/auth.py (ONLY location)
    ↓
Depends(get_auth_service)
    ↓
deps.get_auth_service():
  ├─→ Depends(get_db) → database session
  └─→ Depends(get_user_service):
      ├─→ Depends(get_user_repository):
      │   └─→ Depends(get_db)
      └─→ Depends(get_password_service)
    ↓
Returns fully configured AuthService
    ↓
Endpoint executes business logic
```

---

## 📈 Metrics

### Code Duplication

#### Before
```
/login endpoint:        2 implementations (controllers + endpoints)
/register endpoint:     2 implementations
/me endpoint:           2 implementations
/users/ endpoint:       2 implementations
/users/{id} endpoint:   2 implementations
/health endpoint:       3 implementations (main.py x2 + endpoints)
─────────────────────────────────────────────────────────────────
Total duplications:     13 duplicate definitions
```

#### After
```
Each endpoint:          1 implementation (in endpoints only)
─────────────────────────────────────────────────────────────────
Total duplications:     0
```

### Testability

#### Before
```
Mock requirements:      Can't mock services (created internally)
Test type:              Integration tests only (need real DB)
Test speed:             Slow (database operations)
Test complexity:        High (complex setup)
```

#### After
```
Mock requirements:      Easy (override dependencies)
Test type:              True unit tests possible
Test speed:             Fast (no database)
Test complexity:        Low (simple mocking)
```

---

## 🎓 Learning Resources

### Key Concepts

1. **Dependency Injection**: Framework provides dependencies instead of manual creation
2. **Single Responsibility**: Each file/class has one job
3. **Separation of Concerns**: Clear boundaries between layers
4. **Don't Repeat Yourself (DRY)**: No duplicate code

### FastAPI Patterns

- **Dependency providers**: Functions that return configured instances
- **Depends()**: FastAPI's dependency injection mechanism
- **Router organization**: One router per resource
- **Testing with overrides**: `app.dependency_overrides[provider] = mock`

---

**Next Steps:** See `docs/API_REFACTORING_PLAN.md` for detailed implementation guide!

