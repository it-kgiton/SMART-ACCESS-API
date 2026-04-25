# Smart Access API — Architecture Guide

> Baca file ini sebelum menyentuh kode. Semua konvensi, pola, dan aturan ada di sini.

---

## Overview

**Smart Access** adalah platform pembayaran biometrik hybrid untuk lingkungan sekolah.
Siswa (client) membayar ke merchant kantin/laundry menggunakan sidik jari atau wajah melalui
perangkat ESP32. Orang tua (parent) melakukan top-up saldo wallet anak secara manual.

**Stack:**

- Python 3.11 + FastAPI (async)
- PostgreSQL (Supabase cloud / local Docker)
- SQLAlchemy 2.0 async ORM — hanya untuk CRUD, **bukan** schema migration
- InsightFace ArcFace (`buffalo_l`) — face recognition 512-dim embedding
- KGiTON API — validasi lisensi perangkat ESP32
- Supabase Storage — firmware OTA + biometric assets
- WebSocket — komunikasi realtime dengan perangkat ESP32

---

## Arsitektur Layer

```
┌──────────────────────────────────────────────────────┐
│               HTTP Clients / ESP32 Device             │
└────────────────────┬─────────────────────────────────┘
                     │ REST / WebSocket
┌────────────────────▼─────────────────────────────────┐
│          app/api/v1/endpoints/  (Transport Layer)     │
│  FastAPI routers — validasi input, auth check,        │
│  delegate ke service, format response                 │
└────────────────────┬─────────────────────────────────┘
                     │ memanggil service
┌────────────────────▼─────────────────────────────────┐
│          app/services/          (Business Layer)      │
│  Semua logika bisnis ada di sini. Tidak ada logika    │
│  bisnis di endpoint atau model.                       │
└────────────────────┬─────────────────────────────────┘
                     │ query via SQLAlchemy
┌────────────────────▼─────────────────────────────────┐
│          app/models/            (Data Layer)          │
│  SQLAlchemy ORM models — definisi tabel saja.         │
│  Tidak ada logika bisnis di sini.                     │
└──────────────────────────────────────────────────────┘

Pendukung:
  app/schemas/       — Pydantic: validasi request & shape response
  app/core/          — database engine, security (JWT/bcrypt), exceptions
  app/dependencies.py — DI: auth token parsing, role guard
```

---

## Struktur Direktori

```
smart-access-api/
├── app/
│   ├── main.py                 # FastAPI app, lifespan, middleware, router mount
│   ├── config.py               # Settings dari .env via pydantic-settings
│   ├── dependencies.py         # DI: get_current_user, require_role, role helpers
│   │
│   ├── api/v1/
│   │   ├── router.py           # Gabungkan semua endpoint router
│   │   └── endpoints/          # Satu file per domain
│   │       ├── auth.py
│   │       ├── organizations.py
│   │       ├── merchants.py
│   │       ├── parents.py
│   │       ├── clients.py
│   │       ├── wallets.py
│   │       ├── transactions.py
│   │       ├── devices.py
│   │       ├── enrollment.py
│   │       ├── biometric.py
│   │       ├── products.py
│   │       ├── tickets.py
│   │       ├── notifications.py
│   │       ├── approvals.py
│   │       ├── dashboard.py
│   │       └── ws_device.py    # WebSocket ESP32
│   │
│   ├── services/               # Satu file per domain
│   │   ├── auth_service.py
│   │   ├── organization_service.py
│   │   ├── merchant_service.py
│   │   ├── parent_service.py
│   │   ├── client_service.py
│   │   ├── wallet_service.py
│   │   ├── transaction_service.py
│   │   ├── device_service.py
│   │   ├── enrollment_service.py
│   │   ├── biometric_engine.py     # InsightFace singleton
│   │   ├── kgiton_service.py       # KGiTON HTTP client
│   │   ├── notification_service.py
│   │   ├── approval_service.py
│   │   ├── audit_service.py
│   │   ├── dashboard_service.py
│   │   ├── product_service.py
│   │   └── ticket_service.py
│   │
│   ├── models/                 # SQLAlchemy ORM — satu file per tabel/domain
│   │   └── __init__.py         # Export semua model (wajib, untuk SQLAlchemy mapper)
│   │
│   ├── schemas/                # Pydantic — satu file per domain
│   │   # Konvensi nama: *Create, *Update, *Response
│   │
│   └── core/
│       ├── database.py         # engine, AsyncSessionLocal, Base, get_db
│       ├── security.py         # JWT encode/decode, bcrypt hash/verify
│       └── exceptions.py       # Custom HTTPException subclasses
│
├── database/
│   ├── schema.sql              # DDL lengkap — jalankan manual di Supabase / psql
│   ├── reset.sql               # Drop semua tabel & enum — dev/staging only
│   └── buckets.sql             # Supabase Storage buckets — jalankan di Supabase only
│
├── .env                        # Secrets — JANGAN commit ke git
├── .env.example                # Template tanpa nilai sensitif
├── requirements.txt
├── Dockerfile
└── docker-compose.yml          # local dev: postgres + api
```

---

## Pola Kode

### Endpoint → Service (wajib ikuti pola ini)

```python
# app/api/v1/endpoints/wallets.py
@router.post("/topup")
async def topup_wallet(
    data: TopUpRequest,
    db: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    service = WalletService(db)           # service di-instantiate per request
    result = await service.topup(...)     # semua logika ada di service
    return {"success": True, "data": result}
```

**Aturan endpoint:**

- Hanya validasi input (Pydantic sudah handle) dan auth check
- Instantiate service, panggil method, return response
- Tidak ada query database langsung di endpoint
- Tidak ada logika bisnis di endpoint

### Service Pattern

```python
# app/services/wallet_service.py
class WalletService:
    def __init__(self, db: AsyncSession):
        self.db = db                      # DB session di-inject, bukan diambil sendiri

    async def topup(self, client_id: str, amount: float) -> Wallet:
        # 1. Fetch entity yang dibutuhkan
        wallet = await self._get_wallet(client_id)
        # 2. Validasi bisnis
        if wallet.status != WalletStatus.ACTIVE:
            raise BadRequestException("Wallet is not active")
        # 3. Mutasi data
        wallet.balance += Decimal(str(amount))
        # 4. Commit
        await self.db.commit()
        await self.db.refresh(wallet)
        return wallet
```

**Aturan service:**

- Constructor selalu menerima `db: AsyncSession`
- Private helper method diawali `_` (contoh: `_get_wallet`, `_get_client`)
- Selalu raise exception dari `app.core.exceptions`, bukan `HTTPException` langsung
- `await self.db.commit()` hanya di service, tidak di endpoint
- Service boleh panggil service lain (inject db yang sama)

### Role Guard

```python
# Satu role
current_user = Depends(require_role("super_admin"))

# Beberapa role yang diizinkan
current_user = Depends(require_any_role("super_admin", "admin_hub", "admin_ops"))

# Akses terbuka (hanya perlu login)
current_user = Depends(get_current_user)

# Helper cek role di dalam fungsi
if is_super_admin(current_user):
    ...
```

### Exception

Selalu gunakan exception dari `app.core.exceptions`:

```python
from app.core.exceptions import (
    NotFoundException,           # 404
    BadRequestException,         # 400
    UnauthorizedException,       # 401
    ForbiddenException,          # 403
    ConflictException,           # 409
    InsufficientBalanceException, # 402
    BiometricVerificationFailed,  # 401
    DeviceBlockedException,       # 403
)
```

### Schema Naming Convention

```python
class WalletTopUpRequest(BaseModel):   # input/request
    ...

class WalletResponse(BaseModel):       # output/response
    model_config = {"from_attributes": True}  # wajib untuk ORM serialization
    ...
```

---

## Database

### Gunakan SQL, Bukan Alembic

Schema dikelola **manual** via SQL:

- `database/schema.sql` — buat tabel, jalankan sekali saat setup
- `database/reset.sql` — hapus semua, untuk dev/staging
- `database/buckets.sql` — Supabase Storage, jalankan di Supabase SQL Editor

**Alembic tidak digunakan.** Kalau ada perubahan tabel, update `schema.sql` langsung
lalu jalankan SQL-nya sendiri.

### Query Pattern

```python
# SELECT
result = await self.db.execute(select(Wallet).where(Wallet.client_id == client_id))
wallet = result.scalar_one_or_none()

# INSERT
obj = ModelClass(**data)
self.db.add(obj)
await self.db.commit()
await self.db.refresh(obj)

# UPDATE — langsung mutasi atribut, lalu commit
wallet.balance += amount
await self.db.commit()

# SELECT dengan pagination
result = await self.db.execute(
    select(Model).offset(skip).limit(limit)
)
items = result.scalars().all()
```

### ID Convention

Semua primary key adalah `VARCHAR(36)` UUID string, bukan integer.
Default: `gen_random_uuid()::text` di PostgreSQL, atau `str(uuid.uuid4())` di Python.

---

## Auth & Token

### User JWT Payload

```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "role": "admin_ops",
  "region_id": "...",
  "school_id": "...",
  "merchant_id": "..."
}
```

### Device JWT Payload

```json
{
  "sub": "device-uuid",
  "device_serial": "ESP32-XXXX",
  "type": "device"
}
```

Device token diidentifikasi dari field `"type": "device"`.
Gunakan `Depends(get_current_device)` untuk endpoint yang khusus perangkat.

---

## Role Hierarchy

| Role          | Akses                                                                |
| ------------- | -------------------------------------------------------------------- |
| `super_admin` | Full access — semua endpoint                                         |
| `admin_hub`   | Manage school, merchant, parent, client, device, transaksi, approval |
| `admin_ops`   | Operasional harian — enrollment, transaksi, device                   |
| `merchant`    | Hanya data & transaksi merchant sendiri                              |
| `parent`      | Hanya data & wallet anak sendiri                                     |

`super_admin` selalu lolos `require_role` dan `require_any_role`.

---

## External Integrations

### KGiTON API

Digunakan untuk **validasi lisensi perangkat ESP32**.

- `kgiton_service.validate_license(license_key)` — cek lisensi valid
- `kgiton_service.validate_license_ownership(license_key)` — cek kepemilikan
- `kgiton_service.get_license_info(license_key)` — info lengkap device

Auth: `X-API-Key` header menggunakan `KGITON_API_KEY` dari env.

### Biometric Engine (InsightFace)

`biometric_engine` adalah **singleton** yang di-init saat startup (background task).
Jangan instantiate ulang — selalu import dari `app.services.biometric_engine`:

```python
from app.services.biometric_engine import biometric_engine

embedding = biometric_engine.extract_face_embedding(image_bytes)
matched, score = biometric_engine.verify_face(stored_embedding_bytes, image_bytes)
```

Model: ArcFace `w600k_r50` (buffalo_l) — 512-dim L2-normalized embedding, cosine similarity.
Threshold pembayaran: `FACE_SIMILARITY_THRESHOLD` (default 0.55).

### WebSocket — ESP32 Device

Perangkat konek ke `/ws/device/{license_key}`.
`DeviceConnectionManager` di `ws_device.py` adalah singleton yang menyimpan koneksi aktif.

Flow:

1. Device konek → validasi `license_key` di tabel `devices`
2. Device kirim `{"event":"connected",...}` → update `last_heartbeat`
3. Server bisa push command: `enroll`, `verify`, `verify_templates`, `cancel`, `ping`
4. Device kirim hasil: `enroll_ok`, `verify_ok`, `verify_fail`

### Supabase Storage

Bucket `firmware` — file OTA untuk ESP32 (private, service_role only).
Bucket `biometric-assets` — face image enrollment (private, service_role only).

---

## Environment Variables

```
# Supabase — koneksi SDK (Storage, Auth)
SUPABASE_URL
SUPABASE_KEY
SUPABASE_SERVICE_ROLE_KEY

# Database — koneksi SQLAlchemy (PostgreSQL direct)
DATABASE_URL=postgresql+asyncpg://...

# JWT
JWT_SECRET_KEY
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEVICE_TOKEN_EXPIRE_DAYS=365

# Biometric
FACE_SIMILARITY_THRESHOLD=0.55
FINGERPRINT_MATCH_THRESHOLD=40
MAX_FACE_CANDIDATES=5
FACE_LIVENESS_ENABLED=true

# KGiTON
KGITON_API_URL
KGITON_API_KEY

# Storage
FIRMWARE_STORAGE_BUCKET=firmware
BIOMETRIC_STORAGE_BUCKET=biometric-assets
```

---

## Local Dev

```bash
# Jalankan dengan Docker (postgres + api)
docker-compose up

# Tanpa Docker — perlu PostgreSQL lokal
cp .env.example .env
# Edit DATABASE_URL ke localhost
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Setup database (pertama kali)
# Paste isi database/schema.sql ke psql atau Supabase SQL Editor
psql postgresql://postgres:postgres@localhost:5432/smartaccess -f database/schema.sql

# Reset database
psql postgresql://postgres:postgres@localhost:5432/smartaccess -f database/reset.sql
psql postgresql://postgres:postgres@localhost:5432/smartaccess -f database/schema.sql
```

API docs setelah server jalan:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Aturan Wajib

1. **Tidak ada `Base.metadata.create_all`** — schema dikelola manual via SQL
2. **Tidak ada logika bisnis di endpoint** — delegasikan ke service
3. **Tidak ada query DB di endpoint** — selalu melalui service
4. **`biometric_engine` adalah singleton** — jangan instantiate ulang
5. **Selalu gunakan custom exceptions** dari `app.core.exceptions`
6. **Schema response wajib `model_config = {"from_attributes": True}`** untuk serialisasi ORM
7. **Commit hanya di service** — bukan di endpoint, bukan di model
8. **Jangan simpan secret di kode** — semua dari `.env`
