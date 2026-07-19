# How to Test Your API — Complete Guide

Your BioHub API is ready for testing. Choose your preferred method below.

---

## Option 1: Run Automated Test Script (Recommended)

### On Windows:
```bash
test_all_endpoints.bat
```

Runs all 8 tests in sequence with pauses between each.

### On macOS/Linux:
```bash
bash test_all_endpoints.sh
```

---

## Option 2: Manual Testing with curl

### Prerequisites
- Service running: `uvicorn main:app --reload`
- `curl` installed (or use PowerShell on Windows)

### Quick Test (30 seconds)

```bash
# 1. Check health
curl http://localhost:8000/health

# 2. Create record
curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d '{"identificacion_basica":{"id_registro":"QUICK-TEST"},"geolocalizacion":{"nivel_sensibilidad":"RESTRICTED"},"informacion_registro":{"investigador":"test@org"}}'

# 3. Query results
curl http://localhost:8000/auditoria/historial/QUICK-TEST
```

---

## Option 3: Interactive Browser Testing (Swagger UI)

### Steps:
1. Make sure service is running: `uvicorn main:app --reload`
2. Open browser: `http://localhost:8000/docs`
3. Expand each endpoint (click the arrow)
4. Click "Try it out"
5. Fill in parameters
6. Click "Execute"
7. See response below

### Endpoints to test:
- `GET /health` → Click Execute (no parameters needed)
- `POST /dev/simulate` → Paste JSON body, click Execute
- `GET /auditoria/historial/{id}` → Enter your id_registro
- `GET /auditoria/metadatos/{id}` → Enter your id_registro
- `GET /auditoria/sensibilidad/{id}` → Enter your id_registro
- `GET /aprobacion/{id}` → Enter your id_registro
- `POST /aprobacion/actualizar` → Paste JSON body, click Execute

---

## Option 4: Postman/Insomnia Import

### Create new requests manually:

**Collection: BioHub API Tests**

| # | Method | Endpoint | Body |
|---|---|---|---|
| 1 | GET | http://localhost:8000/health | - |
| 2 | POST | http://localhost:8000/dev/simulate | [See below](#test-data) |
| 3 | GET | http://localhost:8000/auditoria/historial/{{id}} | - |
| 4 | GET | http://localhost:8000/auditoria/metadatos/{{id}} | - |
| 5 | GET | http://localhost:8000/auditoria/sensibilidad/{{id}} | - |
| 6 | GET | http://localhost:8000/aprobacion/{{id}} | - |
| 7 | POST | http://localhost:8000/aprobacion/actualizar | [See below](#approval-update) |

### Environment Variables (in Postman):
```
base_url: http://localhost:8000
id_registro: REG-TEST-001
```

---

## Test Data

### For POST /dev/simulate (Create Record)

**Minimal version** (quickest):
```json
{
  "identificacion_basica": {
    "id_registro": "TEST-001",
    "nombre_cientifico": "Panthera onca"
  },
  "geolocalizacion": {
    "latitud": 5.52,
    "nivel_sensibilidad": "RESTRICTED"
  },
  "informacion_registro": {
    "investigador": "test@example.org"
  }
}
```

**Full version** (recommended):
See `TESTING_GUIDE.md` for complete sample record.

---

## Expected Results

### Test 1: Health Check
```json
{
  "status": "ok",
  "service": "biohub-change-management",
  "db": "connected",
  "cache": "memory",
  "kafka": "mock",
  "environment": "development"
}
```

### Test 2: Create Record
```json
{
  "status": "ok",
  "id_registro": "TEST-001",
  "version": 1,
  "timestamp": "2026-04-19T15:30:00.123456"
}
```

### Test 3: Get History
```json
[
  {
    "id_registro": "TEST-001",
    "version": 1,
    "timestamp": "2026-04-19T15:30:00.123456",
    "usuario": "test@example.org",
    "sensibilidad": "RESTRICTED",
    "estado_aprobacion": "PENDIENTE"
  }
]
```

### Test 4: Get Sensitivity
```json
{
  "id_registro": "TEST-001",
  "sensibilidad": "RESTRICTED"
}
```

### Test 5: Get Approval (Initial)
```json
{
  "id_registro": "TEST-001",
  "estado_aprobacion": "PENDIENTE"
}
```

---

## Approval Update

### For POST /aprobacion/actualizar

```json
{
  "id_registro": "TEST-001",
  "nuevo_estado": "EN_REVISION",
  "director_aprobador": "director@institute.org",
  "comentarios": "Enviado para revisión"
}
```

Expected response:
```json
{
  "status": "ok",
  "id_registro": "TEST-001",
  "version": 2,
  "nuevo_estado": "EN_REVISION",
  "timestamp": "2026-04-19T15:35:00.123456"
}
```

After this, query `/aprobacion/TEST-001` again → should return `"estado_aprobacion": "EN_REVISION"`

---

## Complete Test Sequence

Run these in order:

```bash
# 1. Health check
curl http://localhost:8000/health | jq

# 2. Create TEST-WORKFLOW record
curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d '{"identificacion_basica":{"id_registro":"TEST-WORKFLOW"},"geolocalizacion":{"nivel_sensibilidad":"PUBLIC"},"informacion_registro":{"investigador":"scientist@org"}}'

# 3. Get initial history (should show 1 entry, PENDIENTE)
curl http://localhost:8000/auditoria/historial/TEST-WORKFLOW | jq

# 4. Get metadata
curl http://localhost:8000/auditoria/metadatos/TEST-WORKFLOW | jq

# 5. Get sensitivity
curl http://localhost:8000/auditoria/sensibilidad/TEST-WORKFLOW | jq

# 6. Get initial approval status
curl http://localhost:8000/aprobacion/TEST-WORKFLOW | jq

# 7. Update to EN_REVISION
curl -X POST http://localhost:8000/aprobacion/actualizar \
  -H "Content-Type: application/json" \
  -d '{"id_registro":"TEST-WORKFLOW","nuevo_estado":"EN_REVISION","director_aprobador":"reviewer@org","comentarios":"In review"}' | jq

# 8. Check approval changed
curl http://localhost:8000/aprobacion/TEST-WORKFLOW | jq

# 9. Update to APROBADO
curl -X POST http://localhost:8000/aprobacion/actualizar \
  -H "Content-Type: application/json" \
  -d '{"id_registro":"TEST-WORKFLOW","nuevo_estado":"APROBADO","director_aprobador":"director@org","comentarios":"Approved"}' | jq

# 10. Final history (should show 3 entries)
curl http://localhost:8000/auditoria/historial/TEST-WORKFLOW | jq '.[] | {version, estado_aprobacion}'
```

---

## Verify in MongoDB

After testing, verify data was stored:

```javascript
// Connect to MongoDB Compass or mongosh

// Show all audit entries for your test record
db.audit_entries.find({ id_registro: "TEST-WORKFLOW" }).pretty()

// Show the latest snapshot
db.biological_records.findOne({ id_registro: "TEST-WORKFLOW" })

// Count total records created
db.biological_records.countDocuments()

// Count total audit entries (should be 3 if you did all updates)
db.audit_entries.countDocuments()
```

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `curl: command not found` | Install curl or use PowerShell: `Invoke-WebRequest` |
| `Connection refused` | Service not running. Run `uvicorn main:app --reload` |
| `404 Not Found` | Record doesn't exist. Create one with `/dev/simulate` first |
| `"db": "error"` in health | Check MongoDB URI in `.env` |
| Slow first request | Normal (cold start). Second request cached. |
| Empty response from POST | Check JSON format in request body |

---

## What Each Endpoint Does

| Endpoint | Purpose | For Group 3? |
|---|---|---|
| `GET /health` | Verify service is running | Testing only |
| `POST /dev/simulate` | Create mock audit entries | Development only |
| `GET /auditoria/historial/{id}` | Get full change history | **YES** |
| `GET /auditoria/metadatos/{id}` | Get record metadata | **YES** |
| `GET /auditoria/sensibilidad/{id}` | Get sensitivity level | **YES** |
| `GET /aprobacion/{id}` | Get approval status | **YES** |
| `POST /aprobacion/actualizar` | Update approval state | **YES** |

---

## Performance Expectations

- **First request:** 30-100ms (MongoDB cold start)
- **Cached request:** <5ms
- **Cache TTL:** 60s for history, 300s for metadata

---

## Next Steps

1. ✓ Test all endpoints locally
2. ✓ Verify data in MongoDB
3. → Deploy to staging
4. → Share API documentation with Group 3
5. → Group 3 starts integration via REST endpoints

---

## For Detailed Info

- **Architecture:** See `README.md`
- **Setup:** See `QUICK_START.md`
- **All Endpoints:** See `ENDPOINTS_REFERENCE.md`
- **Full Examples:** See `TESTING_GUIDE.md`

---

**Ready to test? Start with the automated script or Swagger UI at `/docs`** 🚀
