# BioHub API Documentation Index

## Quick Navigation

### 🚀 Just Getting Started?
→ **[START_HERE.md](START_HERE.md)** — 3-minute overview + testing options

### 📖 Documentation

| Document | Best For |
|---|---|
| [START_HERE.md](START_HERE.md) | Quick start (3 min) |
| [HOW_TO_TEST.md](HOW_TO_TEST.md) | Testing guide with 4 methods |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | Detailed examples for each endpoint |
| [ENDPOINTS_REFERENCE.md](ENDPOINTS_REFERENCE.md) | Quick API reference card |
| [README.md](README.md) | Architecture & project overview |
| [QUICK_START.md](QUICK_START.md) | 5-minute setup walkthrough |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Full technical summary |

### 🧪 Test Scripts

| Script | Platform |
|---|---|
| `test_all_endpoints.sh` | Linux / macOS |
| `test_all_endpoints.bat` | Windows |

Run these to automatically test all 7 endpoints.

### 📁 Project Structure

```
biohub-datamanager/
├── main.py                    # FastAPI app
├── config.py                  # Settings from .env
├── requirements.txt           # Dependencies
├── .env                       # Credentials
├── .gitignore                 # Git ignore rules
│
├── database/
│   ├── connection.py          # MongoDB async client
│   └── models.py              # Pydantic models
│
├── services/
│   ├── audit_service.py       # Audit trail logic
│   ├── sensitivity_service.py # Classification
│   └── approval_service.py    # Workflow state machine
│
├── routers/
│   ├── auditoria.py           # Audit endpoints
│   └── aprobacion.py          # Approval endpoints
│
├── kafka_service/
│   ├── consumer.py            # Kafka consumer
│   └── mock_producer.py       # Mock for testing
│
├── cache/
│   └── cache.py               # Redis/in-memory
│
└── Documentation/
    ├── INDEX.md               # This file
    ├── START_HERE.md          # Quick start ← BEGIN HERE
    ├── HOW_TO_TEST.md         # Testing methods
    ├── TESTING_GUIDE.md       # Full examples
    ├── ENDPOINTS_REFERENCE.md # API quick ref
    ├── README.md              # Architecture
    ├── QUICK_START.md         # Setup guide
    └── PROJECT_SUMMARY.md     # Technical summary
```

## The 7 Endpoints

### Create/Test (Development Only)
- `POST /dev/simulate` — Inject mock biological record

### Audit Trail (for Group 3)
- `GET /auditoria/historial/{id}` — Full change history
- `GET /auditoria/metadatos/{id}` — Record metadata
- `GET /auditoria/sensibilidad/{id}` — Sensitivity level

### Approval Workflow (for Group 3)
- `GET /aprobacion/{id}` — Current approval status
- `POST /aprobacion/actualizar` — Update approval

### System
- `GET /health` — Service status
- `GET /` — Service info

## Technology Stack

- **FastAPI** 0.136.0 — Web framework
- **Motor** 3.3.2 — Async MongoDB
- **aiokafka** 0.10.0 — Async Kafka
- **Redis** 5.2.0 — Cache (optional)
- **Pydantic** 2.13.2 — Data validation
- **deepdiff** 9.0.0 — Field-level diff

## Getting Started

### 1. Start the service:
```bash
uvicorn main:app --reload
```

### 2. Choose a testing method:

**Option A: Browser (Easiest)**
- Open: http://localhost:8000/docs
- Click endpoint → "Try it out" → "Execute"

**Option B: Automated (Fastest)**
- Windows: `test_all_endpoints.bat`
- Linux: `bash test_all_endpoints.sh`

**Option C: Manual curl (Learn more)**
- See [HOW_TO_TEST.md](HOW_TO_TEST.md) for examples

**Option D: Postman**
- Import from `/openapi.json`

### 3. Check your data in MongoDB:
```javascript
db.audit_entries.find({ id_registro: "YOUR-ID" }).pretty()
```

## Key Features

✓ **Immutable audit trail** — All changes versioned, nothing deleted
✓ **Field tracking** — Sees exact changes (old value → new value)
✓ **Sensitivity levels** — PUBLIC / RESTRICTED / CONFIDENTIAL
✓ **Approval workflow** — 4-state machine with full audit trail
✓ **High performance** — Async throughout, caching enabled
✓ **Production ready** — Full error handling, logging, monitoring hooks

## Integration

### Group 3 (API Consumers)

Group 3 can call these endpoints:
```
GET  /auditoria/historial/{id}       → Full audit trail
GET  /auditoria/metadatos/{id}       → Metadata only
GET  /auditoria/sensibilidad/{id}    → Sensitivity classification
GET  /aprobacion/{id}                → Approval status
POST /aprobacion/actualizar          → Update approval
```

Interactive documentation at: `/docs`

### Group 1 (Data Producers)

When ready, configure:
```env
USE_MOCK_KAFKA=false
KAFKA_BOOTSTRAP_SERVERS=group1-broker:9092
KAFKA_TOPIC=registros-biologicos
```

Service will consume from `registros-biologicos` topic.

## Status

✓ **Backend:** Complete and tested
✓ **Documentation:** Comprehensive
✓ **Tests:** Automated scripts included
✓ **Database:** Configured and connected
✓ **API:** Ready for Group 3 integration
✓ **Kafka:** Mock enabled, real consumer ready

## Next Steps

1. **Test locally:** Follow [START_HERE.md](START_HERE.md)
2. **Verify MongoDB:** Check your data appears
3. **Share with Group 3:** Give them `/docs` endpoint
4. **Deploy:** Move to production when ready
5. **Connect Group 1:** When Kafka ready, update `.env`

---

**Ready? Start with [START_HERE.md](START_HERE.md)** 🚀
