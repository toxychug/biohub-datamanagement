# BioHub Change Management & Audit Service (Group 2)

Change Management & Audit microservice for the BioHub biological intelligence platform. Acts as the middle layer of the data pipeline for the Ministry of Environment of Colombia.

## Architecture

- **Consumes:** Kafka events from Group 1 (`registros-biologicos` topic)
- **Stores:** Immutable audit trails in MongoDB
- **Exposes:** REST API for Group 3 to query change history and traceability
- **Cache:** Redis (optional) with in-memory fallback

## Project Structure

```
biohub-datamanagement/
├── config.py              # Settings from .env
├── main.py                # FastAPI app entry point
├── requirements.txt       # Python dependencies
├── pytest.ini            # Test configuration
├── README.md             # This file
├── CONTRIBUTING.md       # Contribution guidelines
├── TESTING_GUIDE.md      # Testing documentation
├── CHANGELOG.md          # Version history
├── GITHUB_DEPLOYMENT.md  # Deployment guide
│
├── docs/                 # 📚 Documentation (see docs/README.md)
│   ├── QUICK_START.md
│   ├── MOCK_INPUT_SPECS.md
│   ├── ENDPOINTS_REFERENCE.md
│   └── ...
│
├── scripts/              # 🔧 Utility scripts (see scripts/README.md)
│   ├── generate_report.py
│   ├── generate_guide.py
│   └── ...
│
├── archive/              # 📦 Historical reference (see archive/README.md)
│   ├── BIOHUB_DESIGN1.md
│   └── ...
│
├── cache/                # Cache layer
│   └── cache.py          # Redis or in-memory cache
│
├── database/             # Database layer
│   ├── connection.py     # Async MongoDB (Motor) client
│   └── models.py         # Pydantic domain models
│
├── services/             # Business logic
│   ├── audit_service.py
│   ├── sensitivity_service.py
│   └── approval_service.py
│
├── routers/              # API endpoints
│   ├── auditoria.py      # Historial, metadatos, sensibilidad
│   └── aprobacion.py     # Approval status and updates
│
├── kafka_service/        # Kafka integration
│   ├── consumer.py       # Async Kafka consumer
│   └── mock_producer.py  # Development simulator
│
├── static/               # Frontend
│   ├── index.html        # Dashboard
│   └── mock-input.html   # Mock Kafka input form
│
├── tests/                # Unit tests
│   ├── test_audit_service.py
│   ├── test_eca01_cache.py
│   └── test_eca02_kafka.py
│
├── .github/              # GitHub Actions
│   └── workflows/        # CI/CD pipelines
│
├── Dockerfile            # Docker container
├── docker-compose.yml    # Full stack with services
└── .env.example          # Environment template
```

## 📂 Folder Guide

- **`docs/`** — Comprehensive documentation (setup, testing, API reference)
- **`scripts/`** — One-time utility scripts (not part of core app)
- **`archive/`** — Historical/reference documents
- **`cache/`, `database/`, `services/`, etc.** — Core application code

See [docs/README.md](docs/README.md) for documentation index.


## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your MongoDB credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=BiohubCluster
MONGODB_DB_NAME=biohub_db
```

### 3. Run the Service

```bash
uvicorn main:app --reload
```

Service starts at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /health` — Service connectivity status

### Audit History
- `GET /auditoria/historial/{id_registro}` — Complete change history (versioned)
- `GET /auditoria/metadatos/{id_registro}` — Metadata from latest snapshot
- `GET /auditoria/sensibilidad/{id_registro}` — Sensitivity classification

### Approval Workflow
- `GET /aprobacion/{id_registro}` — Current approval status
- `POST /aprobacion/actualizar` — Advance approval workflow state

### Development (Mock Kafka)
- `POST /dev/simulate` — Inject a biological record (dev mode only)

## Development

### Mock Kafka Events

In development mode, use `POST /dev/simulate` to inject events without Kafka:

```bash
curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d @sample_record.json
```

The `.env` file comes with `USE_MOCK_KAFKA=true` by default — the real Kafka consumer is skipped.

### Database

- `audit_entries` — Append-only audit records (immutable)
- `biological_records` — Latest snapshot of each record (upserted)

Index: `{ id_registro: 1, version: -1 }`

### Cache

Redis is optional. If not available, the service falls back to in-memory dict cache.

## Integration with Other Groups

**Group 1 → Group 2 (Kafka)**
- Topic: `registros-biologicos`
- Format: Full biological record JSON with `trazabilidad.version` and `trazabilidad.historial_cambios`

**Group 2 → Group 3 (REST)**
- `GET /auditoria/*` — Change history and metadata
- `GET /aprobacion/*` — Approval workflow status

## Immutability Pattern

All records are **never deleted or modified**:
- Each change creates a new `AuditEntry` with incremented `version`
- Previous values are recorded in `campos_modificados`
- Full record snapshot stored in `snapshot_completo`
- Scientific approval changes also create new audit entries (no in-place updates)

## Testing

Run the server and test endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Inject mock event
curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "identificacion_basica": {
      "id_registro": "REG-001",
      "nombre_cientifico": "Panthera onca"
    },
    "geolocalizacion": {
      "latitud": 5.52,
      "longitud": -74.08,
      "nivel_sensibilidad": "RESTRICTED"
    },
    "informacion_registro": {
      "investigador": "test@example.com"
    }
  }'

# Query audit history
curl http://localhost:8000/auditoria/historial/REG-001

# Query sensitivity
curl http://localhost:8000/auditoria/sensibilidad/REG-001

# Query approval status
curl http://localhost:8000/aprobacion/REG-001
```

## Notes

- All timestamps are in UTC (`datetime.utcnow()`)
- Sensitivity defaults to `PUBLIC` if not specified
- Approval state defaults to `PENDIENTE` on record creation
- Cache TTL: 60s for historial, 300s for metadata and sensitivity
