# Quick Reference Card

## 🚀 Essential Commands

### Start/Stop Services
```bash
make up              # Start all services
make down            # Stop all services
make restart         # Restart services
make logs            # View logs
```

### Testing
```bash
make test                           # Run all tests with coverage
open htmlcov/index.html            # View coverage report (macOS)
pytest -k "auth"                   # Run tests matching pattern
pytest -x                          # Stop on first failure
pytest -v                          # Verbose output
```

### Code Quality
```bash
make format          # Auto-format code (black + isort)
make lint            # Run all linters
```

### Database
```bash
make migrate         # Run migrations
make seed            # Seed database with test data
```

### Development
```bash
make shell           # Open shell in API container
make clean           # Remove all containers & data ⚠️
```

---

## 📍 Access Points

| Service | URL |
|---------|-----|
| API Docs | http://localhost:8001/api/docs |
| Health Check | http://localhost:8001/ |
| Metrics | http://localhost:8001/api/metrics |

---

## 🧪 Test Commands

| Command | Purpose |
|---------|---------|
| `make test` | Run all tests |
| `pytest app/tests/api/` | Test specific directory |
| `pytest -k "login"` | Test by name pattern |
| `pytest -x` | Stop on first failure |
| `pytest -s` | Show print statements |
| `pytest --pdb` | Debug on failure |
| `pytest --durations=10` | Show slowest tests |

---

## 📊 Coverage

```bash
# Generate reports
make test

# View HTML report
open htmlcov/index.html

# Terminal report with missing lines
pytest --cov-report=term-missing
```

**Target:** ≥80% overall coverage

---

## 🔐 Default Credentials

**Admin:**
- Email: `admin@rovet.io`
- Password: `admin123`

**Regular Users:**
- Email: `kamen@rovet.io`, `tsetso@rovet.io`, etc.
- Password: `user123`

---

## 🐳 Docker Commands

```bash
docker-compose up -d              # Start in background
docker-compose logs -f api        # Follow API logs
docker-compose exec api sh        # Shell into container
docker-compose ps                 # List containers
docker-compose down -v            # Stop & remove volumes ⚠️
```

---

## 📁 Project Structure

```
app/
├── api/              # Endpoints & routes
│   ├── deps.py      # Dependencies
│   └── v1/          # API v1
├── services/         # Business logic
├── repositories/     # Data access
├── models/          # Database models
├── schemas/         # Pydantic schemas
├── dto/             # Data transfer objects
├── core/            # Config & utilities
├── middleware/      # Custom middleware
└── tests/           # Test suite
```

---

## 🔄 Development Workflow

```bash
# 1. Start services
make up

# 2. Run migrations
make migrate

# 3. Seed database (first time)
make seed

# 4. Make code changes...

# 5. Run tests
make test

# 6. Format & lint
make format
make lint

# 7. View coverage
open htmlcov/index.html

# 8. Commit changes
git add .
git commit -m "Your message"
git push
```

---

## 🔍 Debugging

```bash
# View logs
make logs
docker-compose logs -f api

# Shell access
make shell

# Python REPL
docker-compose exec api python

# Run single test with debug
pytest -s -vv app/tests/api/v1/test_auth.py::test_login_success
```

---

## 📝 API Testing (curl)

```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@rovet.io","password":"admin123"}' \
  | jq -r '.access_token')

# List users
curl http://localhost:8001/api/v1/users/ \
  -H "Authorization: Bearer $TOKEN"

# Create user
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "new@example.com",
    "password": "Password123!",
    "full_name": "New User"
  }'
```

---

## 🚨 Common Issues

| Problem | Solution |
|---------|----------|
| Import errors | `docker-compose exec api poetry install` |
| Database issues | `docker-compose down -v && make up && make migrate` |
| Port in use | `lsof -ti:8001 \| xargs kill -9` (macOS/Linux) |
| Tests fail | `docker-compose restart api && make test` |
| Coverage missing | `pytest --cov=app --cov-report=html` |

---

## 📚 Documentation

- **README.md** - Full project documentation
- **docs/TESTING_GUIDE.md** - Comprehensive testing guide
- **docs/PROPOSAL_DEPENDENCY_INJECTION.md** - DI refactoring proposal
- **API Docs** - http://localhost:8001/api/docs (when running)

---

## ⚡ Pro Tips

1. **Use Make** - All common tasks have Make shortcuts
2. **Watch Logs** - `make logs` in a separate terminal
3. **Test Early** - Run `make test` before committing
4. **Coverage First** - Check coverage report before PR
5. **Format Always** - Run `make format` before commit
6. **Read Errors** - Pytest errors are usually very clear

---

## 🎯 Quick Checklist Before Commit

- [ ] `make test` - All tests pass
- [ ] `make lint` - No linting errors
- [ ] `make format` - Code formatted
- [ ] Coverage ≥80% - Check `htmlcov/index.html`
- [ ] Tests for new features - Write tests first
- [ ] Docs updated - If adding new features

---

**💡 Need Help?**

1. Check logs: `make logs`
2. Check test output: `make test`
3. Check API docs: http://localhost:8001/api/docs
4. Read full docs: `README.md` and `docs/TESTING_GUIDE.md`


