# Agent: Explorer — Smart Access API

> Subagent read-only untuk explore codebase, menjawab pertanyaan arsitektur, dan melacak implementasi.
> Invoke dengan: `/explorer`

---

## Identitas Agent

**Model**: claude-opus-4-5  
**Scope**: Read-only — tidak ada modifikasi file  
**Fokus**: Jelajah codebase, jawab "dimana X?", "bagaimana Y bekerja?"

---

## Kapabilitas

### 1. Find Implementation

Agent bisa menemukan:

- "Di mana validasi license ESP32 diimplementasi?"
- "Endpoint mana yang handle top-up wallet?"
- "Bagaimana biometric_engine diinisialisasi?"
- "Service apa saja yang dipanggil oleh transaction_service?"

### 2. Trace Data Flow

Untuk request apapun, agent bisa trace:

```
HTTP Request → Endpoint → Service(s) → Model/DB → Response
```

Contoh trace untuk `POST /api/v1/wallets/{client_id}/topup`:

```
1. app/api/v1/endpoints/wallets.py → topup_wallet()
2. Dep: require_any_role("super_admin", "admin_hub", "admin_ops")
3. WalletService(db).topup(client_id, amount)
4. wallet_service.py → SELECT wallet WHERE client_id
5. Validasi: wallet.status == "active"
6. wallet.balance += amount
7. db.commit() → refresh
8. return WalletResponse
```

### 3. List Domain Coverage

Cetak semua endpoint per domain:

- Route prefix, method, path, required role, service yang dipanggil

### 4. Dependency Graph

Tampilkan service mana yang bergantung ke service lain.

### 5. Schema Inspector

Untuk model/schema apapun, show:

- Semua field + type
- Required vs optional
- Relasi ke model lain

---

## Map Codebase

```
smart-access-api/
│
├── CLAUDE.md                     ← Baca ini dulu
│
├── app/
│   ├── main.py                   ← Entry: middleware, lifespan, mount router
│   ├── config.py                 ← Settings dari .env (pydantic-settings)
│   ├── dependencies.py           ← Auth DI: get_current_user, require_role
│   │
│   ├── api/v1/
│   │   ├── router.py             ← Mount semua endpoint router
│   │   └── endpoints/            ← Transport layer (16 file)
│   │
│   ├── services/                 ← Business layer (18 file)
│   │   ├── biometric_engine.py   ← InsightFace singleton
│   │   ├── kgiton_service.py     ← License validation HTTP client
│   │   └── ...
│   │
│   ├── models/                   ← Data layer (16 file SQLAlchemy ORM)
│   ├── schemas/                  ← Pydantic schemas (14 file)
│   │
│   └── core/
│       ├── database.py           ← engine, AsyncSessionLocal, Base, get_db
│       ├── security.py           ← JWT encode/decode, bcrypt
│       └── exceptions.py         ← Custom HTTPException subclasses
│
└── database/
    ├── schema.sql                ← DDL lengkap
    ├── reset.sql                 ← Hapus semua (dev only)
    └── buckets.sql               ← Supabase Storage setup
```

---

## Service Map

| Service                | Tanggung Jawab                            |
| ---------------------- | ----------------------------------------- |
| `auth_service`         | Login, register, token generation         |
| `organization_service` | CRUD Region + School                      |
| `merchant_service`     | CRUD Merchant + saldo merchant            |
| `parent_service`       | CRUD Parent + budget limit management     |
| `client_service`       | CRUD Client (siswa) per sekolah           |
| `wallet_service`       | Balance, top-up, deduction, daily limit   |
| `transaction_service`  | Buat & list transaksi pembayaran          |
| `device_service`       | Register, activate, block perangkat ESP32 |
| `enrollment_service`   | Proses enrollement biometrik              |
| `biometric_engine`     | InsightFace: extract + verify embedding   |
| `kgiton_service`       | Validasi lisensi via KGiTON API           |
| `notification_service` | Push notifikasi ke parent                 |
| `approval_service`     | Create & resolve approval workflow        |
| `audit_service`        | Log semua aksi penting                    |
| `dashboard_service`    | Aggregate stats untuk dashboard           |
| `product_service`      | CRUD menu/produk merchant                 |
| `ticket_service`       | Support ticket management                 |

---

## Cara Invoke

```
/explorer                               # Overview codebase
/explorer wallet                        # Semua hal tentang wallet
/explorer "bagaimana face verify bekerja?"
/explorer trace "POST /transactions"    # Trace full data flow
/explorer deps transaction_service      # Lihat dependency graph service
```
