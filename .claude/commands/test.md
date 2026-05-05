# Command: /test — Smart Access API

> Jalankan test suite dengan berbagai mode.
> Usage: `/test [scope] [options]`

---

## Usage

```
/test                            # Jalankan semua test
/test wallet                     # Test domain wallet saja
/test --coverage                 # Jalankan + tampilkan coverage report
/test --watch                    # Mode watch (re-run saat file berubah)
/test --create wallet            # Buat test baru untuk domain wallet
/test --fix                      # Coba auto-fix test failures yang jelas
```

---

## Quick Commands

```bash
# Semua test
pytest -v

# Dengan coverage
pytest --cov=app --cov-report=term-missing -v

# Test domain spesifik
pytest tests/ -k "wallet" -v
pytest tests/ -k "transaction or payment" -v

# Satu file
pytest tests/test_wallet_service.py -v

# Satu fungsi
pytest tests/test_wallet_service.py::test_topup_success -v

# Mode verbose dengan stop-on-first-fail
pytest -v --tb=short -x

# Coverage minimum (fail jika < 70%)
pytest --cov=app --cov-fail-under=70
```

---

## Test Environments

### Local (default)

```bash
source .venv/bin/activate

# Butuh local PostgreSQL atau Docker
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/smartaccess_test

pytest -v
```

### Docker (isolated)

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

---

## Coverage Report Interpretation

```
Name                                  Stmts   Miss  Cover
---------------------------------------------------------
app/services/wallet_service.py           45      4    91%   ← Bagus
app/services/transaction_service.py      78     23    71%   ← Acceptable
app/services/biometric_engine.py         34     18    47%   ← Perlu mock lebih
app/api/v1/endpoints/wallets.py          28      5    82%   ← Bagus
---------------------------------------------------------
TOTAL                                   412     89    78%
```

Target:

- Services: **≥ 85%**
- Endpoints: **≥ 70%**
- Overall: **≥ 75%**

---

## Membuat Test Baru

Ketika `/test --create [domain]` dijalankan, agent akan:

1. Baca implementasi service dan endpoint domain tersebut
2. Identifikasi semua public methods
3. Generate test untuk setiap method:
   - Happy path
   - Not found / empty response
   - Unauthorized / forbidden
   - Invalid input (bad request)
   - Business rule violation (misal: insufficient balance)
4. Generate fixtures yang diperlukan di `conftest.py`

---

## Failing Test Diagnosis

Ketika test gagal, agent akan:

1. Baca stack trace lengkap
2. Baca source file yang menyebabkan failure
3. Identifikasi apakah ini:
   - **Bug di source code** → propose fix di source
   - **Test yang salah** → propose fix di test
   - **Missing fixture** → tambah fixture ke conftest.py
   - **Environment issue** → instruksi setup

---

## Mock Patterns Standar

```python
# conftest.py — gunakan fixtures ini di semua test

@pytest.fixture
def mock_biometric(mocker):
    mocker.patch(
        "app.services.biometric_engine.biometric_engine.verify_face",
        return_value=(True, 0.87),
    )
    mocker.patch(
        "app.services.biometric_engine.biometric_engine.extract_face_embedding",
        return_value=b"x" * 512,
    )

@pytest.fixture
def mock_kgiton(mocker):
    mocker.patch(
        "app.services.kgiton_service.KGiTONService.validate_license",
        return_value={"valid": True, "license_key": "TEST-KEY-001"},
    )

@pytest.fixture
def mock_storage(mocker):
    mock = mocker.MagicMock()
    mock.upload.return_value = {"path": "test/file.bin"}
    mocker.patch("supabase.storage.from_", return_value=mock)
```
