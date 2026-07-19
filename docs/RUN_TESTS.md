# How to Run Tests — Fixed Version

The health check endpoint error has been fixed. Here's how to test:

## Quick Test (30 seconds)

### 1. Start the service:
```bash
uvicorn main:app --reload
```

### 2. In another terminal, test the health endpoint:
```bash
curl http://localhost:8000/health
```

**Expected response:**
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

### 3. If that works, try creating a record:
```bash
curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "identificacion_basica": {"id_registro":"QUICK-TEST","nombre_cientifico":"Panthera onca"},
    "geolocalizacion": {"latitud":5.52,"nivel_sensibilidad":"RESTRICTED"},
    "informacion_registro": {"investigador":"test@example.org"}
  }'
```

### 4. Query the result:
```bash
curl http://localhost:8000/auditoria/historial/QUICK-TEST
```

---

## Full Automated Test

### Windows:
```bash
test_all_endpoints.bat
```

### macOS/Linux:
```bash
bash test_all_endpoints.sh
```

---

## Browser (Easiest)

Open: `http://localhost:8000/docs`

Then:
1. Click on any endpoint
2. Click "Try it out"
3. Fill in parameters (if needed)
4. Click "Execute"
5. See response below

---

## What Was Fixed

The health check endpoint had an issue with MongoDB object testing. It's now fixed to properly handle database connections and cache checks.

**The error you saw:**
```
"detail": "Database objects do not implement truth value testing..."
```

**Is now fixed.** The health endpoint properly checks the connection status.

---

## Next: Full Testing

See **[START_HERE.md](START_HERE.md)** or **[HOW_TO_TEST.md](HOW_TO_TEST.md)** for complete testing guides.
