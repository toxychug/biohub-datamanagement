# 🚀 In-Memory Database: Quick Start

## Test It Out Now!

### **Without MongoDB**

```bash
# No setup needed - just run!
uvicorn main:app --reload
```

Watch the console:
```
[*] Starting BioHub Change Management & Audit Service...
[!] MongoDB connection failed: Connection refused
[*] Falling back to in-memory database (development mode)
[✓] Seeded 5 sample records to in-memory database
[✓] Service started successfully
```

### **Access the App**

1. **Dashboard**: http://localhost:8000/ui
2. **Sample Data**: Already loaded (5 biological records)
3. **Query History**: http://localhost:8000/auditoria/historial/REG-001
4. **Register New**: http://localhost:8000/ui/mock-input.html

### **Check Database Status**

```bash
curl http://localhost:8000/health | jq '.db'
# Output: "in-memory (MongoDB unavailable)"
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│     FastAPI Application (main.py)       │
├─────────────────────────────────────────┤
│                                         │
│   ┌────────────────────────────────┐   │
│   │  Connection.py                 │   │
│   │  ├─ Try MongoDB                │   │
│   │  └─ Fallback → In-Memory ✅    │   │
│   └────────────────────────────────┘   │
│              │                          │
│       ┌──────┴──────┐                  │
│       ↓             ↓                  │
│   MongoDB      In-Memory DB            │
│   (if up)      (if down)               │
│                                         │
│   ├─ audit_entries                     │
│   └─ biological_records                │
│                                         │
│   Seeded with 5 sample records ✓       │
│                                         │
└─────────────────────────────────────────┘
```

---

## Files Added/Modified

| File | Change | Purpose |
|------|--------|---------|
| `database/in_memory_db.py` | ✨ NEW | In-memory storage layer |
| `database/db_seed.py` | ✨ NEW | Auto-seeds sample data |
| `database/connection.py` | 🔄 MODIFIED | MongoDB + fallback logic |
| `main.py` | 🔄 MODIFIED | Calls seeder on startup |
| `docs/IN_MEMORY_DATABASE.md` | ✨ NEW | Full documentation |

---

## What Works

- ✅ All endpoints function normally
- ✅ Data persists during session
- ✅ Sample data loads on startup
- ✅ New records via simulator are stored
- ✅ Queries return results
- ✅ Cache works (in-memory)

---

## What Doesn't Persist

- ❌ Data lost when app stops
- ❌ No database backup
- ❌ Single-instance only (no clustering)

---

## When to Use

| Scenario | Use In-Memory? | Recommendation |
|----------|---|---|
| Local Development | ✅ Yes | **Best** - No setup |
| Testing Features | ✅ Yes | **Fast** - Test immediately |
| Demo | ✅ Yes | **Good** - No dependencies |
| Production | ❌ No | Use MongoDB or managed DB |
| Integration Testing | ⚠️ Maybe | Consider Docker Compose |

---

## Next: Set Up MongoDB (Optional)

When you're ready to persist data:

```bash
# Start MongoDB with Docker
docker run -d -p 27017:27017 mongo

# Restart app
uvicorn main:app --reload
```

The app will automatically detect MongoDB and use it.

---

## Documentation

- **Full Guide**: [IN_MEMORY_DATABASE.md](./docs/IN_MEMORY_DATABASE.md)
- **Deployment**: [../GITHUB_DEPLOYMENT.md](../GITHUB_DEPLOYMENT.md)
- **Docker**: See docker-compose.yml

---

## Troubleshooting

**Q: How do I know if it's using in-memory?**
```bash
curl http://localhost:8000/health
# Look for: "db": "in-memory (MongoDB unavailable)"
```

**Q: How do I force MongoDB?**
- Start MongoDB before running the app
- App will auto-detect and use it

**Q: How do I clear data?**
- Restart the app (fresh seed data loads)

**Q: Can I export data?**
- Not directly from in-memory
- Use `/dev/simulate` to manually test scenarios

---

**Ready to test?** 🎉
```bash
uvicorn main:app --reload
```
