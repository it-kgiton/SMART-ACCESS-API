# Command: /review — Smart Access API

> Jalankan code review terhadap perubahan terbaru atau file spesifik.
> Usage: `/review [target]`

---

## Usage

```
/review                          # Review semua perubahan sejak commit terakhir
/review app/services/wallet_service.py   # Review file spesifik
/review wallet                   # Review semua file domain wallet
/review --strict                 # Review mode ketat (include style issues)
/review --security               # Focus ke security vulnerabilities
```

---

## Scope Review

Agent akan menjalankan review otomatis terhadap:

### Architecture Violations

```bash
# Deteksi query DB di endpoint (violation)
grep -rn "await db.execute\|scalar_one_or_none\|db.add\|db.commit" app/api/ --include="*.py"

# Deteksi bisnis logic di endpoint
grep -rn "if.*role\|if.*status\|if.*balance" app/api/v1/endpoints/ --include="*.py"

# Deteksi HTTPException langsung (harus custom exception)
grep -rn "raise HTTPException" app/services/ --include="*.py"
grep -rn "raise HTTPException" app/api/ --include="*.py"
```

### Security Scan

```bash
# Cek hardcoded secrets
grep -rn "secret\|password\|api_key\s*=" app/ --include="*.py" | grep -v "test\|env\|config"

# Cek missing auth dependency
grep -rn "@router\." app/api/v1/endpoints/ --include="*.py" | grep -v "require_role\|require_any_role\|get_current_user"

# Response schema bocorkan field sensitif
grep -rn "password\|token\|secret" app/schemas/ --include="*.py"
```

### Schema Validation

```bash
# Cek Response schema missing from_attributes
grep -rn "class.*Response" app/schemas/ --include="*.py" -A 5 | grep -v "from_attributes"
```

---

## Checklist Review Manual

Agent akan verify secara manual:

#### Layer Compliance

- [ ] Endpoint hanya validasi + auth + delegate ke service
- [ ] Tidak ada `db.execute` di file `app/api/`
- [ ] Semua `db.commit()` ada di service layer saja

#### Exception Handling

- [ ] Custom exceptions dari `app.core.exceptions`
- [ ] Proper HTTP status code mapping
- [ ] Error response tidak bocorkan internal info

#### Auth & Permissions

- [ ] Setiap endpoint punya auth dependency
- [ ] Role check sesuai dengan permission matrix
- [ ] Device endpoint pakai `get_current_device`

#### Schema

- [ ] `*Response` punya `model_config = {"from_attributes": True}`
- [ ] UUID field → `str`, bukan `UUID` type
- [ ] `Optional[X]` untuk nullable fields

#### Database

- [ ] Primary key UUID string
- [ ] Relationship pakai `lazy="selectin"`
- [ ] Tidak ada hardcoded SQL string (gunakan SQLAlchemy expressions)

---

## Output Format

```
## Code Review Report
**Target:** app/services/wallet_service.py
**Date:** 2026-05-05

### Summary
...

### Issues Found

| Severity | Line | Issue | Fix |
|----------|------|-------|-----|
| 🔴 Critical | 45 | ... | ... |
| 🟡 Warning | 78 | ... | ... |
| 🔵 Info | 92 | ... | ... |

### Security Notes
...

### Verdict
✅ Approved / ⚠️ Needs Fix / ❌ Rejected
```
