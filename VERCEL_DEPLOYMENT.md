# Deploying BioHub to Vercel

This guide explains how to deploy the BioHub Change Management microservice to Vercel.

## Prerequisites

- Vercel account (free at https://vercel.com)
- GitHub repository connected to Vercel
- MongoDB Atlas cluster (or use in-memory mode without MongoDB)

## Deployment Steps

### 1. Connect Repository to Vercel

1. Go to https://vercel.com
2. Click "New Project"
3. Select your BioHub repository from GitHub
4. Click "Import"

### 2. Set Environment Variables

In Vercel Dashboard, go to **Settings → Environment Variables** and add:

| Variable | Value | Notes |
|----------|-------|-------|
| `MONGODB_URI` | `mongodb+srv://user:pass@cluster.mongodb.net/?appName=...` | Optional. If not set, app uses in-memory database |
| `MONGODB_DB_NAME` | `biohub_db` | Database name (optional, defaults to `biohub_db`) |
| `ENV` | `production` | Environment mode |
| `USE_MOCK_KAFKA` | `true` | Use mock Kafka (required for serverless) |

**Important:** The app will work **without `MONGODB_URI`** — it falls back to in-memory database automatically.

### 3. Deploy

Push to your repository:

```bash
git push origin main
```

Vercel will automatically:
1. Install dependencies
2. Build the application
3. Deploy to serverless functions

### 4. Verify Deployment

Your app will be available at: `https://your-project.vercel.app`

Test endpoints:
- Dashboard: `https://your-project.vercel.app/ui/`
- API Docs: `https://your-project.vercel.app/docs`
- Health Check: `https://your-project.vercel.app/health`

---

## How It Works on Vercel

| Component | Status | Notes |
|-----------|--------|-------|
| **FastAPI Backend** | ✅ Running | Deployed as serverless function |
| **Static Files** | ✅ Served | HTML/CSS/JS from `/static/` folder |
| **MongoDB** | ⚠️ Optional | Connects if `MONGODB_URI` is set |
| **In-Memory Database** | ✅ Default | Auto-activates if MongoDB unavailable |
| **Kafka Consumer** | ⚠️ Mock Mode | Real Kafka not recommended on serverless |
| **Redis Cache** | ⚠️ Not available | Uses in-memory cache on Vercel |

---

## Troubleshooting

### Error: "mongodb_uri: Field required"

**Solution:** This error is now fixed! The app will automatically use in-memory mode if `MONGODB_URI` is not set.

If you still see this error:
1. Redeploy the project: `git push origin main`
2. Check that `config.py` has `mongodb_uri: Optional[str] = None`

### App starts but no data

**Expected behavior:** On first deploy without MongoDB, the app seeds sample data (5 biological records) automatically. They'll persist for the session.

### "Static files not found"

Vercel might need to know about the `/static/` directory. If this happens:
1. Check that `static/index.html` exists in repository
2. Redeploy: `git push origin main`

---

## Optional: Add MongoDB

To persist data on Vercel:

1. Create free MongoDB Atlas cluster at https://www.mongodb.com/cloud/atlas
2. Get connection string: `mongodb+srv://user:pass@cluster.mongodb.net/`
3. Add `MONGODB_URI` to Vercel environment variables
4. Redeploy

---

## Optional: Custom Domain

1. Go to **Settings → Domains** in Vercel
2. Add your custom domain
3. Update DNS records (instructions provided by Vercel)

---

## Environment Configuration

The app supports these environment variables:

```env
# Optional - if not set, uses in-memory database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/?appName=BiohubCluster

# Database name (default: biohub_db)
MONGODB_DB_NAME=biohub_db

# Environment mode (default: development)
ENV=production

# Use mock Kafka instead of real Kafka (recommended for serverless)
USE_MOCK_KAFKA=true

# Kafka settings (only if not using mock)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=registros-biologicos

# Redis URL (optional, uses in-memory cache if not set)
REDIS_URL=redis://localhost:6379
```

---

**Status:** ✅ Ready to deploy to Vercel!

Last Updated: 2024 | Group 2 — BioHub Project
