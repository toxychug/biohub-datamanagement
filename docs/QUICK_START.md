# Quick Start Guide

## Prerequisites

- Python 3.10+
- MongoDB account (Cloud Atlas or local)
- Virtual environment initialized (.venv)

## Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure MongoDB

Edit `.env` and set your MongoDB connection string:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=BiohubCluster
```

### 3. Run the Service

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

---

## First Test (Inject Mock Event)

Create a file `test_record.json`:

```json
{
  "identificacion_basica": {
    "id_registro": "TEST-001",
    "nombre_cientifico": "Panthera onca",
    "nombre_comun": "Jaguar",
    "taxonomia": {
      "reino": "Animalia",
      "filo": "Chordata",
      "clase": "Mammalia",
      "orden": "Carnivora",
      "familia": "Felidae",
      "genero": "Panthera",
      "especie": "onca"
    }
  },
  "datos_hallazgo": {
    "fecha": "2026-04-19",
    "tipo_registro": "Avistamiento",
    "cantidad_individuos": 1
  },
  "geolocalizacion": {
    "latitud": 5.52,
    "longitud": -74.08,
    "altitud": 500,
    "region": "Cauca",
    "nivel_sensibilidad": "RESTRICTED"
  },
  "informacion_registro": {
    "investigador": "researcher@institute.org",
    "institucion": "Instituto Humboldt"
  }
}
```

### Inject via Mock Kafka

```bash
curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d @test_record.json
```

Expected response:
```json
{
  "status": "ok",
  "id_registro": "TEST-001",
  "version": 1,
  "timestamp": "2026-04-19T10:30:00"
}
```

---

## Query the Audit Trail

### Get Change History
```bash
curl http://localhost:8000/auditoria/historial/TEST-001
```

### Get Metadata
```bash
curl http://localhost:8000/auditoria/metadatos/TEST-001
```

### Get Sensitivity Classification
```bash
curl http://localhost:8000/auditoria/sensibilidad/TEST-001
```

### Get Approval Status
```bash
curl http://localhost:8000/aprobacion/TEST-001
```

---

## Update Approval Status

```bash
curl -X POST http://localhost:8000/aprobacion/actualizar \
  -H "Content-Type: application/json" \
  -d '{
    "id_registro": "TEST-001",
    "nuevo_estado": "EN_REVISION",
    "director_aprobador": "director@institute.org",
    "comentarios": "Enviado para revisión científica"
  }'
```

---

## Health Check

```bash
curl http://localhost:8000/health
```

Response:
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

---

## Switching to Real Kafka

When Group 1 is ready:

1. Edit `.env`:
   ```env
   USE_MOCK_KAFKA=false
   KAFKA_BOOTSTRAP_SERVERS=group1-broker:9092
   ```

2. Restart the service — it will connect to the real broker and start consuming `registros-biologicos` topic.

---

## MongoDB Collections

Inspect your data in MongoDB:

```javascript
// Show all audit entries for a record
db.audit_entries.find({ id_registro: "TEST-001" }).pretty()

// Show latest snapshot
db.biological_records.findOne({ id_registro: "TEST-001" })

// Count all records
db.biological_records.countDocuments()
```

---

## Troubleshooting

**MongoDB connection fails:** Check `.env` credentials and network access.

**Port 8000 already in use:** Use `uvicorn main:app --port 8001 --reload`

**Import errors:** Run `pip install -r requirements.txt` again and check for version conflicts.

**Mock Kafka not working:** Ensure `ENV=development` in `.env`.

---

## Next: Connect to Group 3

Your REST API is ready for Group 3 to consume:
- `GET /auditoria/historial/{id}`
- `GET /auditoria/metadatos/{id}`
- `GET /auditoria/sensibilidad/{id}`
- `GET /aprobacion/{id}`
- `POST /aprobacion/actualizar`

All endpoints return JSON and support caching. See `/docs` for full OpenAPI spec.
