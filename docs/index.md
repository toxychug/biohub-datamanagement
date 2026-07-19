# BioHub Change Management & Audit Service

**Production-ready microservice for biological record tracking, change auditing, and approval workflows.**

---

## 🚀 Quick Links

| Document | Purpose |
|----------|---------|
| [START_HERE.md](START_HERE.md) | **Begin here** — Project overview and setup |
| [QUICK_START.md](QUICK_START.md) | Get running in 5 minutes |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Technical architecture overview |
| [IN_MEMORY_QUICKSTART.md](IN_MEMORY_QUICKSTART.md) | Run without MongoDB |

---

## 📚 Documentation Sections

### Getting Started
- [START_HERE.md](START_HERE.md) — Introduction and project goals
- [QUICK_START.md](QUICK_START.md) — Installation and first run
- [HOW_TO_TEST.md](HOW_TO_TEST.md) — Testing guide and endpoints

### API Reference
- [ENDPOINTS_REFERENCE.md](ENDPOINTS_REFERENCE.md) — Complete API documentation
- [MOCK_INPUT_SPECS.md](MOCK_INPUT_SPECS.md) — Mock Kafka input form specification

### Advanced Topics
- [IN_MEMORY_DATABASE.md](IN_MEMORY_DATABASE.md) — In-memory database implementation details
- [IN_MEMORY_QUICKSTART.md](IN_MEMORY_QUICKSTART.md) — Running without MongoDB
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) — Detailed project specification
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) — Technical implementation notes
- [RUN_TESTS.md](RUN_TESTS.md) — Test suite and validation

---

## 🏗️ Technology Stack

- **FastAPI** 0.100+ — Async REST API framework
- **Motor** — Async MongoDB driver with in-memory fallback
- **aiokafka** — Kafka event consumer with mock mode
- **Alpine.js** — Frontend interactivity
- **Docker** — Containerized deployment
- **GitHub Actions** — CI/CD pipeline

---

## 🎯 Key Features

✅ **Change Auditing** — Immutable audit trail for all biological record modifications  
✅ **Approval Workflow** — Multi-stage approval system for sensitive data  
✅ **Kafka Integration** — Event-driven record processing  
✅ **In-Memory Fallback** — Works without MongoDB (development mode)  
✅ **Spanish UI** — Full Spanish language mock input form  
✅ **Redis Caching** — Optional Redis with in-memory fallback  
✅ **Docker Support** — Complete docker-compose.yml for full stack  
✅ **GitHub Actions CI/CD** — Automated testing on push/PR  

---

## 📦 Project Structure

```
biohub-datamanagement/
├── main.py                    # FastAPI application entry
├── config.py                  # Environment configuration
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Full stack orchestration
├── .github/workflows/         # GitHub Actions CI/CD
├── database/                  # Database layer
│   ├── connection.py          # MongoDB/in-memory connection
│   ├── models.py              # Pydantic data models
│   ├── in_memory_db.py        # In-memory fallback implementation
│   └── db_seed.py             # Sample data seeding
├── routers/                   # API route handlers
│   ├── auditoria.py           # Audit endpoints
│   └── aprobacion.py          # Approval endpoints
├── services/                  # Business logic
├── kafka_service/             # Kafka consumer and mocking
├── static/                    # Frontend assets
│   ├── index.html             # Dashboard
│   └── mock-input.html        # Spanish mock input form
├── tests/                     # Test suite
└── docs/                      # Documentation
    └── index.md               # This page
```

---

## 🔗 Repository Links

- **GitHub**: https://github.com/toxychug/biohub-datamanagement
- **Main Branch**: Stable production-ready code
- **Dev Branch**: Active development

---

## 📋 Environment Setup

See [QUICK_START.md](QUICK_START.md) for detailed setup instructions.

**Minimum requirements:**
- Python 3.8+
- Docker & Docker Compose (optional, for full stack)
- MongoDB (optional, app runs in-memory without it)

---

## ❓ Need Help?

1. Check the [QUICK_START.md](QUICK_START.md) guide
2. Review [HOW_TO_TEST.md](HOW_TO_TEST.md) for testing procedures
3. See [ENDPOINTS_REFERENCE.md](ENDPOINTS_REFERENCE.md) for API details
4. Check [IN_MEMORY_QUICKSTART.md](IN_MEMORY_QUICKSTART.md) if running without MongoDB

---

**Last Updated**: 2024 | Group 2 — BioHub Project
