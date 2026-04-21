# BioHub API Testing Guide

Complete walkthrough for testing every endpoint with curl, Postman, or the browser.

---

## Prerequisites

1. **Start the service:**
   ```bash
   uvicorn main:app --reload
   ```

2. **Service runs at:** `http://localhost:8000`

3. **Interactive docs:** `http://localhost:8000/docs`

---

## Test Data (Sample Biological Record)

Save this as `test_record.json`:

```json
{
  "identificacion_basica": {
    "id_registro": "REG-TEST-001",
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
    },
    "estado_taxonomico": "Válido",
    "autoridad_taxonomica": "Linnaeus, 1758",
    "fecha_clasificacion": "2026-01-15"
  },
  "datos_hallazgo": {
    "fecha": "2026-04-19",
    "hora": "14:30",
    "tipo_registro": "Avistamiento",
    "metodo_observacion": "Cámara trampa",
    "cantidad_individuos": 1,
    "comportamiento": "Cazando"
  },
  "geolocalizacion": {
    "latitud": 5.52,
    "longitud": -74.08,
    "altitud": 520,
    "region": "Cauca",
    "ecosistema": "Selva húmeda tropical",
    "precision": "100m",
    "nivel_sensibilidad": "RESTRICTED"
  },
  "datos_ambientales": {
    "temperatura": 24.5,
    "humedad": 85,
    "ph_suelo": 6.2,
    "tipo_suelo": "Franco-arcilloso",
    "clima": "Tropical húmedo",
    "precipitacion": 250.5,
    "cobertura_vegetal": "Selva primaria"
  },
  "caracteristicas_fisicas": {
    "tamano": "Grande",
    "peso": "95 kg",
    "coloracion": "Manchado",
    "edad_aproximada": "Adulto",
    "sexo": "Macho",
    "estado_salud": "Bueno",
    "caracteristicas_distintivas": "Cicatriz en oreja izquierda"
  },
  "evidencia": {
    "fotografias": ["foto_001.jpg"],
    "videos": [],
    "audios": [],
    "archivos_adjuntos": [],
    "metadatos": {
      "fecha_captura": "2026-04-19T14:30:00Z",
      "gps": "5.52,-74.08",
      "dispositivo": "Canon EOS 5D Mark IV"
    }
  },
  "estado_conservacion": {
    "categoria_amenaza": "Vulnerable",
    "nivel_riesgo": "Alto",
    "listas_oficiales": ["CITES Apéndice I", "UICN Red List"],
    "observaciones": "Población en declive"
  },
  "informacion_registro": {
    "investigador": "researcher@institute.org",
    "equipo_expedicion": "Expedición Cauca 2026",
    "institucion": "Instituto Humboldt",
    "id_expedicion": "EXP-2026-001",
    "fecha_registro": "2026-04-19T15:00:00Z",
    "estado_registro": "Activo"
  },
  "validacion_cientifica": {
    "director_aprobador": "director@institute.org",
    "estado_validacion": "Pendiente",
    "comentarios": "En revisión",
    "fecha_validacion": null
  },
  "trazabilidad": {
    "version": 0,
    "historial_cambios": []
  },
  "datos_analiticos": {
    "incluido_mapa_calor": true,
    "frecuencia_avistamiento": 2,
    "tendencias": "Estable",
    "indicadores_ecologicos": ["Biodiversidad alta"]
  },
  "datos_consumo_externo": {
    "anonimizado": false,
    "visible_publico": false,
    "version_api": "1.0",
    "restricciones_acceso": "Investigadores autorizados"
  }
}
```

---

## 1. Health Check Endpoint

### Purpose
Verify service is running and all components (DB, cache, Kafka) are connected.

### Request
```bash
curl http://localhost:8000/health
```

### Expected Response (200 OK)
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

### What to Check
- ✓ `db: "connected"` — MongoDB is reachable
- ✓ `cache: "memory" or "redis"` — Cache layer active
- ✓ `kafka: "mock" or "real"` — Kafka status
- ✓ `environment: "development"` — Mock endpoints enabled

---

## 2. Root Endpoint

### Purpose
Basic service info.

### Request
```bash
curl http://localhost:8000/
```

### Expected Response (200 OK)
```json
{
  "service": "BioHub Change Management & Audit",
  "version": "0.1.0",
  "docs": "/docs"
}
```

---

## 3. Simulate Kafka Event (POST /dev/simulate)

### Purpose
Inject a mock biological record into the system without Kafka. This creates the first audit entry.

### Request
```bash
curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d @test_record.json
```

Or inline (short version):
```bash
curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "identificacion_basica": {
      "id_registro": "TEST-SIMPLE",
      "nombre_cientifico": "Panthera onca"
    },
    "geolocalizacion": {
      "latitud": 5.52,
      "nivel_sensibilidad": "RESTRICTED"
    },
    "informacion_registro": {
      "investigador": "test@example.org"
    }
  }'
```

### Expected Response (200 OK)
```json
{
  "status": "ok",
  "id_registro": "REG-TEST-001",
  "version": 1,
  "timestamp": "2026-04-19T15:30:00.123456"
}
```

### What to Check
- ✓ `status: "ok"` — Event processed successfully
- ✓ `version: 1` — First version created
- ✓ ID matches your request
- ✓ Timestamp is current UTC

### MongoDB Verification
After this call, check MongoDB:
```javascript
// In MongoDB Compass or mongosh
db.audit_entries.findOne({ id_registro: "REG-TEST-001" })
db.biological_records.findOne({ id_registro: "REG-TEST-001" })
```

You should see one document in each collection.

---

## 4. Get Audit History (GET /auditoria/historial/{id_registro})

### Purpose
Retrieve complete change history for a biological record (all versions).

### Request
```bash
curl http://localhost:8000/auditoria/historial/REG-TEST-001
```

### Expected Response (200 OK)
```json
[
  {
    "id_registro": "REG-TEST-001",
    "version": 1,
    "timestamp": "2026-04-19T15:30:00.123456",
    "usuario": "researcher@institute.org",
    "ip_origen": null,
    "campos_modificados": [],
    "motivo": "",
    "snapshot_completo": { /* full record JSON */ },
    "sensibilidad": "RESTRICTED",
    "estado_aprobacion": "PENDIENTE"
  }
]
```

### Testing Scenarios

**Scenario A: Record doesn't exist**
```bash
curl http://localhost:8000/auditoria/historial/NONEXISTENT
```
Expected: `404 Not Found` — "No audit history found"

**Scenario B: Multiple versions**
1. Create first version with `/dev/simulate`
2. Create a second by simulating another event with same `id_registro` but different data
3. Query `/auditoria/historial/{id}` → should return 2 entries

### What to Check
- ✓ Entries sorted by version (ascending)
- ✓ Each entry has full `snapshot_completo`
- ✓ `campos_modificados` shows field changes (empty for first version)
- ✓ Cache working: second identical request is faster

---

## 5. Get Metadata (GET /auditoria/metadatos/{id_registro})

### Purpose
Get only the essential metadata (taxonomic info + record info) from the latest version.

### Request
```bash
curl http://localhost:8000/auditoria/metadatos/REG-TEST-001
```

### Expected Response (200 OK)
```json
{
  "identificacion_basica": {
    "id_registro": "REG-TEST-001",
    "nombre_cientifico": "Panthera onca",
    "nombre_comun": "Jaguar",
    "taxonomia": { /* full taxonomy */ },
    "estado_taxonomico": "Válido",
    "autoridad_taxonomica": "Linnaeus, 1758",
    "fecha_clasificacion": "2026-01-15"
  },
  "informacion_registro": {
    "investigador": "researcher@institute.org",
    "equipo_expedicion": "Expedición Cauca 2026",
    "institucion": "Instituto Humboldt",
    "id_expedicion": "EXP-2026-001",
    "fecha_registro": "2026-04-19T15:00:00Z",
    "estado_registro": "Activo"
  }
}
```

### Testing Scenarios

**Scenario A: Lightweight query**
```bash
curl http://localhost:8000/auditoria/metadatos/REG-TEST-001
```
Compare size with `/auditoria/historial` → metadata should be much smaller

**Scenario B: Cache validation**
- First request: ~50-100ms (queries MongoDB)
- Second request: <5ms (from cache, 300s TTL)

### What to Check
- ✓ Only `identificacion_basica` + `informacion_registro` returned
- ✓ No environmental or physical characteristic data
- ✓ Response is lean (good for high-volume queries)

---

## 6. Get Sensitivity Classification (GET /auditoria/sensibilidad/{id_registro})

### Purpose
Check the sensitivity level of a record (determines who can access the location data).

### Request
```bash
curl http://localhost:8000/auditoria/sensibilidad/REG-TEST-001
```

### Expected Response (200 OK)
```json
{
  "id_registro": "REG-TEST-001",
  "sensibilidad": "RESTRICTED"
}
```

### Testing Scenarios

**Scenario A: RESTRICTED (from test data)**
```bash
curl http://localhost:8000/auditoria/sensibilidad/REG-TEST-001
```
Response: `"sensibilidad": "RESTRICTED"`

**Scenario B: Different sensitivity levels**

Inject a record with `nivel_sensibilidad: "PUBLIC"`:
```bash
curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "identificacion_basica": { "id_registro": "PUBLIC-RECORD" },
    "geolocalizacion": { "nivel_sensibilidad": "PUBLIC" },
    "informacion_registro": { "investigador": "test@example.org" }
  }'

curl http://localhost:8000/auditoria/sensibilidad/PUBLIC-RECORD
```
Response: `"sensibilidad": "PUBLIC"`

**Scenario C: Missing sensitivity (defaults to PUBLIC)**
```bash
curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "identificacion_basica": { "id_registro": "DEFAULT-RECORD" },
    "geolocalizacion": {},
    "informacion_registro": { "investigador": "test@example.org" }
  }'

curl http://localhost:8000/auditoria/sensibilidad/DEFAULT-RECORD
```
Response: `"sensibilidad": "PUBLIC"` (default)

### What to Check
- ✓ Correct classification from `geolocalizacion.nivel_sensibilidad`
- ✓ Fallback to `datos_consumo_externo.restricciones_acceso` if geo not set
- ✓ Defaults to PUBLIC when neither is set
- ✓ Cached for 300s

---

## 7. Get Approval Status (GET /aprobacion/{id_registro})

### Purpose
Check the current approval workflow state of a record.

### Request
```bash
curl http://localhost:8000/aprobacion/REG-TEST-001
```

### Expected Response (200 OK)
```json
{
  "id_registro": "REG-TEST-001",
  "estado_aprobacion": "PENDIENTE"
}
```

### Testing Scenarios

**Scenario A: New record (default PENDIENTE)**
```bash
# Create new record
curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d '{"identificacion_basica":{"id_registro":"NEW-REC"},"informacion_registro":{"investigador":"test@org"}}'

# Check approval status
curl http://localhost:8000/aprobacion/NEW-REC
```
Response: `"estado_aprobacion": "PENDIENTE"`

**Scenario B: Record not found**
```bash
curl http://localhost:8000/aprobacion/NONEXISTENT
```
Expected: `404 Not Found`

### What to Check
- ✓ New records always start with `PENDIENTE`
- ✓ Status persists across requests
- ✓ Cached for 300s

---

## 8. Update Approval Status (POST /aprobacion/actualizar)

### Purpose
Advance the approval workflow to the next state (PENDIENTE → EN_REVISION → APROBADO or RECHAZADO).

### Request
```bash
curl -X POST http://localhost:8000/aprobacion/actualizar \
  -H "Content-Type: application/json" \
  -d '{
    "id_registro": "REG-TEST-001",
    "nuevo_estado": "EN_REVISION",
    "director_aprobador": "director@institute.org",
    "comentarios": "Enviado para revisión científica"
  }'
```

### Expected Response (200 OK)
```json
{
  "status": "ok",
  "id_registro": "REG-TEST-001",
  "version": 2,
  "nuevo_estado": "EN_REVISION",
  "timestamp": "2026-04-19T16:00:00.123456"
}
```

### Testing Scenarios

**Scenario A: Full approval workflow**

Step 1: Create record (default = PENDIENTE)
```bash
curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d '{"identificacion_basica":{"id_registro":"WORKFLOW-TEST"},"informacion_registro":{"investigador":"test@org"}}'
```

Step 2: Move to EN_REVISION
```bash
curl -X POST http://localhost:8000/aprobacion/actualizar \
  -H "Content-Type: application/json" \
  -d '{
    "id_registro": "WORKFLOW-TEST",
    "nuevo_estado": "EN_REVISION",
    "director_aprobador": "reviewer@institute.org",
    "comentarios": "Revisando datos taxonómicos"
  }'
```
Response: `"version": 2, "nuevo_estado": "EN_REVISION"`

Step 3: Approve
```bash
curl -X POST http://localhost:8000/aprobacion/actualizar \
  -H "Content-Type: application/json" \
  -d '{
    "id_registro": "WORKFLOW-TEST",
    "nuevo_estado": "APROBADO",
    "director_aprobador": "director@institute.org",
    "comentarios": "Datos validados. Aprobado para publicación."
  }'
```
Response: `"version": 3, "nuevo_estado": "APROBADO"`

Step 4: Verify history
```bash
curl http://localhost:8000/auditoria/historial/WORKFLOW-TEST
```
Should show 3 versions: initial (PENDIENTE) → EN_REVISION → APROBADO

**Scenario B: Rejection workflow**
```bash
curl -X POST http://localhost:8000/aprobacion/actualizar \
  -H "Content-Type: application/json" \
  -d '{
    "id_registro": "REG-TEST-001",
    "nuevo_estado": "RECHAZADO",
    "director_aprobador": "director@institute.org",
    "comentarios": "Datos incompletos. Datos ambientales faltantes."
  }'
```
Response: `"nuevo_estado": "RECHAZADO"`

### What to Check
- ✓ New audit entry created (version increments)
- ✓ Approval state updates in historial
- ✓ Cache invalidated (historial and aprobacion)
- ✓ Full record snapshot preserved at each state
- ✓ User (director_aprobador) recorded in audit trail
- ✓ Comments saved in motivo field

### Valid State Transitions
- `PENDIENTE` → `EN_REVISION`, `APROBADO`, or `RECHAZADO`
- `EN_REVISION` → `APROBADO` or `RECHAZADO`
- (Any state) → any state (no restrictions enforced, flexibility for corrections)

---

## Complete Test Sequence (Copy & Paste)

Run these in order to fully test the system:

```bash
# 1. Health check
echo "=== HEALTH CHECK ==="
curl http://localhost:8000/health | jq

# 2. Create record
echo -e "\n=== CREATE RECORD ==="
curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "identificacion_basica": {"id_registro":"TEST-FULL","nombre_cientifico":"Panthera onca"},
    "geolocalizacion": {"latitud":5.52,"nivel_sensibilidad":"RESTRICTED"},
    "informacion_registro": {"investigador":"scientist@institute.org","institucion":"Instituto Humboldt"}
  }' | jq

# 3. Get history
echo -e "\n=== GET HISTORY ==="
curl http://localhost:8000/auditoria/historial/TEST-FULL | jq

# 4. Get metadata
echo -e "\n=== GET METADATA ==="
curl http://localhost:8000/auditoria/metadatos/TEST-FULL | jq

# 5. Get sensitivity
echo -e "\n=== GET SENSITIVITY ==="
curl http://localhost:8000/auditoria/sensibilidad/TEST-FULL | jq

# 6. Get approval status
echo -e "\n=== GET APPROVAL STATUS ==="
curl http://localhost:8000/aprobacion/TEST-FULL | jq

# 7. Update approval
echo -e "\n=== UPDATE APPROVAL ==="
curl -X POST http://localhost:8000/aprobacion/actualizar \
  -H "Content-Type: application/json" \
  -d '{
    "id_registro": "TEST-FULL",
    "nuevo_estado": "EN_REVISION",
    "director_aprobador": "director@institute.org",
    "comentarios": "En revisión"
  }' | jq

# 8. Verify history updated
echo -e "\n=== VERIFY HISTORY (SHOULD SHOW 2 VERSIONS) ==="
curl http://localhost:8000/auditoria/historial/TEST-FULL | jq '.[] | {version, estado_aprobacion}'
```

---

## Testing with Postman/Insomnia

1. Create new HTTP request collection
2. Add requests for each endpoint above
3. Use environment variables:
   ```
   {{base_url}} = http://localhost:8000
   {{id_registro}} = REG-TEST-001
   ```

4. Example POST body for `/aprobacion/actualizar`:
   ```json
   {
     "id_registro": "{{id_registro}}",
     "nuevo_estado": "EN_REVISION",
     "director_aprobador": "director@institute.org",
     "comentarios": "Reviewing"
   }
   ```

---

## Testing with Swagger UI

1. Open browser: `http://localhost:8000/docs`
2. Click on each endpoint to expand
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"
6. See response in real-time

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `Connection refused` | Service not running. Run `uvicorn main:app --reload` |
| `404 Not Found` | Record doesn't exist. Create with `/dev/simulate` first |
| `"db": "error"` in health | MongoDB credentials wrong in `.env` |
| Slow first request | Normal (MongoDB cold start). Second request will be cached. |
| Cache not working | Redis not available? Check `"cache": "memory"` in `/health` |

---

## Expected Performance

| Endpoint | First Call | Cached Call |
|---|---|---|
| `/auditoria/historial` | 50-100ms | <5ms |
| `/auditoria/metadatos` | 30-50ms | <5ms |
| `/auditoria/sensibilidad` | 20-40ms | <5ms |
| `/aprobacion/{id}` | 30-50ms | <5ms |
| `/dev/simulate` | 20-50ms | N/A (not cached) |

---

## Next: MongoDB Verification

After testing endpoints, verify data in MongoDB:

```javascript
// MongoDB Compass or mongosh

// Show all audit entries for a record
db.audit_entries.find({ id_registro: "TEST-FULL" }).pretty()

// Show latest snapshot
db.biological_records.findOne({ id_registro: "TEST-FULL" })

// Count total records
db.biological_records.countDocuments()

// Count total audit entries
db.audit_entries.countDocuments()
```

---

## Complete! 🎉

Once all tests pass, your API is ready for Group 3 to integrate.

Share with them:
- Base URL: `http://your-server:8000`
- OpenAPI Docs: `http://your-server:8000/docs`
- Endpoints: All documented in `/docs`
