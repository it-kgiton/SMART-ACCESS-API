# Biometric Payment API

Backend platform for Hybrid Biometric Merchant Payment System (Single Device).

## Tech Stack

- **Python 3.11+** with **FastAPI**
- **Supabase** (PostgreSQL + pgvector + Auth + Storage + Realtime)
- **SQLAlchemy 2.0** for ORM
- **InsightFace** (ArcFace) for face recognition
- **ONNX Runtime** for ML inference

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env template
cp .env.example .env
# Edit .env with your credentials

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

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
