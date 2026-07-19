# BioHub Change Management & Audit Microservice — Project Summary

**Status:** ✓ Complete & Ready to Deploy  
**Date:** 2026-04-19  
**Group:** 2 (Change Management & Audit)

---

## Deliverables

### REST API Endpoints (for Group 3)
- `GET /auditoria/historial/{id_registro}` — Change history (versioned)
- `GET /auditoria/metadatos/{id_registro}` — Record metadata
- `GET /auditoria/sensibilidad/{id_registro}` — Sensitivity classification
- `GET /aprobacion/{id_registro}` — Approval status
- `POST /aprobacion/actualizar` — Update approval workflow
- `GET /health` — Service health check
- `POST /dev/simulate` — Mock Kafka injection (development only)

### Core Features
- ✓ Immutable audit trail (append-only)
- ✓ Version control with field-level diffs
- ✓ Complete snapshot storage at each version
- ✓ Sensitivity classification (PUBLIC/RESTRICTED/CONFIDENTIAL)
- ✓ Approval workflow (4-state machine)
- ✓ Kafka consumer (real + mock)
- ✓ Redis cache (optional, with fallback)
- ✓ Full async/await architecture

---

## Technology Stack

| Component | Version | Purpose |
|---|---|---|
| **FastAPI** | 0.136.0 | Web framework |
| **Uvicorn** | 0.44.0 | ASGI server |
| **Motor** | 3.3.2 | Async MongoDB driver |
| **aiokafka** | 0.10.0 | Async Kafka consumer |
| **Redis** | 5.2.0 | Optional cache |
| **Pydantic** | 2.13.2 | Data validation |
| **deepdiff** | 9.0.0 | Field-level diffing |

---

## Project Structure (20 files)

```
biohub-datamanager/
├── .env + .env.example          # Credentials
├── config.py                    # Settings from .env
├── main.py                      # FastAPI entry point
├── requirements.txt             # Dependencies
├── README.md                    # Architecture guide
├── QUICK_START.md               # Setup walkthrough
├── PROJECT_SUMMARY.md           # This file
│
├── database/
│   ├── connection.py            # Async Motor client
│   └── models.py                # Pydantic models + enums
│
├── services/
│   ├── audit_service.py         # Core audit logic
│   ├── sensitivity_service.py   # Classification
│   └── approval_service.py      # Workflow state machine
│
├── routers/
│   ├── auditoria.py             # Audit endpoints (cached)
│   └── aprobacion.py            # Approval endpoints
│
├── kafka_service/
│   ├── consumer.py              # Async Kafka consumer
│   └── mock_producer.py         # Test injection
│
└── cache/
    └── cache.py                 # Redis/in-memory cache
```

---

## MongoDB Schema

### `audit_entries` (append-only)
```javascript
{
  id_registro: "REG-001",
  version: 1,
  timestamp: ISODate("2026-04-19T10:30:00Z"),
  usuario: "researcher@institute.org",
  ip_origen: "192.168.1.100",
  campos_modificados: [
    { campo: "geolocalizacion.latitud", valor_anterior: null, valor_nuevo: 5.52 }
  ],
  motivo: "Registro inicial",
  snapshot_completo: { /* full record */ },
  sensibilidad: "RESTRICTED",
  estado_aprobacion: "PENDIENTE"
}
```

Index: `{ id_registro: 1, version: -1 }`

### `biological_records` (upserted snapshots)
Latest version of each record, updated on each Kafka event.

---

## Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Configure
Edit `.env`:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=BiohubCluster
```

### 3. Run
```bash
uvicorn main:app --reload
```

### 4. Test
```bash
curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "identificacion_basica": { "id_registro": "TEST-001", "nombre_cientifico": "Panthera onca" },
    "geolocalizacion": { "latitud": 5.52, "nivel_sensibilidad": "RESTRICTED" },
    "informacion_registro": { "investigador": "test@example.com" }
  }'
```

### 5. Query
```bash
curl http://localhost:8000/auditoria/historial/TEST-001
```

See **QUICK_START.md** for full walkthrough.

---

## Integration

### Group 1 → Group 2
- **Channel:** Kafka topic `registros-biologicos`
- **Action:** Each message creates a new audit entry

### Group 2 → Group 3
- **Channel:** REST API (`/auditoria/*`, `/aprobacion/*`)
- **Format:** JSON responses with caching

---

## Deployment

**Environment Variables:**
- `MONGODB_URI` (required)
- `KAFKA_BOOTSTRAP_SERVERS` (default: localhost:9092)
- `USE_MOCK_KAFKA` (default: true)
- `REDIS_URL` (optional)
- `ENV` (default: development)

**Security:**
- All credentials in `.env` (gitignored)
- Template in `.env.example` for team

**Performance:**
- Full async/await (no blocking I/O)
- Cache TTLs: 60s historial, 300s metadata
- Connection pooling via Motor

---

## Ready For

1. ✓ Add MongoDB credentials to `.env`
2. ✓ Run `uvicorn main:app --reload`
3. ✓ Test with mock events (`POST /dev/simulate`)
4. ✓ Query audit trail via REST endpoints
5. ✓ Switch to real Kafka when Group 1 ready (set `USE_MOCK_KAFKA=false`)

All code compiles, imports verified, ready for testing.

---

## Support

- **Architecture:** README.md
- **Setup:** QUICK_START.md
- **Interactive Docs:** http://localhost:8000/docs
- **Code:** Well-commented throughout

