# Biometric Payment API

Backend platform for Hybrid Biometric Merchant Payment System (Single Device).

## Tech Stack

- **Python 3.11+** with **FastAPI**
- **Supabase** (PostgreSQL + pgvector + Auth + Storage + Realtime)
- **SQLAlchemy 2.0** for ORM
- **InsightFace** (ArcFace) for face recognition
- **ONNX Runtime** for ML inference

## Setup

### 1. Clone & Masuk Direktori

```bash
git clone <repo-url>
cd smart-access-api
```

### 2. Buat Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Untuk **development** (tanpa InsightFace/ONNX, lebih ringan):
```bash
pip install -r requirements-dev.txt
```

Untuk **production** (lengkap dengan biometric ML):
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Environment

```bash
cp .env.example .env
```

Edit `.env` dan isi variabel berikut:

| Variabel | Keterangan |
|---|---|
| `SUPABASE_URL` | URL project Supabase kamu |
| `SUPABASE_KEY` | Anon/public key Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key Supabase |
| `DATABASE_URL` | Connection string PostgreSQL (format: `postgresql+asyncpg://user:pass@host:port/db`) |
| `JWT_SECRET_KEY` | Secret key untuk signing JWT token |
| `KGITON_API_KEY` | API key untuk integrasi KGiTON (IoT device) |

### 5. Jalankan Database (via Docker)

```bash
docker compose up db -d
```

Database PostgreSQL akan berjalan di port `5433`.

### 6. Seed Data (Opsional)

```bash
python seed.py
```

### 7. Jalankan Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### Alternatif: Jalankan Semua via Docker

```bash
docker compose up --build
```

API akan tersedia di `http://localhost:8000`.

## Project Structure

```
app/
├── main.py              # FastAPI application entry
├── config.py            # Settings / environment config
├── dependencies.py      # Dependency injection
├── api/v1/              # API route handlers
│   ├── router.py        # Main v1 router
│   └── endpoints/       # Endpoint modules
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic request/response schemas
├── services/            # Business logic layer
├── core/                # Core utilities (security, db, exceptions)
└── middleware/           # Custom middleware
```

## API Documentation

Once running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
