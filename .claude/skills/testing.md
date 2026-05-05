# Skill: Testing — Smart Access API

Panduan menulis dan menjalankan test untuk Smart Access API.

---

## Stack Testing

- **pytest** + **pytest-asyncio** — async test support
- **httpx** + **AsyncClient** — HTTP client untuk endpoint test
- **pytest-mock** / **unittest.mock** — mocking external dependencies
- Database: PostgreSQL test (atau SQLite in-memory untuk unit test)

---

## Struktur Test

```
tests/
├── conftest.py          # Shared fixtures: test client, test DB, auth headers
├── unit/
│   ├── test_wallet_service.py
│   ├── test_auth_service.py
│   └── test_biometric_engine.py
└── integration/
    ├── test_wallets.py
    ├── test_transactions.py
    └── test_auth.py
```

---

## Menjalankan Test

```bash
# Semua test
pytest

# Test spesifik file
pytest tests/unit/test_wallet_service.py

# Test spesifik fungsi
pytest tests/unit/test_wallet_service.py::test_topup_success

# Dengan coverage
pytest --cov=app --cov-report=term-missing

# Verbose
pytest -v

# Stop di failure pertama
pytest -x

# Aktifkan venv dulu
source .venv/bin/activate
```

---

## conftest.py Template

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.security import create_access_token

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/smartaccess_test"

@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(engine):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
def super_admin_token():
    return create_access_token({"sub": "test-super-admin", "role": "super_admin", "email": "admin@test.com"})

@pytest.fixture
def admin_hub_token():
    return create_access_token({"sub": "test-admin-hub", "role": "admin_hub", "email": "hub@test.com"})

@pytest.fixture
def auth_headers(super_admin_token):
    return {"Authorization": f"Bearer {super_admin_token}"}
```

---

## Integration Test Template

```python
# tests/integration/test_wallets.py
import pytest
from decimal import Decimal

@pytest.mark.asyncio
async def test_topup_wallet_success(client, auth_headers, test_client_id):
    response = await client.post(
        f"/api/v1/wallets/{test_client_id}/topup",
        json={"amount": "50000"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert Decimal(str(data["data"]["balance"])) > 0

@pytest.mark.asyncio
async def test_topup_wallet_unauthorized(client, test_client_id):
    response = await client.post(
        f"/api/v1/wallets/{test_client_id}/topup",
        json={"amount": "50000"},
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_topup_wallet_not_found(client, auth_headers):
    response = await client.post(
        "/api/v1/wallets/non-existent-id/topup",
        json={"amount": "50000"},
        headers=auth_headers,
    )
    assert response.status_code == 404
```

---

## Unit Test Template (Service)

```python
# tests/unit/test_wallet_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal

from app.services.wallet_service import WalletService
from app.core.exceptions import NotFoundException, BadRequestException

@pytest.mark.asyncio
async def test_topup_success():
    mock_db = AsyncMock()
    mock_wallet = MagicMock(
        client_id="client-123",
        balance=Decimal("100000"),
        status="active",
    )

    service = WalletService(mock_db)
    service._get_wallet_by_client = AsyncMock(return_value=mock_wallet)

    result = await service.topup("client-123", Decimal("50000"))

    assert mock_wallet.balance == Decimal("150000")
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_topup_inactive_wallet():
    mock_db = AsyncMock()
    mock_wallet = MagicMock(status="suspended")

    service = WalletService(mock_db)
    service._get_wallet_by_client = AsyncMock(return_value=mock_wallet)

    with pytest.raises(BadRequestException, match="not active"):
        await service.topup("client-123", Decimal("50000"))

@pytest.mark.asyncio
async def test_topup_wallet_not_found():
    mock_db = AsyncMock()
    service = WalletService(mock_db)
    service._get_wallet_by_client = AsyncMock(side_effect=NotFoundException("not found"))

    with pytest.raises(NotFoundException):
        await service.topup("non-existent", Decimal("50000"))
```

---

## Mocking External Services

```python
# Mock KGiTON API
@patch("app.services.kgiton_service.KGiTONService.validate_license")
async def test_device_registration(mock_validate, client, auth_headers):
    mock_validate.return_value = {"valid": True, "device_type": "ESP32"}
    response = await client.post("/api/v1/devices/register", ...)

# Mock biometric engine
@patch("app.services.biometric_engine.biometric_engine.extract_face_embedding")
async def test_face_enrollment(mock_extract, client, auth_headers):
    mock_extract.return_value = b"\x00" * 2048  # 512-dim float32 embedding
```

---

## Coverage Target

| Layer     | Target            |
| --------- | ----------------- |
| Services  | ≥ 85%             |
| Endpoints | ≥ 70%             |
| Core      | ≥ 90%             |
| Models    | N/A (schema only) |

---

## Requirements Dev

```bash
pip install pytest pytest-asyncio httpx pytest-mock pytest-cov
# atau
pip install -r requirements-dev.txt
```

---

## pytest.ini / pyproject.toml

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```
