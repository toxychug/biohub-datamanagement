# API Endpoints Quick Reference

**Base URL:** `http://localhost:8000`

---

## 1️⃣ Health Check
```bash
GET /health
```
→ Returns: `{ "status": "ok", "db": "connected", "cache": "memory", ... }`

---

## 2️⃣ Create Audit Entry (Mock Kafka)
```bash
POST /dev/simulate
Content-Type: application/json

{
  "identificacion_basica": { "id_registro": "REG-001", ... },
  "geolocalizacion": { "latitud": 5.52, "nivel_sensibilidad": "RESTRICTED" },
  "informacion_registro": { "investigador": "user@org" },
  ...
}
```
→ Returns: `{ "status": "ok", "id_registro": "REG-001", "version": 1 }`

---

## 3️⃣ Get Audit History
```bash
GET /auditoria/historial/{id_registro}
```
Example: `GET /auditoria/historial/REG-001`

→ Returns: Array of audit entries (all versions)
```json
[
  {
    "id_registro": "REG-001",
    "version": 1,
    "timestamp": "2026-04-19T15:30:00",
    "usuario": "researcher@org",
    "campos_modificados": [],
    "motivo": "",
    "sensibilidad": "RESTRICTED",
    "estado_aprobacion": "PENDIENTE"
  }
]
```

---

## 4️⃣ Get Metadata
```bash
GET /auditoria/metadatos/{id_registro}
```
Example: `GET /auditoria/metadatos/REG-001`

→ Returns: `{ "identificacion_basica": {...}, "informacion_registro": {...} }`

---

## 5️⃣ Get Sensitivity
```bash
GET /auditoria/sensibilidad/{id_registro}
```
Example: `GET /auditoria/sensibilidad/REG-001`

→ Returns: `{ "id_registro": "REG-001", "sensibilidad": "RESTRICTED" }`

**Values:** `PUBLIC`, `RESTRICTED`, `CONFIDENTIAL`

---

## 6️⃣ Get Approval Status
```bash
GET /aprobacion/{id_registro}
```
Example: `GET /aprobacion/REG-001`

→ Returns: `{ "id_registro": "REG-001", "estado_aprobacion": "PENDIENTE" }`

**Values:** `PENDIENTE`, `EN_REVISION`, `APROBADO`, `RECHAZADO`

---

## 7️⃣ Update Approval
```bash
POST /aprobacion/actualizar
Content-Type: application/json

{
  "id_registro": "REG-001",
  "nuevo_estado": "EN_REVISION",
  "director_aprobador": "director@org",
  "comentarios": "Reviewing data"
}
```

→ Returns: `{ "status": "ok", "version": 2, "nuevo_estado": "EN_REVISION" }`

---

## Test Workflow (Copy & Paste)

```bash
# 1. Health
curl http://localhost:8000/health

# 2. Create record
curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d '{"identificacion_basica":{"id_registro":"TEST"},"geolocalizacion":{"nivel_sensibilidad":"RESTRICTED"},"informacion_registro":{"investigador":"test@org"}}'

# 3. Get history
curl http://localhost:8000/auditoria/historial/TEST

# 4. Get metadata
curl http://localhost:8000/auditoria/metadatos/TEST

# 5. Get sensitivity
curl http://localhost:8000/auditoria/sensibilidad/TEST

# 6. Get approval status
curl http://localhost:8000/aprobacion/TEST

# 7. Update approval
curl -X POST http://localhost:8000/aprobacion/actualizar \
  -H "Content-Type: application/json" \
  -d '{"id_registro":"TEST","nuevo_estado":"EN_REVISION","director_aprobador":"director@org","comentarios":"reviewing"}'

# 8. Verify updated
curl http://localhost:8000/auditoria/historial/TEST
```

---

## Browser Access

- **Interactive Docs:** http://localhost:8000/docs
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## Response Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 404 | Record not found |
| 400 | Bad request / invalid data |
| 500 | Server error |

---

## Error Example

```bash
curl http://localhost:8000/auditoria/historial/NONEXISTENT
```

→ Returns (404):
```json
{
  "detail": "No audit history found"
}
```

---

For detailed examples and testing scenarios, see **TESTING_GUIDE.md**
