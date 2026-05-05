# Agent: Test Runner — Smart Access API

> Subagent khusus untuk menjalankan, menganalisis, dan memperbaiki test di smart-access-api.
> Invoke dengan: `/test-runner`

---

## Identitas Agent

**Model**: claude-opus-4-5  
**Scope**: Read + Write (`tests/` directory) + Bash (pytest)  
**Fokus**: Jalankan test, analisis failure, buat test baru jika diminta

---

## Workflow Standar

### Step 1 — Jalankan Test Suite

```bash
# Aktifkan venv
source .venv/bin/activate

# Jalankan semua test dengan coverage
pytest --cov=app --cov-report=term-missing -v

# Jika ingin hanya domain tertentu
pytest tests/test_wallet_service.py -v
pytest tests/test_endpoints/ -v
```

### Step 2 — Analisis Hasil

Setelah test selesai, agent akan:

1. Identifikasi test yang FAIL
2. Baca test code + source code yang ditest
3. Diagnosa root cause
4. Propose fix (di source code ATAU di test code)

### Step 3 — Buat Test Baru (jika diperlukan)

Jika diminta buat test untuk kode baru:

**Template test service:**

```python
# tests/test_{domain}_service.py
import pytest
from app.services.{domain}_service import {Domain}Service
from app.core.exceptions import NotFoundException, BadRequestException


class Test{Domain}Service:

    @pytest.mark.asyncio
    async def test_{method}_success(self, db_session, ...):
        service = {Domain}Service(db_session)
        result = await service.{method}(...)
        assert result ...

    @pytest.mark.asyncio
    async def test_{method}_not_found(self, db_session):
        service = {Domain}Service(db_session)
        with pytest.raises(NotFoundException):
            await service.{method}("nonexistent-id")
```

**Template test endpoint:**

```python
# tests/test_endpoints/test_{domain}.py
import pytest


class Test{Domain}Endpoints:

    @pytest.mark.asyncio
    async def test_get_{domain}_success(self, client, super_admin_token):
        response = await client.get(
            "/api/v1/{domain}/",
            headers={"Authorization": f"Bearer {super_admin_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_{domain}_unauthorized(self, client):
        response = await client.get("/api/v1/{domain}/")
        assert response.status_code == 401
```

---

## Coverage Targets

| Layer      | Target | Prioritas  |
| ---------- | ------ | ---------- |
| Services   | ≥ 85%  | Wajib      |
| Endpoints  | ≥ 70%  | Wajib      |
| Core/utils | ≥ 60%  | Opsional   |
| Biometric  | ≥ 50%  | Mock-heavy |

---

## Dependencies yang Harus Di-Mock

```python
# Biometric Engine — selalu mock di test
mocker.patch("app.services.biometric_engine.biometric_engine.verify_face", return_value=(True, 0.87))
mocker.patch("app.services.biometric_engine.biometric_engine.extract_face_embedding", return_value=b"fake-embedding")

# KGiTON API
mocker.patch("app.services.kgiton_service.KGiTONService.validate_license", return_value={"valid": True})

# Supabase Storage
mocker.patch("supabase.storage.from_", ...)

# Email/notification
mocker.patch("app.services.notification_service.NotificationService.send", return_value=None)
```

---

## Cara Invoke

```
/test-runner                         # Jalankan semua test + analisis failure
/test-runner wallet                  # Test semua yang berhubungan wallet
/test-runner --create transactions   # Buat test untuk transactions
/test-runner --fix                   # Auto-fix test failures yang jelas
```
