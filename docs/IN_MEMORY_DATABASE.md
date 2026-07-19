# 💾 In-Memory Database Fallback

## Overview

The BioHub application can work **without MongoDB** by using an in-memory database fallback. This is useful for:

- 🧪 **Development & Testing** — No need to set up MongoDB locally
- 🔧 **Prototyping** — Quick testing without database setup
- ⏸️ **MongoDB Downtime** — App continues to work if MongoDB is paused/unavailable
- 📚 **Demo/Learning** — Try the app with pre-loaded sample data

---

## How It Works

### 1. **Automatic Fallback**

When the app starts:
1. ✅ Tries to connect to MongoDB
2. ❌ If MongoDB is unavailable → Falls back to in-memory storage
3. 🌱 Auto-seeds 5 sample records

```
[*] Starting BioHub Change Management & Audit Service...
[!] MongoDB connection failed: <error>
[*] Falling back to in-memory database (development mode)
[✓] Seeded 5 sample records to in-memory database
[✓] Service started successfully
```

### 2. **API Works the Same**

All endpoints work identically:
```bash
# These work with both MongoDB and in-memory
GET  /auditoria/historial/{id_registro}
GET  /auditoria/metadatos/{id_registro}
GET  /auditoria/sensibilidad/{id_registro}
GET  /aprobacion/{id_registro}
POST /aprobacion/actualizar
POST /dev/simulate
```

### 3. **Sample Data Included**

When using in-memory, these records are pre-loaded:

| ID | Nombre Científico | Nombre Común |
|----|--------------------|--------------|
| REG-001 | *Panthera onca* | Jaguar |
| REG-002 | *Vultur gryphus* | Cóndor andino |
| REG-003 | *Ara chloropterus* | Guacamaya verde |
| REG-004 | *Ateles fusciceps* | Mono araña |
| REG-005 | *Boa constrictor* | Anaconda |

---

## Usage Scenarios

### **Scenario 1: MongoDB is Paused**

```bash
# MongoDB is not running
$ uvicorn main:app --reload

[!] MongoDB connection failed: ...
[*] Falling back to in-memory database (development mode)
[✓] Seeded 5 sample records to in-memory database

# App starts normally!
# All endpoints work with in-memory data
```

### **Scenario 2: Quick Testing**

```bash
# No MongoDB setup needed
$ python -m venv venv
$ .\venv\Scripts\Activate.ps1
$ pip install -r requirements.txt
$ uvicorn main:app --reload

# App is ready immediately with sample data
```

### **Scenario 3: Test New Features**

```bash
# Register new records via the simulator
$ curl -X POST http://localhost:8000/dev/simulate \
  -H "Content-Type: application/json" \
  -d @sample_record.json

# They're stored in memory and available for queries
$ curl http://localhost:8000/auditoria/historial/REG-NEW
```

---

## Technical Details

### **Files**

- **`database/in_memory_db.py`** — In-memory storage implementation
- **`database/db_seed.py`** — Auto-seed sample data
- **`database/connection.py`** — MongoDB with fallback logic

### **What's Stored In-Memory**

- ✅ **Audit Entries** — Full change history
- ✅ **Records Snapshots** — Latest data for each record
- ❌ **NOT Persisted** — Data is lost when app restarts

### **Limitations**

| Feature | MongoDB | In-Memory |
|---------|---------|-----------|
| Persistence | ✅ Yes | ❌ No |
| Production Ready | ✅ Yes | ❌ Dev Only |
| Performance | 📊 Database | ⚡ RAM |
| Data Size | 🔋 Large datasets | 💬 Small (demo) |
| Clustering | ✅ Yes | ❌ No |

---

## Health Check

Check database status:

```bash
$ curl http://localhost:8000/health

{
  "status": "ok",
  "service": "biohub-change-management",
  "db": "in-memory (MongoDB unavailable)",  # ← Shows fallback mode
  "cache": "memory",
  "kafka": "mock",
  "environment": "development"
}
```

---

## Configuration

### **Switch to In-Memory Manually**

Set in `.env`:
```env
# Pause/stop MongoDB, app will fallback
MONGODB_URI=mongodb://invalid:27017  # Invalid URI triggers fallback
```

### **Force MongoDB Connection**

```env
# In production, fails if MongoDB unavailable
ENV=production
MONGODB_URI=mongodb+srv://...
```

---

## When In-Memory is Used

✅ **In Development Mode When:**
- MongoDB connection fails
- MongoDB is paused/stopped
- MongoDB credentials are wrong
- MongoDB is unreachable

❌ **NOT Used In Production:**
- Production mode requires MongoDB to be available
- App will fail to start if MongoDB is down

---

## Data Persistence

### **In-Memory Session**

```
App Start → Seed Data → Accept Requests → App Stop
                           ↓
                      Data Lost
```

### **With MongoDB**

```
App Start → Connect DB → Accept Requests → App Stop
                              ↓
                         Data Persists
```

---

## Development Workflow

### **Option 1: No MongoDB Setup** (Fastest)

```bash
# No MongoDB needed
$ uvicorn main:app --reload

# Test with sample data
# Register new records via the form
# Query everything as normal
```

### **Option 2: With MongoDB** (Recommended for Integration)

```bash
# Start MongoDB separately
$ docker run -d -p 27017:27017 mongo

# Run app
$ uvicorn main:app --reload

# Same API, but data persists
```

### **Option 3: Full Stack with Docker**

```bash
# Everything in one command
$ docker-compose up -d

# MongoDB + Redis + App all running
# Data persists across restarts
```

---

## Switching from In-Memory to MongoDB

1. **Start MongoDB**
   ```bash
   docker run -d -p 27017:27017 mongo
   ```

2. **Restart app**
   ```bash
   uvicorn main:app --reload
   ```

3. **Check status**
   ```bash
   curl http://localhost:8000/health
   # Should show: "db": "connected"
   ```

4. **Fresh data**
   - In-memory data is discarded
   - Use `POST /dev/simulate` to seed new data
   - Or restore from backup

---

## Next Steps

- ✅ Try without MongoDB: `uvicorn main:app --reload`
- 🧪 Test the simulator: http://localhost:8000/ui/mock-input.html
- 🗄️ Set up MongoDB when ready: [GITHUB_DEPLOYMENT.md](../GITHUB_DEPLOYMENT.md)
- 🐳 Use Docker Compose for full stack
