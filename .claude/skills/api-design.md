# Skill: API Design — Smart Access Backend

Panduan desain dan implementasi endpoint FastAPI untuk Smart Access.

---

## Struktur Wajib: Endpoint → Service → Model

Semua kode harus mengikuti 3-layer architecture ini **tanpa pengecualian**:

```
Router (app/api/v1/endpoints/*.py)
  └─ Service (app/services/*_service.py)
       └─ SQLAlchemy Model (app/models/*.py)
```

---

## Membuat Endpoint Baru

### 1. Buat schema di `app/schemas/`

```python
# app/schemas/wallet.py
from pydantic import BaseModel
from decimal import Decimal

class WalletTopUpRequest(BaseModel):
    amount: Decimal
    note: str | None = None

class WalletResponse(BaseModel):
    id: str
    client_id: str
    balance: Decimal
    status: str

    model_config = {"from_attributes": True}  # WAJIB untuk ORM serialization
```

**Naming convention:**

- Request body: `*Request` atau `*Create` / `*Update`
- Response: `*Response`
- `model_config = {"from_attributes": True}` wajib di semua `*Response`

---

### 2. Buat/update service di `app/services/`

```python
# app/services/wallet_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal

from app.models.wallet import Wallet
from app.core.exceptions import NotFoundException, BadRequestException

class WalletService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def topup(self, client_id: str, amount: Decimal) -> Wallet:
        wallet = await self._get_wallet_by_client(client_id)
        if wallet.status != "active":
            raise BadRequestException("Wallet is not active")
        wallet.balance += amount
        await self.db.commit()
        await self.db.refresh(wallet)
        return wallet

    async def _get_wallet_by_client(self, client_id: str) -> Wallet:
        result = await self.db.execute(
            select(Wallet).where(Wallet.client_id == client_id)
        )
        wallet = result.scalar_one_or_none()
        if not wallet:
            raise NotFoundException("Wallet not found")
        return wallet
```

**Aturan service:**

- Constructor selalu `__init__(self, db: AsyncSession)`
- Private helper diawali `_`
- `await self.db.commit()` hanya di service
- Raise dari `app.core.exceptions`, bukan `HTTPException` langsung
- Boleh panggil service lain dengan `db` yang sama

---

### 3. Buat/update endpoint di `app/api/v1/endpoints/`

```python
# app/api/v1/endpoints/wallets.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import require_role, require_any_role, get_current_user
from app.schemas.wallet import WalletTopUpRequest, WalletResponse
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/wallets", tags=["wallets"])

@router.post("/{client_id}/topup", response_model=WalletResponse)
async def topup_wallet(
    client_id: str,
    data: WalletTopUpRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "parent")),
):
    service = WalletService(db)
    result = await service.topup(client_id, data.amount)
    return result
```

**Aturan endpoint:**

- Instantiate service per request (bukan singleton)
- Hanya handle: auth guard, parse input, panggil service, return response
- Tidak ada logika bisnis, tidak ada query DB langsung
- Selalu gunakan `response_model=` untuk type safety

---

### 4. Daftarkan ke router di `app/api/v1/router.py`

```python
from app.api.v1.endpoints import wallets
api_router.include_router(wallets.router)
```

---

## Role Guard Pattern

```python
# Satu role saja
current_user = Depends(require_role("super_admin"))

# Multiple role diizinkan
current_user = Depends(require_any_role("super_admin", "admin_hub", "admin_ops"))

# Hanya perlu login (semua role)
current_user = Depends(get_current_user)

# Cek role di dalam body fungsi
from app.dependencies import is_super_admin, is_admin_hub

if is_super_admin(current_user):
    # bypass filter
```

---

## Response Pattern

```python
# Success dengan data
return {"success": True, "data": result}

# Success dengan list + pagination
return {
    "success": True,
    "data": items,
    "total": total,
    "skip": skip,
    "limit": limit,
}

# Success tanpa data
return {"success": True, "message": "Deleted successfully"}
```

---

## Exception Pattern

```python
from app.core.exceptions import (
    NotFoundException,            # 404
    BadRequestException,          # 400
    UnauthorizedException,        # 401
    ForbiddenException,           # 403
    ConflictException,            # 409
    InsufficientBalanceException, # 402
    BiometricVerificationFailed,  # 401
    DeviceBlockedException,       # 403
)

# Penggunaan
raise NotFoundException(f"Client {client_id} not found")
raise BadRequestException("Insufficient balance")
raise ConflictException("Email already registered")
```

---

## Pagination Pattern

```python
@router.get("/", response_model=dict)
async def list_items(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ItemService(db)
    items, total = await service.list_items(skip=skip, limit=limit)
    return {"success": True, "data": items, "total": total, "skip": skip, "limit": limit}
```

---

## WebSocket Pattern (ESP32)

```python
@router.websocket("/ws/device/{license_key}")
async def websocket_device(
    websocket: WebSocket,
    license_key: str,
    db: AsyncSession = Depends(get_db),
):
    await manager.connect(websocket, license_key)
    try:
        while True:
            data = await websocket.receive_json()
            await handle_device_event(data, license_key, db)
    except WebSocketDisconnect:
        manager.disconnect(license_key)
```

---

## Checklist Endpoint Baru

- [ ] Schema Request dan Response sudah dibuat
- [ ] `model_config = {"from_attributes": True}` ada di Response schema
- [ ] Service method sudah dibuat dan ditest
- [ ] Endpoint hanya memanggil service (no direct DB)
- [ ] Role guard sudah dipasang
- [ ] Router sudah di-include di `router.py`
- [ ] Tidak ada hardcoded secret
