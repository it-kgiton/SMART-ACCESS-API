# Skill: Database — Smart Access API

Panduan pengelolaan database PostgreSQL dengan SQLAlchemy async untuk Smart Access.

---

## Prinsip Utama

1. **Schema dikelola manual via SQL** — tidak ada Alembic, tidak ada `create_all`
2. **SQLAlchemy hanya untuk CRUD** — bukan untuk mendefinisikan atau migrasi schema
3. **Async everywhere** — semua query harus `await`
4. **Commit hanya di service** — tidak di endpoint, tidak di model

---

## File Database

```
database/
├── schema.sql   # DDL lengkap — jalankan sekali saat setup
├── reset.sql    # DROP semua tabel & enum — dev/staging only
├── buckets.sql  # Supabase Storage buckets — jalankan di Supabase
└── seed.sql     # Data awal / test data
```

**Aturan:**

- Setiap perubahan tabel → update `schema.sql` langsung
- Jalankan SQL manual di psql atau Supabase SQL Editor
- `reset.sql` DILARANG di production

---

## Query Patterns

### SELECT — satu baris

```python
result = await self.db.execute(
    select(Wallet).where(Wallet.client_id == client_id)
)
wallet = result.scalar_one_or_none()
if not wallet:
    raise NotFoundException("Wallet not found")
```

### SELECT — list dengan filter

```python
stmt = select(Transaction).where(
    Transaction.school_id == school_id,
    Transaction.status == "completed"
).order_by(Transaction.created_at.desc())

result = await self.db.execute(stmt)
transactions = result.scalars().all()
```

### SELECT — pagination

```python
stmt = (
    select(Client)
    .where(Client.school_id == school_id)
    .offset(skip)
    .limit(limit)
    .order_by(Client.created_at.desc())
)
result = await self.db.execute(stmt)
items = result.scalars().all()

# Count total
count_stmt = select(func.count()).select_from(Client).where(Client.school_id == school_id)
total = await self.db.scalar(count_stmt)
```

### SELECT — JOIN

```python
stmt = (
    select(Transaction, Merchant.business_name)
    .join(Merchant, Transaction.merchant_id == Merchant.id)
    .where(Transaction.client_id == client_id)
)
result = await self.db.execute(stmt)
rows = result.all()
```

### INSERT

```python
new_wallet = Wallet(
    id=str(uuid.uuid4()),
    client_id=client_id,
    balance=Decimal("0"),
    status="active",
)
self.db.add(new_wallet)
await self.db.commit()
await self.db.refresh(new_wallet)
return new_wallet
```

### UPDATE — mutasi langsung

```python
wallet = await self._get_wallet(client_id)
wallet.balance += amount
wallet.updated_at = datetime.utcnow()
await self.db.commit()
await self.db.refresh(wallet)
return wallet
```

### DELETE — soft delete preferred

```python
# Soft delete (preferred)
entity.status = "suspended"
await self.db.commit()

# Hard delete (hanya jika benar-benar perlu)
await self.db.delete(entity)
await self.db.commit()
```

### Bulk INSERT

```python
items = [Model(id=str(uuid.uuid4()), **item_data) for item_data in data_list]
self.db.add_all(items)
await self.db.commit()
```

---

## ID Convention

```python
import uuid

# Selalu UUID string, bukan integer
id = str(uuid.uuid4())

# Di model SQLAlchemy
id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
```

---

## Timestamp Convention

```python
from datetime import datetime

created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## Enum Pattern

Enum didefinisikan di SQL (`schema.sql`), bukan di Python:

```sql
-- Di schema.sql
CREATE TYPE wallet_status AS ENUM ('active', 'suspended', 'frozen');
```

Di Python, gunakan string literal:

```python
wallet.status = "active"   # bukan WalletStatus.ACTIVE
if wallet.status == "active":
```

---

## Session Management

```python
# Di database.py — jangan diubah
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

Session di-inject via `Depends(get_db)` ke endpoint, lalu diteruskan ke service constructor. Jangan buat session baru di dalam service.

---

## Model Convention

```python
# app/models/wallet.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Numeric, DateTime
from app.core.database import Base

class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(36), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="IDR")
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Aturan model:**

- Tidak ada logika bisnis di model — hanya definisi kolom
- Tidak ada method yang memanipulasi data
- Export semua model dari `app/models/__init__.py`

---

## Error Handling Database

```python
from sqlalchemy.exc import IntegrityError

try:
    self.db.add(new_entity)
    await self.db.commit()
except IntegrityError as e:
    await self.db.rollback()
    if "unique" in str(e.orig).lower():
        raise ConflictException("Resource already exists")
    raise BadRequestException("Database constraint violated")
```

---

## Setup Database Lokal

```bash
# Jalankan schema (pertama kali)
psql postgresql://postgres:postgres@localhost:5432/smartaccess -f database/schema.sql

# Reset (dev only)
psql postgresql://postgres:postgres@localhost:5432/smartaccess -f database/reset.sql
psql postgresql://postgres:postgres@localhost:5432/smartaccess -f database/schema.sql

# Tambah data seed
psql postgresql://postgres:postgres@localhost:5432/smartaccess -f database/seed.sql
```

---

## Anti-Pattern — JANGAN LAKUKAN

```python
# ❌ JANGAN — create_all
Base.metadata.create_all(engine)

# ❌ JANGAN — query langsung di endpoint
@router.get("/")
async def get_data(db = Depends(get_db)):
    result = await db.execute(select(Model))  # langsung query di endpoint

# ❌ JANGAN — commit di endpoint
await db.commit()  # commit di endpoint

# ❌ JANGAN — buat session baru di service
async with AsyncSessionLocal() as session:  # di dalam service
```
