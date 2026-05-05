# Skill: Deployment — Smart Access API

Panduan deployment Smart Access API ke Railway dan setup Docker lokal.

---

## Environments

| Environment | Platform | Branch    | URL                                            |
| ----------- | -------- | --------- | ---------------------------------------------- |
| Production  | Railway  | `main`    | `https://smart-access-api.railway.app`         |
| Staging     | Railway  | `staging` | `https://smart-access-api-staging.railway.app` |
| Local Dev   | Docker   | any       | `http://localhost:8000`                        |

---

## Local Development

### Dengan Docker Compose (recommended)

```bash
# Start semua service (postgres + api)
docker-compose up

# Background
docker-compose up -d

# Rebuild image
docker-compose up --build

# Stop
docker-compose down

# Stop dan hapus volume (reset database)
docker-compose down -v
```

### Tanpa Docker

```bash
# Aktifkan virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy dan isi env
cp .env.example .env
# Edit DATABASE_URL, JWT_SECRET_KEY, dll

# Jalankan server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Setup database (sekali saja)
psql postgresql://postgres:postgres@localhost:5432/smartaccess -f database/schema.sql
```

---

## Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system deps untuk InsightFace
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Railway Deployment

### railway.toml

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### Environment Variables di Railway

Wajib di-set di Railway dashboard:

```
DATABASE_URL=postgresql+asyncpg://...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
JWT_SECRET_KEY=<random-256-bit>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEVICE_TOKEN_EXPIRE_DAYS=365
KGITON_API_URL=https://api.kgiton.com
KGITON_API_KEY=<api-key>
FACE_SIMILARITY_THRESHOLD=0.55
FINGERPRINT_MATCH_THRESHOLD=40
FIRMWARE_STORAGE_BUCKET=firmware
BIOMETRIC_STORAGE_BUCKET=biometric-assets
```

### Deploy ke Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link ke project
railway link

# Deploy manual
railway up

# Lihat logs
railway logs

# Set env variable
railway variables set KEY=VALUE
```

---

## Health Check

API expose endpoint `/health` untuk Railway health check:

```python
# app/main.py
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "smart-access-api"}
```

---

## Database Setup di Production

```bash
# Koneksi ke Supabase SQL Editor (preferred)
# Paste isi database/schema.sql

# Atau via psql dengan Supabase connection string
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" \
    -f database/schema.sql
```

**INGAT:** `reset.sql` TIDAK BOLEH dijalankan di production.

---

## Monitoring & Logs

```bash
# Railway logs real-time
railway logs --tail

# Filter error
railway logs | grep ERROR

# Check status deployment
railway status
```

---

## Rollback

```bash
# Railway: rollback ke deployment sebelumnya via dashboard
# atau via CLI
railway rollback

# Atau checkout commit sebelumnya dan deploy ulang
git checkout <previous-commit>
railway up
```

---

## Pre-deploy Checklist

- [ ] Tests lulus: `pytest`
- [ ] Tidak ada import yang salah
- [ ] `.env` TIDAK tercommit ke git
- [ ] `database/schema.sql` sudah up-to-date
- [ ] `requirements.txt` sudah update jika ada dependency baru
- [ ] Health check endpoint berfungsi
- [ ] Semua env variables sudah di-set di Railway
- [ ] `reset.sql` TIDAK dijalankan di production

---

## Supabase Storage Setup

```bash
# Jalankan di Supabase SQL Editor
# (isi dari database/buckets.sql)
INSERT INTO storage.buckets (id, name, public)
VALUES ('firmware', 'firmware', false),
       ('biometric-assets', 'biometric-assets', false);
```
